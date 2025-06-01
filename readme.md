# [PolitePol.com](http://politepol.com "RSS Feed Generator")
# RSS feed generator website with user friendly interface

### Warning: This source code is outdated! Use full featured version on [PolitePol.com](http://politepol.com "RSS Feed Generator")

![PolitePol.com](frontend/frontend/assets/frontend/images/apple-touch-icon-144x144-precomposed.png "PolitePol.com")

This is source code of RSS feed generator website with user friendly interface.

## Installation of development server for Ubuntu
(If you have some questions please contact me by github email)

Install required packages
```
sudo apt-get install python3-minimal libmysqlclient-dev libxml2-dev libxslt-dev python3-dev libffi-dev gcc libssl-dev gettext
```

Install pip
```
pushd /tmp
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
popd
```

Install pip packages
```
sudo pip3 install -r requirements.txt
```

Install less and yuglify
```
sudo apt-get install nodejs npm
sudo npm install -g less@2.7.1
sudo npm -g install yuglify@0.1.4
sudo ln -s /usr/bin/nodejs /usr/bin/node
```

Install sass
```
sudo apt-get install ruby
sudo su -c "gem install sass -v 3.7.4"
```

Install and setup nginx
```
sudo apt-get install nginx
sudo cp pol/nginx/default.site-example /etc/nginx/sites-available/default
sudo service nginx reload
```

Install and setup mysql if you didn't yet.
```
sudo apt-get install mysql-server

sudo mysql -u root
mysql> USE mysql;
mysql> UPDATE user SET plugin='mysql_native_password' WHERE User='root';
mysql> FLUSH PRIVILEGES;
mysql> exit;

sudo mysql_secure_installation
```

Create database. **Use password 'toor' for root user**
```
mysql -uroot -ptoor -e 'CREATE DATABASE pol DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;'
```

Create django config
```
cp pol/frontend/frontend/settings.py.example pol/frontend/frontend/settings.py
```

Initialise database
```
pushd pol/frontend
python3 manage.py migrate
python3 manage.py loaddata fields.json
popd
```

## Run servers

Run downloader server
```
pushd pol
python3 downloader.py
popd
```

Run frontend server
```
pushd pol/frontend
python3 manage.py runserver
popd
```

### JSON feed output

Feed URLs accept an optional `format` query parameter. Use `?format=json` to
get feed items serialized as JSON instead of the default RSS XML.

## Running tests

After installing dependencies from `requirements.txt`, run:

```
pytest
```


# Installation of Docker

## Build
```
git clone https://github.com/taroved/pol
cd pol
docker-compose up -d --build
```

### Environment variables
The application reads configuration from the following variables with defaults
(shown in parentheses):

* `DB_NAME` (`pol`)
* `DB_USER` (`root`)
* `DB_PASSWORD` (`toor`)
* `DB_HOST` (`127.0.0.1`)
* `DB_PORT` (`3306`)
* `TIME_ZONE` (`UTC`)
* `WEB_PORT` (`8000`)
* `SECRET_KEY` (built-in demo key)
* `DEBUG` (`True`)

## Access (port 8088)
Docker Host IP in browser. Ex:
http://192.168.0.10:8088


## License

MIT
