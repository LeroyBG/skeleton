# Script for interacting with Skeleton through the command line
# Author: Leroy Betterton Gage
# Email: leroylightning at ucla dot edu

import Skeleton
import argparse
            
def get_playlist_details() -> str | None: 
        parser: argparse.ArgumentParser = argparse.ArgumentParser(
            description="A command-line tool for finding the samples from your favorite songs",
            )

        parser.add_argument("PLAYLIST_URL", action="store", help="Link to existing Spotify playlist")
        parser.add_argument("--name", "-n", action="store")
        parser.add_argument("--description", "-d", action="store")
        args: argparse.Namespace = parser.parse_args()
        print(args)
        return args.PLAYLIST_URL, args.new_playlist_name, args.new_playlist_description

if __name__ == '__main__':
    url, new_playlist_name, description = get_playlist_details()
    s = Skeleton.Skeleton()
    final_url = s.make_sample_playlist(playlist_url=url, playlist_name=new_playlist_name, playlist_description=description)
    if not final_url:
        print("Something went wrong. Please fix my code and submit a pull request...")
    else:
        print("ding ding ding! Your playlist can be found at " + final_url)
