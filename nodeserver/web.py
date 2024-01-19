#!/usr/bin/env python
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socket, base64

host = ('0.0.0.0', 9933)

class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        tokens = None
        with open('tokens.txt', 'r') as f:
            tokens = f.read().splitlines()
        if query.get('token', [''])[0] in tokens:
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            with open('./config.yaml', 'r', encoding="utf-8") as f:
                nodeContent = f.read()
                http_response = nodeContent.encode('utf-8')
                self.wfile.write(http_response)
        else:
            self.send_response(401)
            self.wfile.write(b'token error')
if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
