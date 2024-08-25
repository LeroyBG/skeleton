import { PUBLIC_CLIENT_ID, PUBLIC_REDIRECT_URI } from "$env/static/public";
export const authorizationRequestLink = 'https://accounts.spotify.com/authorize?'
    + new URLSearchParams({
        "client_id": PUBLIC_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": PUBLIC_REDIRECT_URI,
        "scope": "playlist-read-private playlist-modify-private playlist-modify-public"
    }).toString()