import json

from flask import Flask
from flask import request
from flask import jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mappings.verb import Verb
from mappings.translation import Translation

from config import config

app = Flask(__name__)
app.debug = True

engine_config = (
    config['db_engine'],
    config['db_user'],
    config['db_password'],
    config['db_host'],
    config['db_name']
)

engine = create_engine('%s://%s:%s@%s/%s' % engine_config, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/conjugate', methods=['GET'])
def conjugate():
    lang = request.args.get('lang')
    verb = request.args.get('verb')

    for entry in session.query(Verb).filter_by(lang=lang, verb=verb):
        deserialized = json.JSONDecoder('latin-1').decode(entry.conjugations)
        return jsonify(conjugations=deserialized)

    return jsonify(conjugations={})

@app.route('/translate', methods=['GET'])
def translate():
    lang = request.args.get('lang')
    english = request.args.get('english')

    translations = []
    entries = session.query(Translation).filter_by(lang=lang, english=english)
    for entry in entries:
        translations.append({
            'lang': lang,
            'english': english,
            'verb': entry.verb,
            'description': entry.description
        })

    return jsonify(translations=translations)

if __name__ == '__main__':
    app.run()