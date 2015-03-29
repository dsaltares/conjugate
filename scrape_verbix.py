import json
import verbix_scrapper
import argparse
import os
import urllib2
import urllib

def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('language', help='Language code')
	parser.add_argument('dictionary', help='File with the list of words to retrieve')
	parser.add_argument('output_dir', help='Output dir')
	return parser.parse_args()

def count_file_lines(file_name):
	i = 0
	with open(file_name, 'r') as f:
		for line in f:
			i += 1

	return i

def scrape_verb(language, word, output_dir):
	scrapper = verbix_scrapper.VerbixScrapper()

	print 'Checking whether %s is a verb in %s' % (word, language)

	verb = scrapper.get_verb(language, word)

	if verb is None:
		return

	print 'Attempting to retrieve conjugations for %s in %s' % (verb, language)

	conjugations = scrapper.get_conjugations(language, verb)

	if conjugations is None:
		print 'Failed to get conjugations for %s in %s' % (verb, language)
		return

	file_name = os.path.join(output_dir, verb) + '.json'

	with open(file_name, 'w') as file_out:
		json_dump = json.dumps(
			conjugations,
			sort_keys=True,
			indent = 4,
			separators=(',', ': '),
			ensure_ascii=False,
			encoding='utf-8').encode('utf-8')
		file_out.write(json_dump)
		print 'Successfully retrieved conjugations for %s in %s' % (verb, language)

def cleanse_word(word):
	return word.replace('\n', '')

def ensure_dir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

def scrape_all_verbs(language, dictionary, output_dir):
	ensure_dir(output_dir)

	print 'Scrapping %d words' % count_file_lines(dictionary)

	with open(dictionary, 'r') as dictionary_file:
		for word in dictionary_file:
			word = cleanse_word(word)
			scrape_verb(language, word, output_dir)

arguments = get_arguments()

scrape_all_verbs(arguments.language,
				 arguments.dictionary,
				 arguments.output_dir)
