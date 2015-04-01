import json
import argparse
import os
import urllib2
import urllib
import verbix_scraper
import verbs_db

def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('language', help='Language code')
	parser.add_argument('dictionary', help='File with the list of words to retrieve')
	parser.add_argument('db_host', help='Database hostname')
	parser.add_argument('db_user', help='Database username')
	parser.add_argument('db_password', help='Database password')
	parser.add_argument('db_name', help='Database name')
	parser.add_argument('-r', '--db_rebuild', action="store_true", help='Rebuilds database')
	return parser.parse_args()

def count_file_lines(file_name):
	i = 0
	with open(file_name, 'r') as f:
		for line in f:
			i += 1

	return i

def commit_verb_info(db, language, verb_info):
	verb_data_json = json.dumps(
		verb_info['modes'],
		sort_keys=True,
		indent = 4,
		separators=(',', ': '),
		ensure_ascii=False,
		encoding='utf-8'
	).encode('utf-8')

	verb = verb_info['name']

	if db.insert_verb(language, verb, verb_data_json) is False:
		print 'Failed to get insert %s in db' % verb
		return False

	for meaning in verb_info['meanings']:
		if db.insert_translation(language, verb, meaning['eng'], meaning['description']) is False:
			print 'Failed to get insert translation for %s in db' % verb
			return False

	return True


def scrape_verb(language, word, db):
	scrapper = verbix_scraper.VerbixScraper()

	print 'Checking whether %s is a verb in %s' % (word, language)

	verb = scrapper.get_infinitive(language, word)

	if verb is None:
		return

	db_verb = db.get_verb(language, verb)

	if db_verb is not None:
		print 'Verb %s is already in the db' % verb
		return

	print 'Attempting to retrieve verb info for %s' % verb

	verb_info = scrapper.get_verb_info(language, verb)

	print 'Storing verb %s in database' % verb

	if verb_info is None:
		print 'Failed to get verb info for %s' % verb
		return

	if commit_verb_info(db, language, verb_info) is True:
		print 'Successfully added verb info for %s' % verb

		
def cleanse_word(word):
	return word.replace('\n', '')

def db_setup(db_host, db_user, db_password, db_name, db_rebuild):
	print 'Connecting to database'

	db = verbs_db.VerbsDB(db_host, db_user, db_password, db_name)

	if db_rebuild:
		print 'Rebuilding database'
		db.build()

	return db

def scrape_all_verbs(language, dictionary, db):
	print 'Scrapping %d words' % count_file_lines(dictionary)

	with open(dictionary, 'r') as dictionary_file:
		for word in dictionary_file:
			word = cleanse_word(word)
			scrape_verb(language, word, db)

print '\nVERBIX TO DB SCRAPPING'
print '======================\n'

arguments = get_arguments()

db = db_setup(
	arguments.db_host,
	arguments.db_user,
	arguments.db_password,
	arguments.db_name,
	arguments.db_rebuild
)

scrape_all_verbs(
	arguments.language,
	arguments.dictionary,
	db
)
				 
