import http.server, urllib.parse, json, urllib.request, sys, webbrowser, os

# Read from env vars so secrets never leave your machine
CID = os.environ.get('STRAVA_CLIENT_ID', '')
SEC = os.environ.get('STRAVA_CLIENT_SECRET', '')

if not CID or not SEC:
    print("Set these env vars first:")
    print("  export STRAVA_CLIENT_ID=your_id")
    print("  export STRAVA_CLIENT_SECRET=your_secret")
    sys.exit(1)

RU = 'http://localhost:3000/callback'
SCOPES = 'read,activity:read_all'

webbrowser.open(f'https://www.strava.com/oauth/authorize?client_id={CID}&redirect_uri={urllib.parse.quote(RU)}&response_type=code&scope={SCOPES}')
print('Waiting for auth callback on port 3000...')

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code = q.get('code', [None])[0]
        if not code:
            err = q.get('error', ['unknown'])[0]
            print(f'ERROR: {err}')
            self.send_response(400); self.end_headers(); self.wfile.write(f'Error: {err}'.encode())
            return
        print('Got auth code, exchanging for tokens...')
        d = urllib.parse.urlencode({
            'client_id': CID,
            'client_secret': SEC,
            'code': code,
            'grant_type': 'authorization_code',
        }).encode()
        req = urllib.request.Request('https://www.strava.com/oauth/token', d, {
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        try:
            r = urllib.request.urlopen(req)
            t = json.loads(r.read())
            self.send_response(200); self.send_header('Content-Type', 'text/html'); self.end_headers()
            self.wfile.write(b'<h1>Done! Copy the JSON from your terminal.</h1>')
            # Strip athlete info, only show tokens
            token_data = {k: t[k] for k in ['access_token', 'refresh_token', 'expires_at', 'expires_in', 'token_type'] if k in t}
            print('\n=== PASTE THIS INTO DISCORD ===')
            print(json.dumps(token_data))
            print('=== END ===\n')
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f'\nFailed: {body}\n')
            self.send_response(500); self.end_headers(); self.wfile.write(f'Failed: {body}'.encode())
        import threading; threading.Timer(1, lambda: sys.exit(0)).start()
    def log_message(self, *a): pass

http.server.HTTPServer(('localhost', 3000), H).serve_forever()
