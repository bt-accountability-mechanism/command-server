# Control server for receiving HTTP commands from a client

## Requirements

 - Ubuntu 14.04 OS or Ubuntu 16.x OS or Raspberry OS

## Getting started

You can call the script now by running http://localhost/index.php

Available are the following actions: 
 - straight_on
 - left
 - right
 - turn_around
 - toot
 - reset
 - dock_mode
 - passive_mode
 - active_mode
 - safe_mode
 - cleaning_mode

Example: Toot: 
http://localhost/index.php?action=toot&finished=false

When you use the first 4 actions (left, right, straight_on, turn_around), you have to add a finished flag which tells the server if the move starts (false) or stops (true): 
Example: 
Start moving left: 
http://localhost/index.php?action=left&finished=false
End moving left: 
http://localhost/index.php?action=left&finished=true

For saving logs, please make a POST request with the following parameters: 
```
{
message: string
}
```

Example: `curl -X POST http://localhost/index.php -d "message: \"incredible important log message\""`


## For interested: What does install.sh and how to use program with nginx? 

### Main program

#### Installation

This program helps you to control your iRobot within a web interface or other script you would like to run. 

- Install Python
```bash
$ sudo apt-get update
$ sudo apt-get install python
$ git clone https://github.com/pyserial/pyserial
$ cd pyserial
$ python setup.py install
$ cd ../
$ rm -R pyserial
```

- Make the middleware.py available for other users (required if you call this script from users with minimal rights, e.g. www-data)

    The middleware.py should be called from your webserver script (or any other script which receives and prepares the commands). The format for calling this script will be explained in the [usage guide](#usage). 
    
    This command shows how to change the group for a web server user www-data
    ```
    chown :www-data middleware.py
    ```

    Next you have to make this file executable
    ```
    chmod g+x middleware.py
    ```

- Make boot.sh executable (if not still done)
    ```
    chmod u+x init.py
    ```

    Next, the initialization program can be started which runs also the middleware for accepting proxy requests (e.g. from your webserver). 

    ```
    ./init.py
    ```

#### <a name="usage"></a>Usage guide

- Start the program
    ```
    ./init.py
    ```
- Call the middleware
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


- Hurray! Robot should reset


#### Simulation without robot
Set the environment variable export TEST_IROBOT to 1: 
```
export TEST_IROBOT=1
```

### Install a web server on your server with PHP support

#### Option1: apache2

##### Install apache2
```bash
$ sudo apt-get update
$ sudo apt-get install apache2
```

#### Install PHP
This example shows how to install PHP-5, but you can use any other version >= 5. 

Install PHP: 
```bash
$ sudo apt-get install php5 libapache2-mod-php5
```

Restart Apache2
```bash
sudo service apache2 restart
```

Ref: https://www.digitalocean.com/community/tutorials/how-to-install-linux-apache-mysql-php-lamp-stack-on-ubuntu

#### Option2: nginx

##### Install nginx

```bash
$ sudo apt-get update
$ sudo apt-get install nginx
```

###### Install PHP

First install PHP-FPM

```bash
$ sudo apt-get install php5-fpm
```

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
```bash
sudo service nginx restart
```

### Clone PHP file in public webserver folder

Next, the file which should handle the incomming command requests have to be copied to the public webserver.

If you use apache2, /var/www/html should be normally your public folder: 
```
cp web/index.php /var/www/html/index.php
```

If you use nginx, /var/www/html should be normally your public folder:
```
cd web/index.php /usr/share/nginx/html/index.php
```
