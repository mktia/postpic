# -*- coding: utf-8 -*-
import json
import os
from flask import Flask, render_template, request, make_response, Response, redirect, url_for
from InstagramAPI import InstagramAPI
from werkzeug.utils import secure_filename

app = Flask(__name__)

basic_information = {
    'name': 'Postpic for Instagram',
    'url': 'https://post-pic.herokuapp.com',
    'language_list': [
        {'code': 'ja', 'language': '日本語', 'locale': 'ja_JP'},
        {'code': 'en', 'language': 'English', 'locale': 'en_US'}
    ]
}


def return_html(html_file='index.html', lang='ja'):
    with open('static/' + lang + '.json', encoding='utf-8') as f:
        contents = json.load(f)

    # Attention: If we get the language code from cookie, the user cannot change it manually.
    response = make_response(render_template(
        html_file,
        info=basic_information,
        contents=contents,
        lang=lang,
    ))
    response.set_cookie('language', value=lang)
    return response


@app.route('/')
def index():
    """Japanese"""
    return return_html()


@app.route('/en')
def index_en():
    """English"""
    return return_html(lang='en')


@app.route('/post', methods=['GET', 'POST'])
def post_img():
    # Set username and password
    __USERNAME = request.form['username']
    __PASSWORD = request.form['password']

    api = InstagramAPI(__USERNAME, __PASSWORD)
    api.setUser(__USERNAME, __PASSWORD)

    # Get the language code from cookie
    lang = request.cookies.get('language', None)

    if not api.login():
        print('Failed to login.')
        return redirect(url_for('error', r='login'))

    img = request.files['img']
    if img.filename == '':
        print('No selected file.')
        return redirect(url_for('error', r='no_selected'))

    filename = secure_filename(img.filename)

    if not os.path.isdir('tmp'):
        os.mkdir('tmp')
    path = os.path.join('tmp', filename)

    img.save(path)

    api.uploadPhoto(path, caption=request.form['caption'])

    return return_html('result.html', lang=lang)

@app.route('/error')
def error():
    # Get the language code from cookie
    lang = request.cookies.get('language', None)

    # Why this application occurs an error
    reason = request.args.get('r')

    if reason == 'login':
        return return_html('login_error.html', lang=lang)
    elif reason == 'no_selected':
        return return_html('no_selected.html', lang=lang)
    else:
        return redirect(url_for('/'))

if __name__ == '__main__':
    app.run()
