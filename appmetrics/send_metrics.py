import random
import requests
from time import sleep

from time_execution import settings, time_execution
from time_execution.backends.elasticsearch import ElasticsearchBackend
from time_execution.backends.threaded import ThreadedBackend
from time_execution.decorator import write_metric


# import logging
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# # create file handler which logs even debug messages
# fh = logging.FileHandler('spam.log')
# fh.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
# logger.addHandler(fh)


# HOOKS
# def status_code_hook(response, exception, metric, func_args, func_kwargs):
#     if response:
#         status_code = getattr(response, 'status_code', None)
#     elif exception:
#         status_code = getattr(exception, 'status_code', None)
#     if not status_code:
#         return None
#     return {'status_code': status_code, 'code': status_code}


def status_code_hook(response, exception, metric, func_args, func_kwargs):
    status_code = getattr(response, 'status_code', None)
    if not status_code and hasattr(exception, 'response'):
        status_code = getattr(exception.response, 'status_code', None)
    if status_code:
        return dict(
            name='{}.{}'.format(metric['name'], status_code),
            # my_extra_filed_name='myvalue123'
        )


def configure_metrics():
    # Check feature flag
    #if not settings.METRICS_ENABLED:
    #    return

    if False:
        elasticsearch = ElasticsearchBackend('localhost', index='metrics')
        settings.configure(backends=[elasticsearch])

    if True:
        metrics_backends = []
        async_es_metrics = ThreadedBackend(
            ElasticsearchBackend,
            backend_kwargs={
                'host': 'localhost',
                'port': '9200',
                #'url_prefix': settings.ELASTICSEARCH_PREFIX,
                #'use_ssl': settings.ELASTICSEARCH_SSL,
                #'verify_certs': settings.ELASTICSEARCH_VERIFY_CERTS,
                #'index': settings.ELASTICSEARCH_INDEX,
                #'http_auth': settings.ELASTICSEARCH_AUTH,
            },
        )
        metrics_backends.append(async_es_metrics)
        settings.configure(
            backends=metrics_backends,
            hooks=[
                status_code_hook,
            ],
            origin='inspire_next'
        )


configure_metrics()
# Wait for the configuration to be fully loaded.
sleep(1)


# Wrap the methods where u want the metrics
@time_execution
def ping_google():
    status_code = random.choice([200, 200, 200, 200, 401, 403, 404, 500])
    response = requests.get('http://httpstat.us/{}'.format(status_code))
    response.raise_for_status()
    print response
    return response


ping_google()
# write_metric('__main__.ping_google', origin='inspire_next', hostname='macnim', value=1004.0)

