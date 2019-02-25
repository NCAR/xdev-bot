import asyncio
import os
import sys
import traceback

import aiohttp
import cachetools
from aiohttp import web
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio

from . import issues, project_board, pull_request

router = routing.Router(pull_request.router, issues.router, project_board.router)
cache = cachetools.LRUCache(maxsize=500)

USER = "xdev-bot"


async def main(request):
    try:

        # Read the GitHub webhook payload
        body = await request.read()

        # Our authentication token and secret
        secret = os.environ.get("GH_SECRET")
        oauth_token = os.environ.get("GH_AUTH")

        # A representation of Github webhook event
        event = sansio.Event.from_http(request.headers, body, secret=secret)
        print("GH delivery ID", event.delivery_id, file=sys.stderr)
        if event.event == "ping":
            return web.Response(status=200)

        # Create a session
        async with aiohttp.ClientSession() as session:
            gh = gh_aiohttp.GitHubAPI(session, USER, oauth_token=oauth_token, cache=cache)

            # Give GitHub some time to reach internal consistency.
            await asyncio.sleep(1)
            # Call the approriate callback for the event
            await router.dispatch(event, gh)

        try:
            print(f"GH requests remaining : {gh.rate_limit.remaining}")

        except AttributeError:
            pass
        return web.Response(status=200)

    except Exception:
        traceback.print_exc(file=sys.stderr)
        return web.Response(status=500)


if __name__ == "__main__":  # pragma: no cover
    app = web.Application()

    # Github will send us POST requests to the webhook
    # instead of GET
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
