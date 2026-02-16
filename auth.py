import http.server, urllib.parse, json, urllib.request, sys, webbrowser, secrets
CID='f972e6d6-cc12-44fe-a93b-6d0710ef5a51'
SEC='733ec889e1304499e1cd0e6868b895d2a89bef7ca10d0a57c32663055a7f1a30'
RU='http://localhost:3000/callback'
ST=secrets.token_hex(16)
SCOPES='offline read:recovery read:sleep read:workout read:cycles read:profile read:body_measurement'
webbrowser.open(f'https://api.prod.whoop.com/oauth/oauth2/auth?client_id={CID}&redirect_uri={urllib.parse.quote(RU)}&response_type=code&scope={urllib.parse.quote(SCOPES)}&state={ST}')
print('Waiting for auth callback on port 3000...')
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code=q.get('code',[None])[0]
        if not code:
            err=q.get('error',['unknown'])[0]
            desc=q.get('error_description',[''])[0]
            print(f'ERROR: {err} - {desc}')
            self.send_response(400);self.end_headers();self.wfile.write(f'Error: {err}'.encode())
            return
        print(f'Got auth code, exchanging for tokens...')
        d=urllib.parse.urlencode({
            'grant_type':'authorization_code',
            'code':code,
            'redirect_uri':RU,
            'client_id':CID,
            'client_secret':SEC,
        }).encode()
        req=urllib.request.Request('https://api.prod.whoop.com/oauth/oauth2/token',d,{
            'Content-Type':'application/x-www-form-urlencoded',
            'User-Agent':'WhoopSync/1.0',
        })
        try:
            r=urllib.request.urlopen(req)
            t=json.loads(r.read())
            self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers()
            self.wfile.write(b'<h1>Done! Copy the JSON from your terminal.</h1>')
            print('\n=== PASTE THIS INTO DISCORD ===')
            print(json.dumps(t))
            print('=== END ===\n')
        except urllib.error.HTTPError as e:
            body=e.read().decode()
            print(f'\nFailed: {body}\n')
            self.send_response(500);self.end_headers();self.wfile.write(f'Failed: {body}'.encode())
        import threading;threading.Timer(1,lambda:sys.exit(0)).start()
    def log_message(self,*a):pass
http.server.HTTPServer(('localhost',3000),H).serve_forever()
