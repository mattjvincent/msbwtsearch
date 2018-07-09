from flask import (
    Blueprint,
    redirect,
    jsonify,
    request,
    url_for,
    Response,
    render_template)
from datetime import datetime
import time
import requests
from msbwtsearch.utils import format_time
import json
from celery import group, current_app, chord
from celery.result import GroupResult
# INSTALL CACHE
#import requests_cache
#requests_cache.install_cache()
import os
import MUSCython.MultiStringBWTCython as MultiStringBWT
from msbwtsearch import utils

api = Blueprint('api', __name__, template_folder='templates', url_prefix='/api')


def split_url(url):
    """Splits the given URL into a tuple of (protocol, host, uri)"""
    proto, rest = url.split(':', 1)
    rest = rest[2:].split('/', 1)
    host, uri = (rest[0], rest[1]) if len(rest) == 2 else (rest[0], "")
    return proto, host, uri


def parse_url(url):
    """Parses out Referer info indicating the request is from a previously proxied page.
    For example, if:
        Referer: http://localhost:8080/proxy/google.com/search?q=foo
    then the result is:
        ("google.com", "search?q=foo")
    """

    proto, host, uri = split_url(url)

    print('url=', url)
    print('proto=', proto)
    print('host=', host)
    print('uri=', uri)

    if uri.find("/") < 0:
        return None

    rest = uri.split("/", 2)[2]

    return {'proto': proto, 'host': host, 'uri': uri, 'url': rest}


class Cache:
    def __init__(self):
        self.urls = {}


CACHE = Cache()


@api.route('/search', methods=['GET'])
def api_search():
    sequence = str(request.values['sequence'])
    sample = str(request.values['sample'])
    count = 0

    print('submit called with: {} ... {}'.format(sequence, sample))

    bwt_dir = os.environ.get('BWT_DIR', None)
    sample_dir = os.path.join(bwt_dir, sample)
    print('sample_dir=', sample_dir)


    msbwt = MultiStringBWT.loadBWT(sample_dir)

    print('msbwt=', msbwt)
    count = msbwt.countOccurrencesOfSeq(sequence)

    return jsonify({
        'sequence': str(sequence),
        'sample': str(sample),
        'count': count,
    })


@api.route('/searchall', methods=['GET'])
def api_searchall():
    from msbwtsearch.modules.api.tasks import call_api
    sequence = request.values['sequence']
    print('searchall called with: ', sequence)

    bwt_dir = os.environ.get('BWT_DIR', None)
    calls = []
    for dir in utils.get_dirs_in_dir(bwt_dir):
        sample = dir.split('/')[-1]
        calls.append(call_api.s(sample, sequence))

    # create a group
    # class 'celery.canvas.group'
    job = group(calls)

    # call it
    # class 'celery.result.GroupResult'>
    result = job.apply_async()

    #print('type(job)=', type(job))
    #print('type(result)=', type(result))

    # save the result to get in next request
    result.save()

    #print(result)

    return jsonify({'group_id': result.id})


@api.route('/status/group/<group_id>')
def api_groupstatus(group_id):
    """
    Query Celery for group status based on its taskid for a group

    Celery status can be one of:
    PENDING - Job not yet run or unknown status
    PROGRESS - Job is currently running
    SUCCESS - Job completed successfully
    FAILURE - Job failed
    REVOKED - Job get cancelled
    """
    print('status called for: ', group_id)
    from msbwtsearch.modules.api.tasks import celery
    try:
        # get the GroupResult
        # celery.result.GroupResult
        rs = celery.GroupResult.restore(group_id)
        from msbwtsearch.modules.api.tasks import call_api

        #print('ready()=', rs.ready())
        #print('waiting()=', rs.waiting())
        #print('successful()=', rs.successful())
        #print('failed()=', rs.failed())

        if rs.ready():
            results = rs.get(propagate=False)

            data = {}
            error_count = 0
            for idx, res in enumerate(results):
                if 'error' in res:
                    error_count += 1
                data[res['sample']] = res

            response_data = {
                'task_id': group_id,
                'status': 'DONE',
                'number_tasks_submitted': len(rs.results),
                'number_tasks_completed': rs.completed_count(),
                'number_tasks_errors': error_count,
                'response_data': data
            }

            # delete all the task_ids for this group_id from redis
            rs.forget()

            # group_id still exists, delete it from redis
            rs.delete()

        else:
            response_data = {
                'task_id': group_id,
                'status': 'RUNNING',
                'number_tasks_submitted': len(rs.results),
                'number_tasks_completed': rs.completed_count(),
                'response_data': ''
            }
    except Exception as exc:
        print('Major Error: ', str(exc))
        response_data = {
            'task_id': group_id,
            'status': 'DONE',
            'error': 'UNKNOWN ERROR'
        }

    return jsonify(response_data)


@api.route('/cancel/group/<group_id>')
def api_cancelgroup(group_id):
    """
    Cancel Celery task
    REVOKED - Job gets cancelled
    """
    # TODO: this is now group id and not a single task_id, make sure this works
    rs = current_app.GroupResult.restore(group_id)
    rs.revoke(terminate=True)
    return jsonify({'status': 'revoked?'})


@api.route('/status/task/<task_id>')
def api_status(task_id):
    """
    Query Celery for group status based on its taskid for a group

    Celery status can be one of:
    PENDING - Job not yet run or unknown status
    PROGRESS - Job is currently running
    SUCCESS - Job completed successfully
    FAILURE - Job failed
    REVOKED - Job get cancelled
    """
    print('status called for: ', task_id)
    from msbwtsearch.modules.api.tasks import call_api

    try:
        task = call_api.AsyncResult(task_id)

        if task.state == 'PENDING':
            # job did not start yet
            response = {
                'state': task.state,
            }
        elif task.state != 'FAILURE':
            # print('task.get()=', task.get())
            response = task.info
            response['status'] = 'RUNNING'
            response['state'] = task.state
            if 'results' in task.info:
                response['results'] = task.info['results']
                response['status'] = 'DONE'

            task.forget()
            # task.delete()
        else:
            # something went wrong in the background job
            response = {
                'state': task.state,
                'status': str(task.info),  # this is the exception raised
            }

        return jsonify(response)
    except Exception as exc:
        print('Major Error: ', str(exc))
        response_data = {
            'task_id': task_id,
            'status': 'DONE',
            'error': 'UNKNOWN ERROR'
        }

    return jsonify(response_data)

@api.route('/cancel/task/<task_id>')
def api_cancel(task_id):
    """
    Cancel Celery task
    REVOKED - Job get cancelled
    """
    from msbwtsearch.modules.api.tasks import call_api, celery
    task = call_api.AsyncResult(task_id)
    task.revoke(terminate=True)
    return jsonify({'status': task.state})


