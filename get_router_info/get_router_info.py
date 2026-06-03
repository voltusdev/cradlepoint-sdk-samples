"""get_router_info - Generic cp.get() HTTP proxy.

Passes any HTTP GET request path directly to cp.get() and returns the result
as JSON. Networked clients can query arbitrary router state/config paths.

Usage:
  GET /status/wan/devices
  GET /config/routing/rules
  GET /status/ecm

Access via Remote Connect LAN Manager on 127.0.0.1:8001,
or forward LAN zone to ROUTER zone for local access.
"""

import cp
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

DEFAULT_PORT = 8001


class CpGetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.path.lstrip('/')

        if not path:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'no path provided',
                'usage': 'GET /<cp_path> e.g. GET /status/wan/devices'
            }).encode())
            return

        result = cp.get(path)

        if result is None:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'path returned None',
                'path': path
            }).encode())
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, indent=2).encode())

    def log_message(self, format, *args):
        cp.log(f'HTTP {args[0]}')


def main():
    port = DEFAULT_PORT
    appdata_port = cp.get_appdata('get_router_info_port')
    if appdata_port:
        try:
            port = int(appdata_port)
        except (ValueError, TypeError):
            cp.log(f'Invalid get_router_info_port appdata value "{appdata_port}", using default {DEFAULT_PORT}')
            port = DEFAULT_PORT

    cp.log(f'Starting get_router_info on port {port}')
    server = HTTPServer(('', port), CpGetHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        cp.log('Stopping get_router_info server')


if __name__ == '__main__':
    main()
