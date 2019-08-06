import os

from flask import Flask, request, render_template, send_from_directory
from elasticsearch import Elasticsearch

import globals
import presentation
import common
import mimetypes

es = Elasticsearch([globals.ES_HOST], http_auth=(globals.ES_USER, globals.ES_PASSWORD))
app = Flask(__name__)


@app.route('/')
def my_form():
    return presentation.show_home_page(
        search_text='',
        index_name=app.config['index_name'],
        input_files_root=app.config['input_files_root'])


@app.route('/', methods=['POST'])
def my_form_post():
    search_text = request.form['search_text'].lower()

    try:
        last_score = request.form['last_score']
        last_id = request.form['last_id']
        optional_search_after = '"search_after": [%s, "%s"],' % (last_score, last_id)
    except:
        optional_search_after = ''

    body = render_template("search_body.json",
                           query_string=search_text,
                           optional_search_after=optional_search_after)
    print(body)
    search_result = es.search(index=app.config['index_name'], body=body)
    generated_html = presentation.present_results(
        search_text=search_text,
        index_name=app.config['index_name'],
        input_files_root=app.config['input_files_root'],
        list_of_results=search_result['hits']['hits'])

    return generated_html


@app.route('/elastic_offline_search/<path:relative_path>')
def open_file(relative_path):
    return send_from_directory(app.config['input_files_root'], relative_path)



def configure_global_app():
    parsed_args = common.initial_setup()
    app.config['input_files_root'] = parsed_args.path
    app.config['index_name'] = parsed_args.index_name
    print('Files root: %s. Index name: %s', app.config['input_files_root'], app.config['index_name'])
    return


if __name__ == '__main__':
    configure_global_app()
    app.run()