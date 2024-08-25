from aiohttp import web, ClientSession
from os import environ
import base64
import Skeleton
from aiohttp_session import setup, get_session, session_middleware 
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet
from datetime import datetime, timezone
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
credentials = f"{environ['CLIENT_ID']}:{environ['CLIENT_SECRET']}"
authorization = 'Basic ' + base64.b64encode(credentials.encode()).decode()
routes = web.RouteTableDef()
skeleton = Skeleton.Skeleton(verbose=True)

@routes.get('/')
async def hello_world(request: web.Request):
    return web.Response(body="Hello world!")

@routes.get('/token-from-code')
async def token_from_code(request: web.Request):
    code = request.query["code"]
    headers = {
            "content-type": "application/x-www-form-urlencoded",
            'Authorization': authorization
    }
    data = {
        "code": code,
        "redirect_uri": environ["REDIRECT_URI"],
        "grant_type": "authorization_code"
    }
    req_url = "https://accounts.spotify.com/api/token"
    async with ClientSession() as session:
        async with session.post(req_url, headers=headers, data=data) as res:
            # if res.status != 200:
            #     print(res)
            #     return web.Response(status=500)
            print(res)
            data = await res.json()
            print(data)
            mem_session = await get_session(request)
            mem_session["token"] = {
                "access_token": data["access_token"],
                "expires_at": 
                    data["expires_in"] * 1000
                    + int(
                        datetime.now(timezone.utc).timestamp()
                        )
                    - (5 * 1000),
                "refresh_token": data["refresh_token"]
            }
            response_headers = {
                "Access-Control-Allow-Origin": environ["FRONTEND_URL"],
                "Access-Control-Allow-Credentials": "true",
            }
            return web.Response(headers=response_headers, status=200)

@routes.get('/samples')
async def samples(request: web.Request):
    print("Received a request for samples")
    async with ClientSession() as session:
        resource_uri = request.query["resource_uri"]
        request_session = await get_session(request)
        token_data = request_session.get("token")
        if not token_data:
            return web.Response(status=401, reason="access token not found")
        print(f'is {token_data["expires_at"]} less than {datetime.now(timezone.utc).timestamp()}?')
        if token_data["expires_at"] < datetime.now(timezone.utc).timestamp():
            # Refresh token
            refresh = await refresh_token(session=session, refresh_token=token_data["refresh_token"])
            if not refresh:
                return web.Response(status=401, reason="couldn't refresh your token")
            request_session["token"] = {
                "access_token": refresh["access_token"],
                "expires_at": 
                    refresh["expires_in"] 
                    + int(
                        datetime.now(timezone.utc).timestamp()
                        )
                    - (5 * 1000),
                "refresh_token": refresh["refresh_token"]
            }
        print("does this happen twice? 1")
        playlist_uri, samples_report, original_resource_name, playlist_name = await skeleton.make_sample_playlist(
            resource_uri = resource_uri,
            session = session,
            token = request_session["token"]["access_token"],
        )
        return web.json_response(data={
                "original_resource_name": original_resource_name,
                "playlist_name": playlist_name,
                "playlist_uri": playlist_uri,
                "samples_report": samples_report,
            }, status=200, headers={
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Origin": environ["FRONTEND_URL"],
                "Access-Control-Allow-Method": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "X-Requested-With, Content-type, Authorization"
        })

@routes.options('/*')
async def options(request: web.Request):
    return web.Response(
        status=200,
        headers={
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Origin": environ["FRONTEND_URL"],
            "Access-Control-Allow-Method": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "X-Requested-With, Content-type, Authorization"
        }
    )

async def refresh_token(session: ClientSession, refresh_token: str) -> str | None:
    async with session.post('https://accounts.spotify.com/api/token', headers={
        "content-type": "application/x-www-form-urlencoded",
        "Authorization": authorization
    }, data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }) as res:
        if res.status != 200:
            return None
        data = await res.json()
        return {
            "access_token": data["access_token"],
            "expires_in": data["expires_in"],
            "refresh_token": data["refresh_token"]
        }


app = web.Application()
fernet_key = fernet.Fernet.generate_key()
secret_key = base64.urlsafe_b64decode(fernet_key)
setup(app, EncryptedCookieStorage(secret_key))
app.add_routes(routes)
web.run_app(app, port=int(environ["SERVER_PORT"]))