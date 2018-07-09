# -*- coding: utf-8 -*-
from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from msbwtsearch import utils

import socket

page = Blueprint('page', __name__, template_folder='templates')


@page.route('/ping')
def ping():
    return 'OK!!!!'



@page.route('/')
def index():
    # POST search_term = request.form.get("search_term")
    # GET  search_term = request.args.get("search_term")
    # BOTH search_term = request.values.get("search_term")

    return render_template('page/index.html')


'''
@page.route('/')
def home():
    print('CALL to /')
    # POST search_term = request.form.get("search_term")
    # GET  search_term = request.args.get("search_term")
    # BOTH search_term = request.values.get("search_term")
    search_term = request.values.get('search_term', '')
    datasetid = request.values.get('datasetid', '')

    print(request.cookies)

    resp = redirect('/')
    resp.set_cookie('search_term', 'NOVAL', expires=0)
    resp.set_cookie('datasetid', 'NOVAL', expires=0)

    if search_term or datasetid:

        for arg in request.args:
            if arg.lower() in ['search_term', 'datasetid']:
                resp.set_cookie('{}'.format(arg), request.args[arg])

        return resp
    else:

        if 'search_term' in request.cookies:
            search_term = request.cookies['search_term']

        if 'datasetid' in request.cookies:
            datasetid = request.cookies['datasetid']

    return render_template('page/index.html',
                           search_term=search_term, datasetid=datasetid)

'''
