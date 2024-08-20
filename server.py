from aiohttp import web, ClientSession
from os import environ
from base64 import b64encode
import Skeleton

routes = web.RouteTableDef()

@routes.get('/authorize')
async def auth(request: web.Request):
    print("someone wants auth")
    async with ClientSession() as session:
        print("Someone wants auth")
        code = request.query["code"]
        credentials = f"{environ['CLIENT_ID']}:{environ['CLIENT_SECRET']}"
        headers = {
                "content-type": "application/x-www-form-urlencoded",
                'Authorization': 'Basic ' + b64encode(credentials.encode()).decode()
        }
        data = {
            "code": code,
            "redirect_uri": environ["REDIRECT_URI"],
            "grant_type": "authorization_code"
        }
        req_url = f"https://accounts.spotify.com/api/token"
        async with session.post(req_url, headers=headers, data=data) as res:
            if res.status != 200:
                print(res)
                return web.Response(status=500)
            data = await res.json()
            response_headers = {
                "Access-Control-Allow-Origin": environ["FRONTEND_URL"]
            }
            return web.json_response(headers=response_headers, data=data)

@routes.get('/samples')
async def samples(request: web.Request):
    print("Someone wants samples")
    async with ClientSession() as session:
        playlist_uri = request.query["playlist_id"]
        token = request.headers["Authorization"]
        playlist_uri = await Skeleton.Skeleton(verbose=True).make_sample_playlist(
            resource_uri = playlist_uri,
            session = session,
            token = token,
        )
        return web.json_response(data={
                "playlist_uri": playlist_uri
            }, status=200, headers={
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Origin": environ["FRONTEND_URL"],
                "Access-Control-Allow-Method": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "X-Requested-With, Content-type, Authorization"
        })

@routes.options('/samples')
async def options(request: web.Request):
    print("Preflight!")
    return web.Response(
        status=200,
        headers={
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Origin": environ["FRONTEND_URL"],
            "Access-Control-Allow-Method": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "X-Requested-With, Content-type, Authorization"
        }
    )

@routes.get("/")
async def fallback(request):
    print("Fallback", request)
    return web.Response(500)

app = web.Application()
app.add_routes(routes)
web.run_app(app)