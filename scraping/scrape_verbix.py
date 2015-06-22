# -*- coding: utf-8 -*-

def load_src(name, fpath):
    import os, imp
    path = fpath if os.path.isabs(fpath) \
                 else os.path.join(os.path.dirname(__file__), fpath)

    return imp.load_source(name, path)

load_src('verb', '../site/mappings/verb.py')
load_src('translation', '../site/mappings/translation.py')

import argparse
import os
import json
import logging
import codecs
import re
import progressbar as pbar

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from verb import Verb
from translation import Translation

import verbix_scraper


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

def create_db_session(config, db_rebuild, language):
    logging.info('Connecting to database')

    engine_config = (
        config['db_engine'],
        config['db_user'],
        config['db_password'],
        config['db_host'],
        config['db_name']
    )

    engine = create_engine(
        '%s://%s:%s@%s/%s?charset=utf8&use_unicode=0' % engine_config,
        echo=False
    )

    Session = sessionmaker(bind=engine)
    db_session = Session()

    if db_rebuild:
        logging.info('Cleaning db for language %s' % language)
        db_session.query(Verb).filter_by(lang=language).delete()
        db_session.query(Translation).filter_by(lang=language).delete()
        db_session.commit()

    return db_session

def count_file_lines(file_name):
    i = 0
    with open(file_name, 'r') as f:
        for line in f:
            i += 1

    return i

def commit_verb_info(db_session, language, verb_info):
    verb_data_json = json.dumps(
        verb_info['modes'],
        sort_keys=True,
        indent = 4,
        separators=(',', ': '),
        ensure_ascii=False,
        encoding='utf-8'
    ).encode('utf-8')

    verb = Verb(
        lang=language,
        verb=verb_info['name'],
        conjugations=verb_data_json
    )

    db_session.add(verb)

    translations = []

    for meaning in verb_info['meanings']:
        translation = Translation(
            lang=language,
            english=meaning['eng'],
            description=meaning['description'],
            verb=verb.verb
        )
        duped_translation = next(
            (t for t in translations if t.english == translation.english),
            None
        )

        if duped_translation:
            duped_translation.description += ', ' + translation.description
        else:
            translations.append(translation)

    try:
        for translation in translations:
            db_session.add(translation)

        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        logging.error('Translations already exist %s' % str(translations))

    return True


def scrape_verb(language, word, db_session):
    scrapper = verbix_scraper.VerbixScraper()

    logging.info('Checking whether %s is a verb in %s' % (word, language))

    verb = scrapper.get_infinitive(language, word)

    if verb is None:
        return True

    try:
        db_verb = db_session.query(Verb).filter_by(
            lang=language,
            verb=verb
        ).one()
    except NoResultFound:
        logging.info('Attempting to retrieve verb info for %s' % verb)

        verb_info = scrapper.get_verb_info(language, verb)

        logging.info('Storing verb %s in database' % verb)

        if verb_info is None:
            logging.error('Failed to get verb info for %s' % verb)
            return

        if commit_verb_info(db_session, language, verb_info) is True:
            logging.info('Successfully added verb info for %s' % verb)
    else:
        logging.info('Verb %s is already in the db' % verb)

    return True


def cleanse_word(word):
    return word.replace('\n', '').split('/')[0]

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

def scrape_all_verbs(language, dictionary, db_session, log_file, resume):
    start_line = 0

    if resume:
        last_word = get_last_word(log_file)
        start_line = line_for_word(last_word, dictionary)
        logging.info('Resuming from word %s on line %d' % (last_word, start_line))

    reset_logging(log_file)

    num_words = count_file_lines(dictionary) - start_line
    logging.info('Scrapping %d words' % num_words)

    progressbar = create_progress_bar(num_words)
    current_word = 0
    failed_words = []

    with open(dictionary, 'r') as dictionary_file:
        for word in dictionary_file:
            current_word += 1

            if start_line >= current_word:
                continue

            word = cleanse_word(word)
            result = scrape_verb(language, word, db_session)

            if not result:
                failed_words.append(word)

            progressbar.update(current_word - start_line)

    progressbar.finish()

    return {
        'total_count': current_word,
        'failed_words': failed_words
    }

def print_report(results):
    num_failures = len(results['failed_words'])

    print '\nReport:'
    print 'Processed %d words' % results['total_count']
    print 'Failed to process %d words' % num_failures

    if num_failures > 0:
        print 'List of failed words:\n%s' % '\n'.join(results['failed_words'])

print '\nVERBIX TO DB SCRAPING'
print '=====================\n'

arguments = get_arguments()

config = get_config()

logging.basicConfig(
        filename=config['log_file'],
        format='%(levelname)s: %(asctime)s: %(message)s',
        level=getattr(logging, config.get('log_level', 'DEBUG').upper(), None)
    )

db_session = create_db_session(
    config,
    arguments.db_rebuild,
    arguments.language
)

results = scrape_all_verbs(
    arguments.language,
    arguments.dictionary,
    db_session,
    config['log_file'],
    arguments.resume
)

print_report(results)

print '\nDone!\n'