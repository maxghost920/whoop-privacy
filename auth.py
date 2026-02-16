import http.server, urllib.parse, json, urllib.request, sys, webbrowser, secrets
CID='f972e6d6-cc12-44fe-a93b-6d0710ef5a51'
SEC='733ec889e1304499e1cd0e6868b895d2a89bef7ca10d0a57c32663055a7f1a30'
RU='http://localhost:3000/callback'
ST=secrets.token_hex(16)
webbrowser.open(f'https://api.prod.whoop.com/oauth/oauth2/auth?client_id={CID}&redirect_uri={urllib.parse.quote(RU)}&response_type=code&scope={urllib.parse.quote("read:recovery read:sleep read:workout read:cycles read:profile read:body_measurement")}&state={ST}')
print('Waiting for auth callback on port 3000...')
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code=q.get('code',[None])[0]
        if not code:
            self.send_response(400);self.end_headers();self.wfile.write(b'No code');return
        d=urllib.parse.urlencode({'grant_type':'authorization_code','code':code,'redirect_uri':RU,'client_id':CID,'client_secret':SEC}).encode()
        r=urllib.request.urlopen(urllib.request.Request('https://api.prod.whoop.com/oauth/oauth2/token',d,{'Content-Type':'application/x-www-form-urlencoded'}))
        t=json.loads(r.read())
        self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers()
        self.wfile.write(b'<h1>Done! Copy the JSON from your terminal.</h1>')
        print('\n' + json.dumps(t) + '\n')
        import threading;threading.Timer(1,lambda:sys.exit(0)).start()
    def log_message(self,*a):pass
http.server.HTTPServer(('localhost',3000),H).serve_forever()
