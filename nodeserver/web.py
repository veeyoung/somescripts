#!/usr/bin/env python
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socket, base64
import time
import cgi

host = ('0.0.0.0', 9933)

class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        tokens = None
        with open('tokens.txt', 'r') as f:
            tokens = f.read().splitlines()
        if query.get('token', [''])[0] in tokens:
            self.send_response(200)
            if urlparse(self.path).path == "/upload":
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                with open('./upload.html', 'r', encoding="utf-8") as f:
                    nodeContent = f.read()
                    http_response = nodeContent.encode('utf-8')
                    self.wfile.write(http_response)
            else:
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()
                with open('/dev/shm/config.yaml', 'r', encoding="utf-8") as f:
                    nodeContent = f.read()
                    http_response = nodeContent.encode('utf-8')
                    self.wfile.write(http_response)
        else:
            self.send_response(401)
            self.wfile.write(b'token error')

    def do_POST(self):
        query = parse_qs(urlparse(self.path).query)
        tokens = None
        with open('tokens.txt', 'r') as f:
            tokens = f.read().splitlines()

        if query.get('token', [''])[0] not in tokens:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'Unauthorized')
            return

        content_type, params = cgi.parse_header(self.headers['Content-Type'])
        if content_type != 'multipart/form-data':
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid Content-Type. Expecting multipart/form-data.')
            return

        try:
            form_data = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']}
            )
        except Exception as e:
            print(f"Error parsing form data: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Error parsing form data.')
            return

        file_items = form_data.getlist('file')
        for file_item in file_items:
            file_data = None
            if type(file_item) is not bytes:
                file_data = file_item.file.read()
                print(len(file_data))
            else:
                file_data = file_item
            with open('./nodes.txt', 'wb') as file:
                file.write(file_data)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'File uploaded successfully.')

        print("Update completed.")


if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
