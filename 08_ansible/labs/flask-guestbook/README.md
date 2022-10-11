This is used in the demonstration of development of Ansible Playbooks.

  Below are the steps required to get this working on a base linux system.

  - Install all required dependencies
  - Start Web Server

## 1. Install system dependencies

  Python and its dependencies

    apt-get install -y python python-setuptools python-dev build-essential python-pip python-mysqldb


## 2. Install application dependencies

Install python dependencies

    pip install configparser
    pip install flask
    pip install flask-sqlalchemy

## 3. Download the application
git clone https://github.com/ameade/flask-guestbook /opt/flask-guestbook

## 4. Start Web Server
Ensure the application is not already running
  kill $(ps -ef |grep -v grep | grep -w flask |awk '{print $2}')
Start web server in a background process
    FLASK_APP=/opt/flask-guestbook/app.py nohup flask run -h 0.0.0.0 -p 8080 &

## 5. Test
    List messages
    curl http://<IP>:8080/signatures

    Write a message
    curl -X POST http://<IP>:8080/signatures?message="my message"

# Add a mysql database

## 1. Install and Configure Database

 Install MySQL database

    apt-get install -y mysql-server mysql-client

 Allow any host to connect
 sed -i "s/.*bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/mariadb.conf.d/50-server.cnf

## 2. Start Database Service
  - Start the database service

        service mysqld start

  - Create database and database users

        # mysql -u <username> -p

        mysql> CREATE DATABASE guestbook;
        mysql> GRANT ALL ON *.* to db_user@'%' IDENTIFIED BY 'Passw0rd';

  - Configure database credentials and parameters for the app
        The app looks for a configuration file at '/opt/guestbook/vars.ini'
