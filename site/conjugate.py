import json
import logging
import traceback

from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from flask import send_from_directory
from flask import Blueprint

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from mappings.verb import Verb
from mappings.translation import Translation
from logging.handlers import RotatingFileHandler

from config import config

try:
    import environment_config
except ImportError:
    pass


def create_log_handler():
    formatter = logging.Formatter(
        '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    )
    handler = RotatingFileHandler(
        config['log_file'],
        maxBytes=config['log_max_bytes'],
        backupCount=config['log_backup_count']
    )
    handler.setLevel(config['log_level'])
    handler.setFormatter(formatter)

    return handler

def create_session():
    engine_config = (
        config['db_engine'],
        config['db_user'],
        config['db_password'],
        config['db_host'],
        config['db_name']
    )

    engine = create_engine(
        '%s://%s:%s@%s/%s?charset=utf8&use_unicode=0' % engine_config,
        echo=True
    )

    Session = sessionmaker(bind=engine)

    return Session()


bp = Blueprint(
    'bp',
    __name__,
    template_folder='templates'
)

app = Flask(__name__)
app.debug = config['debug']
app.logger.addHandler(create_log_handler())

session = create_session()


def get_translations(lang, english):
    app.logger.debug('Trying to translate (%s, %s)' % (lang, english))

    translations = []

    try:
        for entry in session.query(Translation).filter_by(lang=lang, english=english):
            translations.append({
                'lang': lang,
                'english': english,
                'verb': entry.verb,
                'description': entry.description
            })
    except:
        app.logger.error('Error querying translations for (%s, %s)\n%s' % (lang, english, traceback.format_exc()))
        raise

    app.logger.debug('%d translations found for (%s, %s)' % (len(translations), lang, english))

    return translations

def get_conjugations(lang, verb):
    app.logger.debug('Trying to conjugate (%s, %s)' % (lang, verb))

    conjugations = []

    try:
        entry = session.query(Verb).filter_by(lang=lang, verb=verb).one()
        conjugations = json.JSONDecoder('utf-8').decode(entry.conjugations)
        app.logger.debug('Found %d conjugations for (%s, %s)' % (len(conjugations), lang, verb))
    except NoResultFound:
        app.logger.warning('No conjugations found for (%s, %s)' % (lang, verb))
    except:
        app.logger.error('Error querying conjugations for (%s, %s)\n%s' % (lang, verb, traceback.format_exc()))
        raise

    return conjugations

def get_english(lang, verb):
    app.logger.debug('Trying to get the English verb for (%s, %s)' % (lang, verb))

    translations = []



    try:
        for entry in session.query(Translation).filter_by(lang=lang, verb=verb):
            translations.append({
                'lang': lang,
                'verb': verb,
                'english': entry.english,
                'description': entry.description
            })

            app.logger.debug('Found English for (%s, %s): %s' % (lang, verb, entry.english))
    except NoResultFound:
        app.logger.warning('No English found for (%s, %s)' % (lang, verb))
    except:
        app.logger.error('Error querying English for (%s, %s)\n%s' % (lang, verb, traceback.format_exc()))
        raise

    return translations


@bp.route('/')
def index():
    app.logger.debug('Processing rule %s' % request.url_rule)
    return render_template('index.html')

@bp.route('/js/<path:path>')
def send_js(path):
    app.logger.debug('Processing rule %s' % request.url_rule)
    return send_from_directory('js', path)

@bp.route('/conjugate', methods=['POST'])
def conjugate():
    app.logger.debug('Processing rule %s' % request.url_rule)

    lang = request.form['lang']
    verb = request.form['verb']
    translate = request.form['translate']
    translate = translate == 'true'

    if translate:
        def make_verb(translation):
            return {
                'lang': translation['lang'],
                'english': translation['english'],
                'verb': translation['verb'],
                'description': translation['description'],
                'conjugations': get_conjugations(
                    translation['lang'],
                    translation['verb']
                )
            }

        return jsonify(
            verbs=[make_verb(translation) \
                   for translation in get_translations(lang, verb)]
        )
    else:
        return jsonify(verb={
            'lang': lang,
            'translations': get_english(lang, verb),
            'verb': verb,
            'conjugations': get_conjugations(
                lang,
                verb
            )
        })

app.register_blueprint(bp, url_prefix=config['url_prefix'])

if __name__ == '__main__':
    app.logger.debug('Running conjugate with config:\n%s' % config)
    app.run(host=config['app_host'])
