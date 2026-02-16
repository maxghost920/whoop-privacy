#!/bin/bash
# Run this on your LOCAL machine (Mac).
# It starts a temporary server, opens the Whoop auth page,
# captures the token, and prints it for you to paste back.

CLIENT_ID="f972e6d6-cc12-44fe-a93b-6d0710ef5a51"
CLIENT_SECRET="733ec889e1304499e1cd0e6868b895d2a89bef7ca10d0a57c32663055a7f1a30"
REDIRECT_URI="http://localhost:3000/callback"
STATE=$(openssl rand -hex 16)
SCOPES="read:recovery read:sleep read:workout read:cycles read:profile read:body_measurement"

AUTH_URL="https://api.prod.whoop.com/oauth/oauth2/auth?client_id=${CLIENT_ID}&redirect_uri=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${REDIRECT_URI}'))")&response_type=code&scope=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${SCOPES}'))")&state=${STATE}"

echo "Opening browser..."
open "$AUTH_URL" 2>/dev/null || xdg-open "$AUTH_URL" 2>/dev/null || echo "Open this URL: $AUTH_URL"

echo "Waiting for callback on port 3000..."

# Simple Python HTTP server to catch the callback
python3 -c "
import http.server, urllib.parse, json, sys

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code = query.get('code', [None])[0]
        if not code:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'No code received. Check for errors.')
            print('ERROR: No code received. Query:', query)
            return

        # Exchange code for tokens
        import urllib.request
        data = urllib.parse.urlencode({
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': '${REDIRECT_URI}',
            'client_id': '${CLIENT_ID}',
            'client_secret': '${CLIENT_SECRET}',
        }).encode()
        req = urllib.request.Request('https://api.prod.whoop.com/oauth/oauth2/token', data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        resp = urllib.request.urlopen(req)
        tokens = json.loads(resp.read())

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Authorized! Copy the tokens from terminal.</h1>')

        print()
        print('=== TOKENS (copy everything between the lines) ===')
        print(json.dumps(tokens))
        print('=== END TOKENS ===')
        print()
        print('Paste the JSON line above back to your health agent in Discord.')

        import threading
        threading.Timer(1, lambda: sys.exit(0)).start()

    def log_message(self, *a): pass

http.server.HTTPServer(('localhost', 3000), Handler).serve_forever()
"
