# Conjugate web application

Conjugate is a [Flask] application and deploying it is fairly easy.

### Download Conjugate

First, download the repository from GitHub:

`git clone git@github.com:saltares/conjugate.git`

Stable releases are easily retrievable by tags, so checkout the release you want to use:

`git checkout tags/conjugate-1.0.0`

Having your `.git` folder in your web application is a bad idea and a security hazard so:

`rm -rf .git`

### Configuration

Conjugate ships with a default configuration in `config.py` but you may want to override it. You can either edit the values
there or add a separate `environment_config.py` file that imports the default one and modifies the `config` object.
Here is the list of variables you can configure, their purpose is rather self explanatory.

```python
config = {
    'db_engine': 'mysql',
    'db_user': 'root',
    'db_password': '',
    'db_name': 'verbs',
    'db_host': '127.0.0.1',
    'db_reconnects': 5,
    'app_host': '127.0.0.1',
    'debug': True,
    'url_prefix': '',
    'log_file': 'conjugate.log',
    'log_level': logging.DEBUG,
    'log_max_bytes': 10000000,
    'log_backup_count': 5,
    'google_analytics_token': ''
}
```

### Web server configuration

Flasks applications can be run from the web server of your choice, I personally use nginx and this
[tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-14-04)
proved to be quite useful.