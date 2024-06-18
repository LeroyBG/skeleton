# Skeleton source
# Source code for Skeleton Python module
# Author: Leroy Betterton Gage
# Email: leroylightning at ucla dot edu

import requests.adapters
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from dotenv import load_dotenv
from os import environ
import requests
from bs4 import BeautifulSoup
import re
import random

type trackList = list[tuple[str, str]]
# Tuple containing a tracklist, user_id, and original playlist name
type spotify_playlist_details = tuple[trackList, str, str]
class Skeleton:
    # Properties:
    session: requests.Session | None = None
    configured_spotipy: spotipy.Spotify | None = None

    # Configure request session thingy
    def session_init(self) -> requests.Session:
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=10)
        s.mount('https://', a)
        s.mount('http://', a)
        s.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.whosampled.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        }
        return s
    
    # Configure spotipy
    def spotipy_init(self):
        # Load environment variables from .env file
        load_dotenv()
        scope = 'playlist-modify-private' # So we can generate a new playlist in user's library
        sp: spotipy.Spotify = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=environ["CLIENT_ID"],
                client_secret=environ["CLIENT_SECRET"],
                redirect_uri=environ["REDIRECT_URI"],
                scope=scope
                )
            )
        return sp
    
    # Initialize properties
    # Mutates: self.session, self.configured_spotipy
    def __init__(self) -> None:
        self.session = self.session_init()
        self.configured_spotipy = self.spotipy_init()
    

    # Get the tracks from a public playlist
    # Returns a list of (song_name, artist_name) tuples if successful, otherwise none
    def get_playlist_details(self, playlist_url: str) -> spotify_playlist_details | None:
        # Parse playlist link
        # Note: If the structure of a 'Share Playlist' link changes, this parsing will break
        try:
            before_id: str = '/playlist/'
            offset: int = len(before_id)
            start_ind: int = playlist_url.index('/playlist/') + offset
            end_ind = playlist_url.index('?')
            id: str = playlist_url[start_ind:end_ind]
        except ValueError:
            return None
        
        # Limit is a huge number for now
        # TODO: Increase limit
        result: dict = self.configured_spotipy.playlist(id, additional_types="track")
        if 'tracks' in result and 'items' in result['tracks']:
            songs: list[dict] = result['tracks']['items']
        # We can safely assume these properties are in the dict as well
        user_id = result['owner']['id']
        original_playlist_name = result['name']
        title_and_artist = []
        for s in songs:
            track: dict = s["track"]
            name: str = track["name"]
            primary_artist: str = track["artists"][0]["name"]
            title_and_artist.append( (name, primary_artist) )
        return title_and_artist, user_id, original_playlist_name


    # Get the whosampled page for your song, if it exists
    # Three possible results
    # 1. No page for your song
    # 2. Page for your song, but it doesn't contain samples
    # 3. Page for your song and it contains samples
    def get_whosampled_page_url(self, song_name: str, artist_name: str) -> str | None:
        # Note: very reliant on whosampled query url structure. 
        # If it changes, this app will break
        whosampled_search_url: str = 'https://www.whosampled.com/search/tracks'
        query_str: str = f'{whosampled_search_url}/?q={(song_name + '%20' + artist_name).replace(' ', '%20')}'
        response = self.session.get(query_str)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        matches = soup.find_all('li', class_='trackEntry')

        found_song_name = None
        found_song_artist = None
        url = None
        for m in matches:
            try:
                found_song_name: str = m.span.a.string
                found_song_artist: str = m.span.span.a.string

                if song_name.lower() in found_song_name.lower().strip() and artist_name.lower() in found_song_artist.lower().strip():
                    url = f'https://whosampled.com{m.span.a.get('href')}' 
                    break

            except AttributeError: # We'll get an attributeerror if we parse too deep
                pass
        
        return url

    # If song contains more than 3 samples, we will need to go to a new page
    def get_whosampled_sample_list(self, song_page_url: str) -> trackList | None:
        response = self.session.get(song_page_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        header = soup.find('h3', string=re.compile('Contains sample.*'))
        if not header:
            return None
        p = re.compile('Contains samples of ([0-9]+) songs?') # Get the number of samples

        try:
            m = p.match(header.string)
            num_samples = int(m.group(1))
        except:
            print("Couldn't determine number of samples")
        
        section_container = header.parent.parent

        if num_samples <= 3:
            rows = section_container("tr")
        
        else:
            more_samples_btn = section_container.find("a", class_="btn")
            song_samples_page_link = 'https://www.whosampled.com' + more_samples_btn.get("href")
            print('This song has a lot of samples. Getting the samples page')
            response = self.session.get(song_samples_page_link)

            sample_soup = BeautifulSoup(response.text, 'html.parser')
            # Notice that the 'Contains sample' text is found in an h2 element in the standalone sample page
            header = sample_soup.find('h2', string=re.compile('Contains sample.*'))
            if not header:
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
        return random.choice(configurations)(original_playlist_name)
    
    # Create a Playlist for the user and return the url as a string
    # Returns playlist_id, final_playlist_uri
    def create_playlist_for_user(self, original_playlist_name: str, 
                                user_id: str, playlist_name:str|None=None, 
                                playlist_description:str|None=None) -> str | None:
             
        new_playlist_name =  playlist_name if playlist_name is not None else self.get_random_skeleton_playlist_name(original_playlist_name)
        description = playlist_description if playlist_description is not None else "generated with Skeleton :)"

        response = self.configured_spotipy.user_playlist_create(user_id, name=new_playlist_name, public=False, description=description)

        if 'uri' in response:
            return response['id'], response['uri']
        
        return None

    # Get the spotify id of a song from its name and artist
    def get_song_spotify_id(self, song_name: str, artist_name: str) -> str | None:
        query_str = f'track:{song_name} artist:{artist_name}'
        response: dict = self.configured_spotipy.search(q=query_str, limit=1, type='track')

        if 'tracks' in response and 'items' in response['tracks'] and len(response['tracks']['items']):
            found_song = response['tracks']['items'][0]
            found_song_name: str = found_song['name']
            found_song_artists: list[str] = [a['name'] for a in found_song['artists']]
            song_name_match = found_song_name.lower() in song_name.lower() or song_name.lower() in found_song_name.lower()
            song_artist_match = False
            for a in found_song_artists:
                if artist_name.lower() in a.lower() or a.lower() in artist_name.lower():
                    song_artist_match = True
                    break
            if song_name_match and song_artist_match:
                return found_song['id']
    
    # Make a new playlist with all the samples from the old one
    # Return the new playlist's url (or None if failure)
    def make_sample_playlist(self, playlist_url: str, playlist_name:str|None=None, playlist_description:str|None=None) -> str | None:
        details = self.get_playlist_details(playlist_url)
        if not details:
            return None
        tracks, user_id, original_playlist_name = details
        new_song_ids = []
        for t in tracks:
            print(f"Current track: {t[0]} by {t[1]}")
            ws_page_url: str | None = self.get_whosampled_page_url(song_name=t[0], artist_name=t[1])
            print(f"{t[0]}'s whosampled page url: {ws_page_url}")
            if ws_page_url == None:
                continue
            
            sample_list: trackList | None = self.get_whosampled_sample_list(ws_page_url)
            if sample_list == None:
                continue
            
            for s in sample_list:
                id = self.get_song_spotify_id(song_name=s[0], artist_name=s[1])
                if id is not None:
                    new_song_ids.append(id)
        
        if len(new_song_ids) > 0:
            playlist_id, playlist_url = self.create_playlist_for_user(original_playlist_name=original_playlist_name,
                                                                    user_id=user_id, 
                                                                    playlist_name=playlist_name, 
                                                                    playlist_description=playlist_description)
            
            self.configured_spotipy.playlist_add_items(playlist_id=playlist_id, items=new_song_ids)

            return playlist_url
        else:
            return None