# Server for interacting with Skeleton through HTTP requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, ParseResult
import json
import Skeleton
from Skeleton import trackList
import os
from dotenv import load_dotenv
import random
import string
import requests
from base64 import b64encode
import json

def convert_json_to_trackList(json_trackList) -> trackList | None:
    parsed = json.loads(json_trackList)
    if 'tracks' not in parsed:
        return None
    
    tracks: trackList = []
    for t in parsed['tracks']:
        tracks.append( (t['title'], t['artist']) )

    return tracks

class WebRequestHandler(BaseHTTPRequestHandler):
    # Routes
    # "/"
    def GET_root(self):
        state = random.choices(string.ascii_letters + string.digits, k=16) # Random string for code state
        state = ''.join(state)
        scope = 'playlist-read-private playlist-modify-private playlist-modify-public'

        querystring = f'https://accounts.spotify.com/authorize?client_id={os.environ['CLIENT_ID']}&response_type=code&redirect_uri={os.environ['REDIRECT_URI']}&state={state}&scope={scope.replace(' ', '+')}'
        print(querystring)
        os.environ['CLIENT_SECRET']
        os.environ['REDIRECT_URI']

        self.send_response(302)
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:5173')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.send_header('Location', querystring)
        self.end_headers()
        return
    
    def GET_authorize(self, url: ParseResult):
        query = url.query
        code = query[(query.index("=") + 1):]
        credentials = f"{os.environ['CLIENT_ID']}:{os.environ['CLIENT_SECRET']}"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            'Authorization': 'Basic ' + b64encode(credentials.encode()).decode()
        }
        response = requests.post(f"https://accounts.spotify.com/api/token", headers=headers, data={
            "code": code,
            "redirect_uri": os.environ["REDIRECT_URI"],
            "grant_type": "authorization_code"
        })
        self.send_response(response.status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "http://localhost:5173")
        self.end_headers()
        self.wfile.write(response.text.encode('utf-8'))
        return

    def GET_samples(self, url: ParseResult):
        query = url.query
        playlist_id = query[(query.index("=") + 1):]
        auth_token = self.headers["Authorization"]
        print(auth_token)
        skeleton = Skeleton.Skeleton(auth_token=auth_token, auth_flow='auth', running_locally=False)
        created_playlist_uri = skeleton.make_sample_playlist(playlist_url=playlist_id)
        print(created_playlist_uri)
        response = json.dumps({"playlist_uri": created_playlist_uri})
        print(response)
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "http://localhost:5173")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
        return

    # Util
    def url(self):
        return urlparse(self.path)
    
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:5173')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type, Authorization")
        self.end_headers()
    
    def do_GET(self): # Sign in with spotify
        url = self.url()
        match url.path:                
            case "/authorize":
                self.GET_authorize(url)
            case "/samples":
                self.GET_samples(url)
                
        

    # A get request receives a list of songs and sends a list of samples back
    def do_POST(self):
        try:
            req_len = int(self.headers["Content-Length"])
        except:
            # TODO: Send informative request
            self.send_response(404)
            return
        body = self.rfile.read(req_len)
        tracks: trackList | None = convert_json_to_trackList(body)
        print(tracks)
        if trackList == None:
            # Send informative request
            self.send_response(404)
            return
        
        s = Skeleton.Skeleton(auth_flow='client')
        sample_ids: list[str] | None = s.get_sample_ids_from_trackList(tracks)
        if sample_ids == None:
            # Send informative response
            self.send_response(404)
            return
        
        jsoned_ids: str = json.dumps(sample_ids)
        print(jsoned_ids)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "http://localhost:5173")
        self.end_headers()
        self.wfile.write(jsoned_ids.encode('utf-8'))

if __name__ == "__main__":
    # TODO: Let user specify port
    load_dotenv()
    server = HTTPServer(("localhost", 3005), WebRequestHandler)
    print("Serving on port", server.server_port)
    server.serve_forever()
