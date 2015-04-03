# -*- coding: utf-8 -*-

import json
import argparse
import os
import urllib2
import urllib
import json
import logging
import codecs
import re
import verbix_scraper
import progressbar as pbar
import verbs_db

def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('language', help='Language code')
	parser.add_argument('dictionary', help='File with the list of words to retrieve')
	parser.add_argument('-d', '--db_rebuild', action="store_true", help='Rebuilds database')
	parser.add_argument('-r', '--resume', action="store_true", help='Resumes process using log file')
	return parser.parse_args()

def get_config():
	config = {}

	with open('config.json') as config_file:
		config = json.load(config_file)

	return config

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
		logging.error('Failed to get insert %s in db' % verb)
		return False

	for meaning in verb_info['meanings']:
		if db.insert_translation(language, verb, meaning['eng'], meaning['description']) is False:
			logging.error('Failed to get insert translation for %s in db' % verb)
			return False

	return True


def scrape_verb(language, word, db):
	scrapper = verbix_scraper.VerbixScraper()

	logging.info('Checking whether %s is a verb in %s' % (word, language))

	verb = scrapper.get_infinitive(language, word)

	if verb is None:
		return

	db_verb = db.get_verb(language, verb)

	if db_verb is not None:
		logging.info('Verb %s is already in the db' % verb)
		return

	logging.info('Attempting to retrieve verb info for %s' % verb)

	verb_info = scrapper.get_verb_info(language, verb)

	logging.info('Storing verb %s in database' % verb)

	if verb_info is None:
		logging.error('Failed to get verb info for %s' % verb)
		return

	if commit_verb_info(db, language, verb_info) is True:
		logging.info('Successfully added verb info for %s' % verb)

		
def cleanse_word(word):
	return word.replace('\n', '')

def db_setup(db_host, db_user, db_password, db_name, db_rebuild):
	logging.info('Connecting to database')

	db = verbs_db.VerbsDB(db_host, db_user, db_password, db_name)

	if db_rebuild:
		logging.info('Rebuilding database')
		db.build()

	return db

def reset_logging(file_name):
	try:
		os.remove(file_name)
	except Exception:
		pass

def create_progress_bar(max_value):
	return pbar.ProgressBar(
		widgets=[
			pbar.Percentage(),
			pbar.Bar(),
			pbar.FormatLabel('Processed: %(value)d/{0} words (in: %(elapsed)s)'.format(max_value))
		],
		maxval=max_value
	).start()

def get_last_word(file_name):
	with codecs.open(file_name, encoding='utf-8') as log_file:
		for line in reversed(log_file.readlines()):
			pattern = re.compile('.*Checking whether\s(?P<verb>.*?)\sis a verb')
			match = pattern.match(line)

			if match:
				return match.group('verb')


def line_for_word(word, file_name):
	line_number = 0

	with codecs.open(file_name, encoding='utf-8') as word_file:
		for line in word_file:
			if word == cleanse_word(line):
				return line_number
			line_number += 1
			
	return 0	

def scrape_all_verbs(language, dictionary, db, log_file, resume):
	start_line = 0

	if resume:
		last_word = get_last_word(log_file)	
		start_line = line_for_word(last_word, dictionary)

	reset_logging(log_file)

	num_words = count_file_lines(dictionary) - start_line
	logging.info('Scrapping %d words' % num_words)

	progressbar = create_progress_bar(num_words)
	current_word = 0

	with open(dictionary, 'r') as dictionary_file:
		for word in dictionary_file:
			current_word += 1

			if start_line >= current_word:
				continue

			word = cleanse_word(word)
			scrape_verb(language, word, db)
			progressbar.update(current_word - start_line)

	progressbar.finish()

print '\nVERBIX TO DB SCRAPING'
print '=====================\n'

arguments = get_arguments()

config = get_config()

logging.basicConfig(
		filename=config['log_file'],
		format='%(levelname)s: %(asctime)s: %(message)s',
		level=logging.DEBUG
	)

db = db_setup(
	config['db_host'],
	config['db_user'],
	config['db_password'],
	config['db_name'],
	arguments.db_rebuild
)

scrape_all_verbs(
	arguments.language,
	arguments.dictionary,
	db,
	config['log_file'],
	arguments.resume
)
				 
print 'Done!\n'