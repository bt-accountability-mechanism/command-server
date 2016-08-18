#! /bin/sh

# webserver installation
apt-get update
apt-get install -y apache2 php5 libapache2-mod-php5
service apache2 restart
cp web/index.php /var/www/html/index.php

# python programs
chown :www-data middleware.py
chmod g+x middleware.py
chmod u+x init.py

