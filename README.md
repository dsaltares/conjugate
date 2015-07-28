# Conjugate

A verb conjugator service. Enter a verb in English and get the conjugations for all tenses in a variety of languages.

Conjugate is available [here](http://saltares.com/conjugate).

### Motivation

When learning a new language, it is very common to struggle with verb conjugations. For example:

> I want to know the third person singular form (masculine) of the future perfect tense of the verb *to eat* in French.

Unfortunately, the available resources are somehow limited:

* Google translator: usually gets conjugations wrong for most languages, especially in terms of gender.
* Apps: seriously? I don't want to install *yet* another app!
* Websites: lists are limited, the sites are old, full of ads and/or don't play well with mobile devices.

Conjugate tries to solve that use case.

### Components

* [Verbix Scraper](https://github.com/siondream/conjugate/tree/master/scraping)
* [Web application](https://github.com/saltares/conjugate/tree/master/site)

### Dependencies

* Python 2.7
* [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/)
* [html5lib](https://pypi.python.org/pypi/html5lib)
* [MySQLdb](https://pypi.python.org/pypi/MySQL-python)
* [progressbar](https://pypi.python.org/pypi/progressbar/2.2)
* [Flask](http://flask.pocoo.org/)
* [sqlAlchemy](http://www.sqlalchemy.org/)

### Report issues

Something not working quite as expected? Do you need a feature that has not been implemented yet? Check the [issue tracker](https://github.com/siondream/conjugate/issues) and add a new one if your problem is not already listed. Please try to provide a detailed description of your problem, including the steps to reproduce it.

### Contribute

Awesome! If you would like to contribute with a new feature or submit a bugfix, fork this repo and send a [pull request](https://github.com/siondream/conjugate/pulls)

### License

Conjugate is licensed under the [Apache 2 License](https://github.com/siondream/conjugate/blob/master/LICENSE), meaning you can use it free of charge, without strings attached in commercial and non-commercial projects. However, if you happen to become a millionaire thanks to it, please do buy me a beer!
