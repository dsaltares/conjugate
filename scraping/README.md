# Verbix scraper

Conjugate uses [Verbix](http://www.verbix.com/) online verb conjugator as a data source. The data is collected through [scraping](https://www.wikiwand.com/en/Web_scraping) and dumped into a MySQL database with the `scrape_verbix` Python script.

*Disclaimer*: Verbix allows non-commercial use of their data.

### Dependencies

* Python 2.7
* [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/)
* [html5lib](https://pypi.python.org/pypi/html5lib)
* [MySQLdb](https://pypi.python.org/pypi/MySQL-python)

### Running the script

First, take a look at the `config.json` file and set the parameters to match your database settings.

```json
{
	"db_host": "localhost",
	"db_user": "root",
	"db_password": "",
	"db_name": "verbs"
}
```

Then run `python scrape_verbix.py`.

```
usage: scrape_verbix.py [-h] [-r] language dictionary

positional arguments:
  language          Language code
  dictionary        File with the list of words to retrieve

optional arguments:
  -h, --help        show this help message and exit
  -r, --db_rebuild  Rebuilds database
```

The `language` argument expects a typical language code such as `"es"` (Spanish) or `"ro"` (Romanian). The scraper needs a list of words in the target language to check if they are verbs through Verbix, hence the `dictionary` argument. The dictionary is meant to be a plain text file with one word per line.