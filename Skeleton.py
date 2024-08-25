# Source code for Skeleton Python module
# Author: Leroy Betterton Gage
# Email: leroylightning at ucla dot edu
import urllib.parse
import aiohttp
import re
from bs4 import BeautifulSoup
import random
import json
import urllib
import logging

# Track name, artist name
type track = tuple[str, str]
# type samples_ds -- -- -- do this later
class Skeleton:
    scraping_headers: dict
    logger: logging.Logger | None
    MAX_RETRIES: int
    def __init__(self, verbose: bool = False):
        self.scraping_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.whosampled.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        }
        self.logger = None
        if verbose:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                "{name} - {levelname}: {message}",
                style="{"
            ))
            self.logger = logging.getLogger(__name__)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)
            self.logger.info("Here we go!")
        self.MAX_RETRIES = 10
        pass
    
    # Given a link, determine if it's a song, album, or playlist
    # Also return resource URI
    def extract_resource_type_and_uri(self, uri: str):
        if self.logger:
            self.logger.info(f"Extracting uri from {uri}")
        p_string = r'.*spotify.com/(?P<resource_type>track|album|playlist)/(?P<id>\w+).*'
        pattern = re.compile(p_string)
        match = pattern.match(uri)
        if not match:
            if self.logger:
                self.logger.error(f"uri didn't match regex. uri: {uri}")
            raise ValueError('Received a uri with bad resource type', uri)
        result_dict = match.groupdict()
        resource_type, id = result_dict['resource_type'], result_dict['id']
        if self.logger:
            self.logger.info(f"Extracted resource type: {resource_type} and id: {id}")
        return (resource_type, id)
        
    def scrub_feature_from_track_title(self, track_name: str) -> str:
        
        feature_pattern = re.compile(r'.*\((feat|with|ft).*', re.IGNORECASE)
        if feature_pattern.match(track_name):
            scrub_pattern = re.compile(r'(?P<scrubbed>.*)\((feat|with|ft).*')
            return scrub_pattern.match(track_name).groupdict()['scrubbed'].strip()
        return track_name

    # Get the tracks from a playlist, album, or single song
    # Returns the track list and resource name
    # TODO: Make this function better...
    async def get_spotify_resource_details(self, resource_id: str,
                                           resource_type: str,
                                           session: aiohttp.ClientSession,
                                           token: str) -> tuple[str, list[track]] | None:
        if self.logger:
            self.logger.info(f"Getting resource name and tracks for {resource_type} with id: {resource_id}")
        get_url = f'https://api.spotify.com/v1/{resource_type}s/{resource_id}'
        headers = {
            "Authorization": 'Bearer ' + token
        }
        for i in range(self.MAX_RETRIES):
            async with session.get(get_url, headers=headers) as res:
                if res.status != 200:
                    if self.logger:
                        self.logger.warning(f"Request {i + 1} for spotify resource failed")
                        if i == self.MAX_RETRIES - 1:
                            self.logger.error(f"Couldn't get resource name and tracks for {resource_type} with id: {resource_id}\n{res}")

                    continue
                data: dict = await res.json()
            resource_name = data["name"]
            tracks = []
            if resource_type == 'track':
                artist_name = data["artists"][0]["name"]
                tracks = [(resource_name, artist_name)]
                # This is ugly...
                trimmed_tracks = [(self.scrub_feature_from_track_title(t[0]), t[1]) for t in tracks]
            else:
                for item in data["tracks"]["items"]:
                    track = item
                    if resource_type == "playlist":
                        track = item["track"]
                    scrubbed_track_name = self.scrub_feature_from_track_title(track["name"])
                    tracks.append( (scrubbed_track_name, track["artists"][0]) )
                    trimmed_tracks = [(t[0], t[1]["name"]) for t in tracks]
            if self.logger:
                self.logger.info(f"Got track list and {resource_type} name. \nTracks: {tracks}")
                
            return resource_name, trimmed_tracks
        return None

    async def get_track_whosampled_page_url(self, track_name: str,
                                            artist_name: str,
                                            session: aiohttp.ClientSession) -> str | None:
        whosampled_search_url: str = 'https://www.whosampled.com/search/tracks'
        get_url: str = f'{whosampled_search_url}/?q={(track_name + ' ' + artist_name).replace(' ', '+')}'
        if self.logger:
            self.logger.info(f"Getting whosampled page for track {track_name} by {artist_name}. \nRequest url: {get_url}")
        for i in range(self.MAX_RETRIES):
            async with session.get(get_url, headers=self.scraping_headers) as res:
                # No retries, for now
                if res.status != 200:
                    self.logger.warning(f"Request {i + 1} failed")
                    if i == self.MAX_RETRIES - 1:
                        self.logger.error(f"Couldn't get whosampled page url for track {track_name} by {artist_name}")
                    continue
                soup = BeautifulSoup(await res.text(), 'html.parser')
                break
        matches = soup.find_all('li', class_='trackEntry')
        found_song_name = None
        found_song_artist = None
        url = None
        for m in matches:
            try:
                found_song_name: str = m.span.a.string
                found_song_artist: str = m.span.span.a.string

                if track_name.lower() in found_song_name.lower().strip() and artist_name.lower() in found_song_artist.lower().strip():
                    url = f'https://whosampled.com{m.span.a.get('href')}' 
                    break

            except AttributeError: # We'll get an attributeerror if we parse too deep
                pass
        if self.logger:
            self.logger.info(f"Got whosampled page url for track {track_name} by {artist_name}: {url}")
        return url

    # If song contains more than 3 samples, we will need to go to a new page
    async def get_whosampled_sample_list(self, song_page_url: str,
                                         session: aiohttp.ClientSession) -> list[track] | None:
        if self.logger:
            self.logger.info(f"Getting sample list for track with whosampled page url: {song_page_url}")
        soup = None
        for i in range(self.MAX_RETRIES):
            async with session.get(song_page_url, headers=self.scraping_headers) as response:
                if response.status != 200:
                    if self.logger:
                        self.logger.warning(f"Sample page request {i + 1} failed")
                    continue
                soup = BeautifulSoup(await response.text(), 'html.parser')
                break
        if not soup:
            if self.logger:
                self.logger.error(f"Couldn't get a response when request whosampled page for song with url {song_page_url} ")
            return None
        header = soup.find('h3', string=re.compile('Contains sample.*'))
        if not header:
            if self.logger:
                self.logger.info(f"Reached whosampled page for song {song_page_url} but it doesn't have any samples")
            return None
        p = re.compile('Contains samples of ([0-9]+) songs?') # Get the number of samples

        try:
            m = p.match(header.string)
            num_samples = int(m.group(1))
        except:
            if self.logger:
                self.logger.error(f"Couldn't determine number of samples for song with url {song_page_url}")
        
        section_container = header.parent.parent

        if num_samples <= 3:
            rows = section_container("tr")
        
        else:
            more_samples_btn = section_container.find("a", class_="btn")
            song_samples_page_link = 'https://www.whosampled.com' + more_samples_btn.get("href")
            if self.logger:
                self.logger.info(f'The song at {song_page_url} has a lot of samples. Getting the samples page')
            for i in range(self.MAX_RETRIES):
                async with session.get(song_samples_page_link, headers=self.scraping_headers) as response:
                    if response.status != 200:
                        if self.logger:
                            self.logger.warning(f"Request {i + 1} for additional sample page failed")
                        if self.logger and i == self.MAX_RETRIES - 1:
                            self.logger.error(f"Couldn't get additional sample page from {song_samples_page_link}")
                            return None
                        continue
                    sample_soup = BeautifulSoup(await response.text(), 'html.parser')
                    break
                # Notice that the 'Contains sample' text is found in an h2 element in the standalone sample page
            header = sample_soup.find('h2', string=re.compile('Contains sample.*'))
            if not header:
                if self.logger:
                    self.logger.info(f"Reached additional whosampled page at {song_samples_page_link} but it doesn't have any samples")
                return None
            
            section_container = header.parent.parent
            rows = section_container.find("tbody")("tr", )

        sample_list = []
        for r in rows:
            song_title_container = r.find("a", class_="trackName")
            song_artist_container = r.find("td", class_="tdata__td3")
            song_title = song_title_container.string
            artist_name = song_artist_container.a.string
            sample_list.append(
                (song_title, artist_name)
            )
        
        return None if len(sample_list) == 0 else sample_list
    
    # Get a random Skeleton-themed name for the new playlist
    def get_random_skeleton_playlist_name(self, original_playlist_name) -> str:
        configurations = lambda n: random.choice(
            [
                f'the skeleton of... {n}',
                f"{n}'s skeleton",
                f"the anatomy of... {n}",
                f'{n}, deconstructed',
                f'all the samples from \"{n}\"'
            ]
        )
        return configurations(original_playlist_name)
    
    # Create a Playlist for the user and return the url as a string
    # Returns playlist_id, final_playlist_uri
    async def create_playlist_for_user(self,
                                       user_id: str,  token: str,
                                       session: aiohttp.ClientSession,
                                       new_playlist_name: str|None=None, 
                                       playlist_description: str|None=None) -> str | None:
        description = playlist_description if playlist_description is not None else "made with Skeleton :)"
        post_url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
        headers = {
            "Authorization": 'Bearer ' + token,
            "Content-Type": "application/json"
        }
        body = json.dumps({
            "name": new_playlist_name,
            "description": description,
            "public": False
        })
        if self.logger:
            self.logger.info(f"Creating a playlist for user {user_id} called {new_playlist_name} with description {description}")
        for i in range(self.MAX_RETRIES):
            async with session.post(post_url, data=body, headers=headers) as res:
                # No troubleshooting
                if res.status != 201:
                    if self.logger:
                        self.logger.warning(f"Attempt {i + 1} to create a playlist failed")
                    if self.logger and i == self.MAX_RETRIES - 1:
                        self.logger.error(f"Couldn't create playlist for user {user_id}")
                    return None
                data = await res.json()
                break
        if 'uri' in data:
            if self.logger:
                self.logger.info(f"created a playlist with name {new_playlist_name} for user {user_id}")
            return data['id'], data['uri']
        return None
    
    # Get the spotify id of a song from its name and artist
    async def get_track_spotify_uri(self, song_name: str,
                                   artist_name: str,
                                   session: aiohttp.ClientSession,
                                   token: str) -> str | None:
        if self.logger:
            self.logger.info(f"getting uri for {song_name} by {artist_name}")
        formatted_query = (f'track:{song_name} artist:{artist_name}')
        req_url = 'https://api.spotify.com/v1/search?type=track&limit=1&q=' + formatted_query
        headers = {
            "Authorization": 'Bearer ' + token,
        }
        if self.logger:
            self.logger.info(f"Getting spotify uri for {song_name} by {artist_name}")
        for i in range(self.MAX_RETRIES):
            async with session.get(req_url, headers=headers) as res:
                if res.status != 200:
                    if self.logger:
                        self.logger.info(f"Request {i + 1} to create a playlist failed")
                    if self.logger and i == self.MAX_RETRIES - 1:
                        self.logger.error(f"Couldn't get uri for {song_name} by {artist_name}")
                        return None
                    continue
                data = await res.json()
                break

        if 'tracks' in data and 'items' in data['tracks'] and len(data['tracks']['items']):
            found_song = data['tracks']['items'][0]
            found_song_name: str = found_song['name']
            found_song_artists: list[str] = [a['name'] for a in found_song['artists']]
            if not (found_song_name.lower() in song_name.lower() or song_name.lower() in found_song_name.lower()):
                return None
            song_artist_match = False
            for a in found_song_artists:
                if artist_name.lower() in a.lower() or a.lower() in artist_name.lower():
                    song_artist_match = True
                    break
            if song_artist_match:
                return found_song['uri']
    
    # Make a playlist containing all the samples from the original supplied playlist
    # Also return a data structure containing each track and the samples for that track
    async def make_sample_playlist(self, resource_uri: str,
                                   session: aiohttp.ClientSession, token: str,
                                   playlist_name: str | None = None, 
                                   user_id: str | None = None,
                                   playlist_description: str | None = None) -> str | None:
        FAILURE_RESPONSE = None, None, None, None
        EMPTY_RESPONSE = None, []#, original resource name
        resource_type, resource_id = self.extract_resource_type_and_uri(resource_uri)
        result = await self.get_spotify_resource_details(resource_id, 
                                                         resource_type,
                                                         session, token)
        if not result:
            return FAILURE_RESPONSE
        resource_name, tracks = result
        new_playlist_name =  self.get_random_skeleton_playlist_name(resource_name)
        if self.logger:
            self.logger.info(f"got all the {resource_type} details out of the way")
        new_song_uris = []
        sample_data_structure: samples_ds = []
        for track_name, artist in tracks:
            ws_page_url: str | None = await self.get_track_whosampled_page_url(track_name=track_name, artist_name=artist, session=session)
            if ws_page_url == None:
                continue
            
            sample_list: list[track] | None = await self.get_whosampled_sample_list(ws_page_url, session=session)
            if self.logger:
                self.logger.info(f"got a sample list for {track_name} by {artist}: {sample_list}")
            if sample_list == None or sample_list == []:
                continue
            ds_key: str = f'{track_name} - {artist}'
            sample_data_structure.append({
                "name": ds_key,
                "song_samples_report": []
            })
            
            for s in sample_list:
                uri = await self.get_track_spotify_uri(song_name=s[0], artist_name=s[1], session=session, token=token)
                if uri is not None:
                    new_song_uris.append(uri)
                
                sample_data_structure[-1]["song_samples_report"].append({
                    "track_name": s[0],
                    "artist": s[1],
                    "uri": uri
                })
        if self.logger:
            self.logger.info("Got all samples")
        if len(new_song_uris) == 0:
            print("no new uris!")
            return None, sample_data_structure, resource_name, new_playlist_name
        if not user_id:
            headers = {
                "Authorization": 'Bearer ' + token,
            }
            self.logger.info("Getting current user's user id")
            for i in range(self.MAX_RETRIES):
                async with session.get('https://api.spotify.com/v1/me', headers=headers) as res:
                    if self.logger and res.status != 200:
                        self.logger.warning(f"Request {i + 1} for user profile failed")
                    if i == self.MAX_RETRIES - 1:
                        if self.logger:
                            self.logger.error("Couldn't get user id of currently signed-in user")
                        return None, sample_data_structure, resource_name, new_playlist_name
                    data = await res.json()
                    user_id = data["id"]
                    break
        playlist_id, playlist_url = await self.create_playlist_for_user(new_playlist_name=new_playlist_name,
                                                                user_id=user_id, 
                                                                playlist_description=playlist_description,
                                                                token=token, session=session)
        headers = {
            "Authorization": 'Bearer ' + token,
        }
        body = {
            "uris": new_song_uris
        }
        put_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        if self.logger:
            self.logger.info(f"adding tracks {body} to playlist {playlist_id}")
        for i in range(self.MAX_RETRIES):
            async with session.put(put_url, headers=headers, json=body) as res:
                if res.status != 200:
                    if self.logger:
                        self.logger.warning(f"Request to add tracks to {playlist_id} failed")
                    if i == self.MAX_RETRIES - 1:
                        if self.logger:
                            self.logger.error(f"Couldn't add songs to playlist {playlist_id}")
                        return FAILURE_RESPONSE
                    continue
        return playlist_url, sample_data_structure, resource_name, new_playlist_name