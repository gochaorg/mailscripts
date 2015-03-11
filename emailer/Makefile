# Бренд
BRAND=cofe.xyz

# Пакет
PACKAGE=emailer

# Версия
VERSION=0.1

# Зависимости
DEPENDS=python, p7zip-full

# Кто собирал пакет
MAINTAINER=Kamnev Georgiy <nt.gocha@gmail.com>

# Автор программы
AUTHOR=Kamnev Georgiy <nt.gocha@gmail.com>

# Владелец copyright
COPYRIGHT_HOLDER=Kamnev Georgiy <nt.gocha@gmail.com>

# Домашняя страница проекта
HOMEPAGE=https://github.com/gochaorg/mailscripts/tree/master/emailer

# Вид ПО к которому отонсится
SECTION=mail

#Архитектура
ARCHITECTURE=all

# Приоритет
PRORITY=optional

# Краткое описание
DESC_SHORT=Программа отправки писем.

# Файл с описанием
DESC_FILE=desc.txt

# Файл номера сборки
BUILD_NUMBER_FILE=build-number.txt

# Номер сборки
BUILD_NUMBER=$$(cat $(BUILD_NUMBER_FILE))

# Дата сборки
BUILD_DATE=$$(date +%Y-%m-%d)

# Дата сборки - год
BUILD_DATE_YEAR=$$(date +%Y)

# Дата сборки - месяц
BUILD_DATE_MONTH=$$(date +%m)

# Дата сборки - день
BUILD_DATE_DATE=$$(date +%d)

# Временный каталог для сборки DEB
DEBDIR=$(PACKAGE)_$(VERSION)_tmp

# Каталог BIN который прописан в PATH
BINDIR=usr/bin

# Контрольный файл DEB
CONTROL_FILE=$(DEBDIR)/DEBIAN/control

# Атрибуты каталогов по умолчанию
DIR_ATTR_DEF=0755

# Шаблон copyright
COPYRIGHT_TMPL=$$(cat copyright_tmpl)

# Файл copyright
COPYRIGHT_FILE=$(DEBDIR)/DEBIAN/copyright

# Рабочий каталог
BASEDIR=$$(pwd)

# Файл с информацией о сборке
BUILD_INFO_FILE=$(DEBDIR)/usr/lib/$(BRAND)/$(PACKAGE)/$(PACKAGE)_buildinfo.py

buildnumber:
	@if ! test -f $(BUILD_NUMBER_FILE) ;	then echo 0 > $(BUILD_NUMBER_FILE) ; fi
	@echo $$(($$(cat $(BUILD_NUMBER_FILE)) + 1)) > $(BUILD_NUMBER_FILE)
	@echo buildnumber = $(BUILD_NUMBER)

init: buildnumber

clean:
	if [ -d $(DEBDIR) ] ; then rm -rf $(DEBDIR) ; fi
	rm $(PACKAGE)*.deb

control: init debdir
	echo "Package: $(PACKAGE)" > $(CONTROL_FILE)
	echo "Version: $(VERSION)-$(BUILD_NUMBER)" >> $(CONTROL_FILE)
	echo "Architecture: $(ARCHITECTURE)" >> $(CONTROL_FILE)
	echo "Maintainer: $(MAINTAINER)" >> $(CONTROL_FILE)
	echo "Section: $(SECTION)" >> $(CONTROL_FILE)
	echo "Depends: $(DEPENDS)" >> $(CONTROL_FILE)
	echo "Priority: $(PRORITY)" >> $(CONTROL_FILE)
	echo "Homepage: $(HOMEPAGE)" >> $(CONTROL_FILE)
	echo "Description: $(DESC_SHORT)" >> $(CONTROL_FILE)
	[ -e $(DESC_FILE) ] && cat $(DESC_FILE) >> $(CONTROL_FILE)
	echo "" >> $(CONTROL_FILE)

debdir: init
	mkdir -p $(DEBDIR)/DEBIAN
	mkdir -p $(DEBDIR)/$(BINDIR)
	mkdir -p $(DEBDIR)/usr/lib/$(BRAND)/$(PACKAGE)
	find $(DEBDIR) -type d -exec chmod $(DIR_ATTR_DEF) {} \;

	#chmod -R 0755 $(DEBDIR)/$(BINDIR)
	#chmod -R 0755 $(DEBDIR)/usr/lib
	
	#cp copyright $(DEBDIR)/DEBIAN
	#[ -d $(DEBDIR)/usr ] && chmod 0755 $(DEBDIR)/usr
	#cp *.py $(DEBDIR)/usr/lib/$(BRAND)/$(PACKAGE)
	#chmod 0755 $(DEBDIR)/usr/lib/$(BRAND)/$(PACKAGE)/sendemail.py
	#ln -sfv ../lib/$(BRAND)/$(PACKAGE)/sendemail.py $(DEBDIR)/$(BINDIR)/emailer

copyright: debdir
	eval "PACKAGE=\"$(PACKAGE)\"; \
	DESC_SHORT=\"$(DESC_SHORT)\"; \
	AUTHOR=\"$(AUTHOR)\"; \
	BUILD_DATE=\"$(BUILD_DATE)\"; \
	HOMEPAGE=\"$(HOMEPAGE)\"; \
	BUILD_NUMBER=\"$(BUILD_NUMBER)\"; \
	BUILD_DATE_DATE=\"$(BUILD_DATE_DATE)\"; \
	BUILD_DATE_YEAR=\"$(BUILD_DATE_YEAR)\"; \
	BUILD_DATE_MONTH=\"$(BUILD_DATE_MONTH)\"; \
	COPYRIGHT_HOLDER=\"$(COPYRIGHT_HOLDER)\"; \
	echo \"$(COPYRIGHT_TMPL)\"" > $(COPYRIGHT_FILE)

copyfiles: debdir
	cp -a *.py $(DEBDIR)/usr/lib/$(BRAND)/$(PACKAGE)
	find . \
	  -maxdepth 1 \
	  -executable -type f \
	  -exec cp -a {}  $(DEBDIR)/usr/lib/$(BRAND)/$(PACKAGE) \;
	
	# Создание ссылок на исполняемые файлы
	find $(DEBDIR)/usr/lib/$(BRAND)/$(PACKAGE) \
	  -executable -type f \
	  -exec bash -c 'VAR={}; VAR=$$(basename $$VAR); echo $$VAR; ln -sv -t $(DEBDIR)/$(BINDIR) ../lib/$(BRAND)/$(PACKAGE)/$$VAR' \;

buildinfo: debdir
	echo "# -*- coding: utf-8 -*-" > $(BUILD_INFO_FILE)
	echo "def BUILD_NUM():" >> $(BUILD_INFO_FILE)
	echo "	return $(BUILD_NUMBER)" >> $(BUILD_INFO_FILE)

	echo "def BUILD_DATE():" >> $(BUILD_INFO_FILE)
	echo "	return \"\"\"$(BUILD_DATE)\"\"\"" >> $(BUILD_INFO_FILE)

	echo "def BUILD_HOMEPAGE():" >> $(BUILD_INFO_FILE)
	echo "	return \"\"\"$(HOMEPAGE)\"\"\"" >> $(BUILD_INFO_FILE)

	echo "def BUILD_AUTHOR():" >> $(BUILD_INFO_FILE)
	echo "	return \"\"\"$(AUTHOR)\"\"\"" >> $(BUILD_INFO_FILE)

	echo "def BUILD_VERSION():" >> $(BUILD_INFO_FILE)
	echo "	return \"\"\"$(VERSION)\"\"\"" >> $(BUILD_INFO_FILE)

	echo "def BUILD_MAINTAINER():" >> $(BUILD_INFO_FILE)
	echo "	return \"\"\"$(MAINTAINER)\"\"\"" >> $(BUILD_INFO_FILE)

	echo "def BUILD_PACKAGE():" >> $(BUILD_INFO_FILE)
	echo "	return \"\"\"$(PACKAGE)\"\"\"" >> $(BUILD_INFO_FILE)

	echo "def BUILD_BRAND():" >> $(BUILD_INFO_FILE)
	echo "	return \"\"\"$(BRAND)\"\"\"" >> $(BUILD_INFO_FILE)

deb: debdir control copyright copyfiles buildinfo
	fakeroot dpkg-deb -b $(DEBDIR)
	mv $(DEBDIR).deb $(PACKAGE)_$(VERSION)-$(BUILD_NUMBER)_$(ARCHITECTURE).deb