import asyncio
import os
import sys
import traceback

import aiohttp
import cachetools
from aiohttp import web
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio

from . import events

router = routing.Router(events.router)
cache = cachetools.LRUCache(maxsize=500)


async def main(request):
    try:

        body = await request.read()

        user = os.environ.get("GH_USER")
        secret = os.environ.get("GH_SECRET")
        oauth_token = os.environ.get("GH_AUTH")

        event = sansio.Event.from_http(request.headers, body, secret=secret)
        print("GitHub delivery ID", event.delivery_id, file=sys.stderr)
        if event.event == "ping":
            return web.Response(status=200)

        async with aiohttp.ClientSession() as session:
            gh = gh_aiohttp.GitHubAPI(session, user, oauth_token=oauth_token, cache=cache)
            await asyncio.sleep(1)
            await router.dispatch(event, gh)

        try:
            print(f"GitHub requests remaining: {gh.rate_limit.remaining}")

        except AttributeError:
            pass
        return web.Response(status=200)

    except Exception:
        traceback.print_exc(file=sys.stderr)
        return web.Response(status=500)


if __name__ == "__main__":  # pragma: no cover
    app = web.Application()
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)
    web.run_app(app, port=port)
