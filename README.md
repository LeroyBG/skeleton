Skeleton
--------------
**Skeleton** is a multi-use tool for grabbing all the samples from the songs in a Spotify playlist.
Skeleton can be run as a command line Python script or a frontend web component with a separate HTTP server that does the computation.
#### Requisites
1. Python3 installed
2. Modules listed in [requirements.txt](requirements.txt) installed. (Use a [Virtual Environment](https://realpython.com/python-virtual-environments-a-primer/#how-can-you-work-with-a-python-virtual-environment) to store dependencies)
3. A configured Spotify for Developers app ([instructions](https://developer.spotify.com/documentation/web-api/tutorials/getting-started#create-an-app)).
### Usage
#### Environment Configuration
1. Duplicate the `.env.example`  file in the same directory, replace the example text with your Spotify project details, and rename the file to `.env`.
2. For usage-specific instructions:
	- [Command Line](####As A Command Line Tool)
	- [Server, Frontend Component](####Server, Frontend Component)
#### As A Command Line Tool
Ideal if you are familiar with Python and only want to use Skeleton on your local machine (i.e., you don't want to embed it into a website).

Usage is very simple. Just supply a playlist uri (found through the "Share Playlist" option in the Spotify web, desktop, or mobile app).
*Note:* You can only analyze public playlists or playlists you created.

**Basic Usage**
```zsh
$ script.py PLAYLIST_URL
```

**Custom Playlist Name, Description**:
Supply arguments to the `--name` and `--description` arguments to supply the generated playlist's name and description. The can be changed any time in Spotify.

Run the script:
```zsh
$ python3 script.py PLAYLIST_URL --name "backbone" --description "the songs that make my favorite songs"
```
#### Server, Frontend Component
**Additional Requisites**
- `node.js` and `npm` installed ([instructions](https://nodejs.org/en))

##### Frontend Initialization
The frontend can be used as a standalone site/app or incorporated into another SvelteKit app. The standalone app is useful if you'd like to test Skeleton before incorporating it into your project.

**Standalone App**
In `App.svelte`, replace the value of `SKELETON_SERVER_URL`, `SKELETON_CLIENT_ID`, and `SKELETON_REDIRECT_URI` variables with your Spotify Web API details.

Install dependencies (only necessary before first run or if you modify dependencies):
```zsh
$ npm i
```

Run the app:
```zsh
$ npm run dev
```

##### Backend Initialization
Make sure the `PORT` and `FRONTEND_URL` environment variables in the `.env` file found the project root are set appropriately. The frontend url is just the base url of the site skeleton is running from, usually `http://localhost:5173`.

Start the server:
```zsh
$ python3 server.py
```
This should output "Serving on port \[your server port]\".