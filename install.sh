#! /bin/sh

# load updated dependencies
apt-get update

# python installation
apt-get install -y python

#pyserial installation
git clone https://github.com/pyserial/pyserial
cd pyserial
python setup.py install
cd ../
rm -R pyserial

# clone project
git clone https://gitlab.christoph-caprano.de/bachelorarbeit/command-server.git
cd command-server

# webserver installation
apt-get install -y apache2 php5 libapache2-mod-php5
service apache2 restart
cp web/index.php /var/www/html/index.php

# python programs
chown :www-data middleware.py
chmod g+x middleware.py
chmod u+x init.py

./init.py
