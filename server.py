# Server for interacting with Skeleton through HTTP requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import Skeleton
from Skeleton import trackList

def convert_json_to_trackList(json_trackList) -> trackList | None:
    parsed = json.loads(json_trackList)
    if 'tracks' not in parsed:
        return None
    
    tracks: trackList = []
    for t in parsed['tracks']:
        tracks.append( (t['title'], t['artist']) )

    return tracks

class WebRequestHandler(BaseHTTPRequestHandler):
    def url(self):
        return urlparse(self.path)
    
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
        
        s = Skeleton.Skeleton('client')
        sample_ids: list[str] | None = s.get_sample_ids_from_trackList(tracks)
        if sample_ids == None:
            # Send informative response
            self.send_response(404)
            return
        
        jsoned_ids: str = json.dumps(sample_ids)
        print(jsoned_ids)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(jsoned_ids.encode('utf-8'))

if __name__ == "__main__":
    # TODO: Let user specify port
    server = HTTPServer(("localhost", 3000), WebRequestHandler)
    server.serve_forever()