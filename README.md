# Web API interface for iRobot App

## Installation

### Install a web server on your server with PHP support

#### Option1: apache2

##### Install apache2
```
sudo apt-get update
sudo apt-get install apache2
```

##### Install PHP
This example shows how to install PHP-5, but you can use any other version >= 5. 

Install PHP: 
```
sudo apt-get install php5 libapache2-mod-php5
```

Restart Apache2
```
sudo service apache2 restart
```

Ref: https://www.digitalocean.com/community/tutorials/how-to-install-linux-apache-mysql-php-lamp-stack-on-ubuntu

#### Option2: nginx

##### Install nginx

```
sudo apt-get update
sudo apt-get install nginx
```

###### Install PHP

First install PHP-FPM

```
sudo apt-get install php5-fpm
``

Next, activate it in your nginx server
`sudo nano /etc/nginx/sites-available/default`

Replace the content with the following: 

```
server {
  listen 80 default_server;
  listen [::]:80 default_server ipv6only=on;

  root /usr/share/nginx/html;
  index index.php index.html index.htm;

  server_name server_domain_name_or_IP;

  location / {
    try_files $uri $uri/ =404;
  }

  error_page 404 /404.html;
  error_page 500 502 503 504 /50x.html;
  location = /50x.html {
    root /usr/share/nginx/html;
  }

  location ~ \.php$ {
    try_files $uri =404;
    fastcgi_split_path_info ^(.+\.php)(/.+)$;
    fastcgi_pass unix:/var/run/php5-fpm.sock;
    fastcgi_index index.php;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    include fastcgi_params;
  }
}

```

Restart nginx
```
sudo service nginx restart
```

### Clone repo in public webserver folder

If you use apache2, /var/www/html should be normally your public folder: 
```
cd /var/www/html
```

If you use nginx, /var/www/html should be normally your public folder:
```
cd /usr/share/nginx/html
```

--------------
Now clone the repository: 
```
git clone http://gitlab.christoph-caprano.de/bachelorarbeit/robot_web.git
```

You can call the script now by running http://localhost/robot_web/index.php

Available are the following actions: 
* straight_on
* left
* right
* turn_around
* toot
* reset
* dock_mode
* passive_mode
* active_mode
* safe_mode
* cleaning_mode

Example: Toot: 
http://localhost/robot_web/index.php?action=toot

When you use the first 4 actions (left, right, straight_on, turn_around), you have to add a finished flag which tells the server if the move starts (false) or stops (true): 
Example: 
Start moving left: 
http://localhost/robot_web/index.php?action=left&finished=false
End moving left: 
http://localhost/robot_web/index.php?action=left&finished=true

For saving logs, please make a POST request with the following parameters: 
``
{
    message: string
}
``
# iRobot control

This program helps you to control your iRobot within a web interface or other script you would like to run. 

## Installation

### 1. Clone this repository
```
git clone http://gitlab.christoph-caprano.de/bachelorarbeit/robot.git
cd robot
```

### 2. Make the middleware.py available for other users (required if you call this script from users with minimal rights, e.g. www-data)

The middleware.py should be called from your webserver script (or any other script which receives and prepares the commands). The format for calling this script will be explained in the [usage guide](#usage). 

This command shows how to change the group for a web server user www-data
```
chown :www-data middleware.py
```

Next you have to make this file executable
```
chmod g+x middleware.py
```

### 3. Make boot.sh executable (if not still done)
```
chmod u+x init.py
```

Next, the initialization program can be started which runs also the middleware for accepting proxy requests (e.g. from your webserver). 

```
./init.py
```

## <a name="usage"></a>Usage guide

### 1. Start the program
```
./init.py
```
### 2. Call the middleware
This example shows how to call the middleware from a web server script: 

```php
<?php
// this command resets your robot
$action = 'RESET';
$path = '/YOUR/PATH';
$file = 'middleware.py';
chdir($path);
// middleware is called with ./middleware.py ACTION:STRING IS_FINISHED:BOOL
shell_exec('./'.$file.' '.$action.' false');
?>
```

This content was still copied to your public webserver root folder (/var/www/html)


### 3. Hurray! Robot should reset


## Simulation without robot
Set the environment variable export TEST_IROBOT to 1: 
``
export TEST_IROBOT=1
``