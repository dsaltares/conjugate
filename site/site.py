import json

from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from flask import send_from_directory

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

engine = create_engine('%s://%s:%s@%s/%s?charset=utf8&use_unicode=0' % engine_config, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/conjugate', methods=['POST'])
def conjugate():
    lang = request.form['lang']
    verb = request.form['verb']

    for entry in session.query(Verb).filter_by(lang=lang, verb=verb):
        deserialized = json.JSONDecoder('utf-8').decode(entry.conjugations)
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