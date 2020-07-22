from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import json
from gh_actions_client import get_gh_actions_client

# KubeMlOpsBot receives callback requests from the KFP pipeline and
# sends an event to the orchestrator (GitHub in this implementation)
# It knows how to build an event message and knows how to communicate
# with the orchestrator. Potentially it may gather additional information
# for the event payload. Currently it sends the payload as comes from KFP.

# TODO: Authenticate as Git Hub App

PORT = 8080


class KubeMlOpsBotRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        print(body.decode())
        payload = json.loads(body)
        get_gh_actions_client().send_dispatch_event(
            payload['event_type'], payload)
        self.send_response(200)
        self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


httpd = ThreadedHTTPServer(('', PORT), KubeMlOpsBotRequestHandler)
httpd.serve_forever()
