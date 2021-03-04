mport copy
import json
import threading

import requests
from six import PY3

from datadog_checks.base import ensure_bytes
from datadog_checks.scadadog import ScadadogCheck

if PY3:
    from http.server import BaseHTTPRequestHandler, HTTPServer
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


HTTP = None
INSTANCE = {'username': 'admin', 'password': 'admin', 'tags': ['test1']}

def setup_module(module):
    global HTTP
    HTTP = HttpServerThread()
    HTTP.start()
    INSTANCE['scadadog_url'] = 'http://localhost:{}'.format(HTTP.port)

def teardown_module(module):
    try:
        HTTP.end_http()
        HTTP.join()
    except requests.exceptions.ConnectionError:
        # The server is already down
        pass

def test_check_all_metrics(aggregator):
    """
    Testing Scadadog check.
    """
    check = ScadadogCheck('scadadog', {}, {})
    check.check(copy.deepcopy(INSTANCE))
    tags = copy.deepcopy(INSTANCE['tags'])
    tags.append("scadadog_url:http://localhost:%d" % HTTP.port)
    for metric_key in CHANNEL_DATA:
        metric_name = "scadadog.%s" % metric_key
        metric_val = CHANNEL_DATA[metric_key]
        aggregator.assert_metric(metric_name, count=1, value=metric_val, tags=tags)
    aggregator.assert_all_metrics_covered

class HttpServerThread(threading.Thread):
    def __init__(self):
        super(HttpServerThread, self).__init__()
        self.done = False
        self.hostname = 'localhost'

        class MockScadadog(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/config/v1/project/channels':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    # json.dumps always outputs a str, wfile.write requires bytes
                    self.wfile.write(ensure_bytes(json.dumps(CHANNEL_DATA)))
                else:
                    self.send_response(404)
                    return

        self.http = HTTPServer((self.hostname, 0), MockScadadog)
        self.port = self.http.server_port

    def run(self):
        while not self.done:
            self.http.handle_request()

    def end_http(self):
        self.done = True
        # just a dummy get to wake it up
        requests.get("http://%s:%d" % (self.hostname, self.port))


CHANNEL_DATA = {
    "PROJECT_ID": 3552893928,
    "common.ALLTYPES_NAME": "Data Type Examples",
    "common.ALLTYPES_DESCRIPTION": "Example Simulator Channel",
    "servermain.MULTIPLE_TYPES_DEVICE_DRIVER": "Simulator",
    "servermain.CHANNEL_DIAGNOSTICS_CAPTURE": false,
    "servermain.CHANNEL_UNIQUE_ID": 3467605889,
    "servermain.CHANNEL_STATIC_TAG_COUNT": 216,
    "servermain.CHANNEL_WRITE_OPTIMIZATIONS_METHOD": 2,
    "servermain.CHANNEL_WRITE_OPTIMIZATIONS_DUTY_CYCLE": 10,
    "servermain.CHANNEL_NON_NORMALIZED_FLOATING_POINT_HANDLING": 0,
    "simulator.CHANNEL_ITEM_PERSISTENCE": false,
    "simulator.CHANNEL_ITEM_PERSISTENCE_DATA_FILE": "C:\\ProgramData\\Kepware\\KEPServerEX\\V6\\Simulator\\Data Type Examples.dat"
}

# https://<hostname_or_ip>:<port>/config/v1/event_log
# https://<hostname_or_ip>:<port>/config/v1/event_log?limit=10&start=2016-01-01T00:00:00.000&end=2016-01-02T20:00:00.000
# Limit = Maximum number of log entries to return. The default setting is 100 entries. 
# Start = Earliest time to be returned in YYYY-MM-DDTHH:mm:ss.sss (UTC) format. 
# End = Latest time to be returned in YYYY-MM-DDTHH:mm:ss.sss (UTC) format. 

