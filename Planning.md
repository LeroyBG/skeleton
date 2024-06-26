Goal: Want to make this as simple as possible to accomplish its base functionality.
Core functionality should come from a function that takes in a song from Spotify and returns a list of samples, with the understand that that list will be used to add songs to a playlist.

**`Asyncio`**: Should I use the `asyncio` module/approach for this application? Ideally, yes, but I think it would be better to get a baseline working example before getting into anything too fancy.
### Helper Functions
#### `getSamples`
**Arguments:** A representation of a single song (link? name?)
**Return value:** A sample list option (Either a list of samples or nothing).

#### `getSkeleton`
**Argument**: A link to a Spotify playlist.
**Return value:** A Spotify playlist containing all the samples from the original playlist.


## Command Line Tool
I have a command-line tool (almost) working. You put your playlist link into the command line and it makes a playlist full of samples for you. The only problem: I want to make this accessible to people without Python installed (i.e. a web app). Therefore, I'd like to use the current Skeleton functionality as a server with a separate frontend.
Currently, the goal is to modularize Skeleton.py so I can extract all the useful bits.

## TODO
- Make logging optional in Skeleton
- add server-side route for refreshing tokens
- Add ability to analyze albums, individual songs