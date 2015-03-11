#!/usr/bin/python
# -*- coding: utf-8 -*-

import smtplib
import os
import re
import sys
import imaplib
import email
import tempfile
import shutil
import datetime
import quopri
import base64
import hashlib

import quopri
import base64
import hashlib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

class Mailer:
	"""Класс по работе с электронной почтой"""
	
	addrTo = []
	'''Список адресатов'''
	
	addrFrom = False
	login = False
	subject = 'Без темы'
	subjectTmpl = '{subject} {part}/{total}'
	text = ''
	attach = []
	smtpHost = False
	smtpPort = 25
	useSSL = False
	useTLS = False
	smtpPassword = False
	verbose = False
	timeout = 30
	split = False
	imapHost = False
	imapPort = 143
	#md5 = False
	imapHost = False
	imapPort = 143
	imapPassword = False
	imapSSL = False
	
	def timeString( self, d ):
		"""Возвращает текстовое представление времени
		d - Дата"""
		timeStr = "{year}-{month:#02}-{day:#02}_{hour:#02}-{minute:#02}-{second:#02}".format(
			year=d.year,
			month=d.month,
			day=d.day,
			hour=d.hour,
			minute=d.minute,
			second=d.second )
		return timeStr

	def log(self,text):
		'''Лог - Выводил текст (text)'''
		if self.verbose:
			print text
		
	def serr(self,text):
		"""Лог - ошибка состояния объекта, text - описание"""
		print 'Ошибка состояния объекта = '+text

	def exception(self,ex):
		"""Лог - исключительная ситуация, ex - описание"""
		print 'Ошибка почты {err}'.format( err=ex )

	def attachFile(self,msg,fileName):
		"""Присоединяет файл (fileName) к сообщению (msg)"""
		part = MIMEBase('application', 'octet-stream')
		part.set_payload(open(fileName, 'rb').read())
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(fileName))
		msg.attach(part)
		return True

	def splitFile(self,fileName):
		"""Разделяет файл (fileName) на куски (формат 7z) во временную директорию.
		Возвращает путь временной директории, после использования директории следует самостоятельно ее удалить.
		Если не получилось разделить (ошибка), то вернет False"""
		tmpDir = tempfile.mkdtemp('mailer')
		verb = ''
		if not self.verbose:
			verb = '1>/dev/null'
		cmd = "7z a -v{volsize} '{arcfile}' '{sendfile}' {verbose}".format(
			volsize=self.split,
			arcfile='{tmpdir}/{basename}.7z'.format(
				tmpdir=tmpDir,
				basename=os.path.basename(fileName),
				),
			sendfile=fileName,
			verbose=verb
			)
		cmd = cmd.replace( "(", "\(" ).replace( ")","\)" )
		result = os.system( cmd )
		if result==0:
			return tmpDir
		else:
			return False

	def sendParts(self,tmpDir,srcFilePath):
		"""Отсылает файлы указанной директории (tmpDir) отдельными письмами.
		Возвращает кол-вот отправленых писем."""
		def mf( msg ):
			return lambda: msg.makeMessage()
		succCount = 0
		messages = []
		for dirpath, dirnames, filenames in os.walk(tmpDir):
			count = len(filenames)
			idx = 0
			for filename in filenames:
				idx = idx + 1
				filepath = os.path.join( dirpath,filename )
				date_ = datetime.datetime.now()
				
				tmpl = self.subjectTmpl
				subject = tmpl.format(
					subject=self.subject, 
					part=idx, 
					total=count,
					date=self.timeString(date_),
					filepath=srcFilePath,
					filename=os.path.basename(srcFilePath),
					attachpath=filepath,
					attachname=os.path.basename(filepath))
					
				m = Mailer()
				m.addrTo = self.addrTo
				m.addrFrom = self.addrFrom
				m.subject = subject
				m.text = self.text
				m.attach = filepath
				m.smtpHost = self.smtpHost
				m.smtpPort = self.smtpPort
				m.useSSL = self.useSSL
				m.useTLS = self.useTLS
				m.smtpPassword = self.smtpPassword
				m.verbose = self.verbose
				m.timeout = self.timeout
				m.split = False

				#msg = m.makeMessage()
				msg = mf( m )
				if not isinstance(msg,bool):
					messages.append( msg )

		succ = self.sendMailMessage( messages )
		if succ:
			return len(messages)
		return 0

	def send(self):
		"""Отправляет письмо на почту.
		Если указано разделять вложения на части - то отправит несколько писем.
		Возвращает кол-во отправленых писем."""
		if isinstance(self.split,str):
			count = 0
			if isinstance(self.attach,(list,tuple)):
				if len(self.attach)>0:
					for attc in self.attach:
						if os.path.isfile( attc ):
							tmpDir = self.splitFile( attc )
							if os.path.isdir(tmpDir):
								count = count + self.sendParts(tmpDir,attc)
								shutil.rmtree(tmpDir)
					pass
			elif os.path.isfile( self.attach ):
				tmpDir = self.splitFile( self.attach )
				if os.path.isdir(tmpDir):
					count = count + self.sendParts(tmpDir,self.attach)
					shutil.rmtree(tmpDir)
			self.log( 'Отправлено {counter} писем'.format(counter=count) )
			return count>0
		return self.sendMail()

	def sendMailMessage(self,msg):
		"""Отправляет сообщения (msg) на почту.
		msg - либо список сообщений (объекты MIMEMultipart / набор функций(без аргументов) - возвращающие MIMEMultipart)
		    / либо отдельный объект MIMEMultipart.
		Возвращает True - успешно / False - Ошибка отправки.
		"""
		try:
			if self.useSSL:
				self.log( 'Соединение по SSL, хост={host} порт={port}'.format( host=self.smtpHost,port=self.smtpPort ) )
				mailServer = smtplib.SMTP_SSL( self.smtpHost, self.smtpPort, timeout=float(self.timeout) )
			else:
				self.log( 'Соединение, хост={host} порт={port}'.format( host=self.smtpHost,port=self.smtpPort ) )
				mailServer = smtplib.SMTP( self.smtpHost, self.smtpPort, timeout=float(self.timeout) )

			self.log( 'Команда EHLO' )
			mailServer.ehlo()

			if self.useTLS:
				self.log( 'Команда STARTTLS' )
				mailServer.starttls()

			_login_ = self.login
			if _login_ == False:
				_login_ = self.addrFrom

			self.log( 'Команда LOGIN, логин={login}'.format(login=_login_) )
			mailServer.login( _login_, self.smtpPassword )

			if isinstance(msg,(tuple,list)):
				for message in msg:
					m = message
					if hasattr(message, '__call__'):
						m = message()
					if not isinstance(m,bool):
						self.log( 'Отправка письма, адресат:{to} тема:{subj}'.format(
							to=m['To'],
							subj=m['Subject']
							) )
						mailServer.sendmail(self.addrFrom, m['To'], m.as_string())
			else:
				self.log( 'Отправка письма, адресат:{to} тема:{subj}'.format(
					to=msg['To'],
					subj=msg['Subject']
					) )
				mailServer.sendmail(self.addrFrom, msg['To'], msg.as_string())

			self.log( 'Закрытие соединения' )
			mailServer.close()

			self.log( 'Письмо отправлено' )

			return True
		except smtplib.SMTPException as e:
			print 'Ошибка почты {err}'.format( err=e )
			return False

	def makeMessage(self):
		"""Создает сообщение - объект MIMEMultipart и возвращает его."""
		msg = MIMEMultipart()

		if not isinstance(self.addrFrom,str):
			self.serr( 'Не указан отправитель - addrFrom не строка' )
			return False
		msg['From'] = self.addrFrom

		if isinstance(self.addrTo,(str,unicode)):
			msg['To'] = self.addrTo
		elif isinstance(self.addrTo,(list,tuple)):
			if len(self.addrTo)==0:
				self.serr( 'Не указан адресат - len(addrTo) = 0' )
				return False
			msg['To'] = ', '.join( self.addrTo )
		else:
			self.serr( 'addrTo не строка / список' )
			return False

		if isinstance(self.subject,(str,unicode)):
			msg['Subject'] = self.subject
		else:
			self.serr( 'Не указана тема - subject не строка' )
			return False

		if isinstance(self.text,(str,unicode)):
			msg.attach( MIMEText(self.text) )
		else:
			self.serr( 'text не строка' )
			return False

		if isinstance(self.attach,(list,tuple)):
			for attc in self.attach:
				self.attachFile( msg, attc )
		elif os.path.exists( self.attach ):
			self.attachFile( msg, self.attach )
			
		return msg

	def sendMail(self):
		"""Отправляет отдельное письмо.
		Если сообщение создано удачно и письмо отправлено вернет - True.
		Если возникли проблемы - то вернет False."""
		msg = self.makeMessage()
		if isinstance(msg,bool):
			return msg
		return self.sendMailMessage( msg )

	def imapWork(self,workFun):
		"""Соединяется с сервером imap, производит login и передает управление функции workFun( m )
		m - Объект imaplib.IMAP4. После завершению работы workFun завершает работу с imap."""
		if not self.imapHost:
			self.serr( 'Не указан параметр imap (imapHost)' )
			return False
		if not self.imapPort:
			self.serr( 'Не указан параметр imap (imapPort)' )
			return False
		if not self.imapPassword:
			self.serr( 'Не указан параметр password (imapPassword)' )
			return False
		if not self.addrFrom:
			self.serr( 'Не указан параметр from (addrFrom)' )
			return False
			
		mail = None
		if self.imapSSL:
			self.log( 'Соединение с imap по ssl {host}:{port}'.format(host=self.imapHost,port=self.imapPort) )
			mail = imaplib.IMAP4_SSL(self.imapHost,self.imapPort)
		else:
			self.log( 'Соединение с imap {host}:{port}'.format(host=self.imapHost,port=self.imapPort) )
			mail = imaplib.IMAP4(self.imapHost,self.imapPort)

		self.log( 'Команда LOGIN, логин={login}'.format(login=self.addrFrom) )
		mail.login(self.addrFrom,self.imapPassword)
			
		workFun( mail )

		self.log( 'Завершение работы с imap' )
		mail.logout()
		return True

	def decode_m_utf7(self,s):
		r = []
		decode = []
		for c in s:
			if c == '&' and not decode:
				decode.append('&')
			elif c == '-' and decode:
				if len(decode) == 1:
					r.append('&')
				else:
					r.append(self.modified_unbase64(''.join(decode[1:])))
				decode = []
			elif decode:
				decode.append(c)
			else:
				r.append(c)
		if decode:
			r.append(self.modified_unbase64(''.join(decode[1:])))
		out = ''.join(r)

		if not isinstance(out, unicode):
			out = unicode(out, 'latin-1')
		return out

	def modified_base64(self,s):
		s_utf7 = s.encode('utf-7')
		return s_utf7[1:-1].replace('/', ',')
		
	def modified_unbase64(self,s):
		s_utf7 = '+' + s.replace(',', '/') + '-'
		return s_utf7.decode('utf-7')

	def encode_m_utf7(s):
		if isinstance(s, str) and sum(n for n in (ord(c) for c in s) if n > 127):
			raise FolderNameError("%r contains characters not valid in a str folder name. "
								"Convert to unicode first?" % s)
		r = []
		_in = []
		for c in s:
			if ord(c) in (range(0x20, 0x26) + range(0x27, 0x7f)):
				if _in:
					r.extend(['&', modified_base64(''.join(_in)), '-'])
					del _in[:]
				r.append(str(c))
			elif c == '&':
				if _in:
					r.extend(['&', modified_base64(''.join(_in)), '-'])
					del _in[:]
				r.append('&-')
			else:
				_in.append(c)
		if _in:
			r.extend(['&', modified_base64(''.join(_in)), '-'])
		return ''.join(r)

	def list(self):
		"""Просматривает список ящиков на сервере imap"""
		def listwf(mail):
			self.log( 'Команда LIST' )
			res = mail.list()
			if isinstance(res,(list,tuple)):
				if len(res)>1 and res[0]=='OK' and isinstance(res[1],(list,tuple)):
					for item in res[1]:
						print self.decode_m_utf7( item )
		succ = self.imapWork( listwf )
		return succ