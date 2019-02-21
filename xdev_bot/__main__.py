import os
import aiohttp
from aiohttp import web
from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

router = routing.Router()


@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    """ Whenever an issue is opened, greet the author and say thanks.
    
    Subscribe to the Github issues event and 
    specifically to the "opened" issues event 
    Two important params: 

    - event: the representation of Github webhook event. We 
             can access the event payload by doing `event.data`
    - gh: the gidgethub GitHub API, which we use to make API calls
          to GitHub
    """

    url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]

    message = f"Thanks for the report @{author}! I will look into it ASAP! ( I am a bot)."
    await gh.post(url, data={"body": message})


@router.register("pull_request", action="closed")
async def pull_request_merge_event(event, gh, *args, **kwargs):
    """ Whenever a PR is merged, greet the author and say thanks to both the PR author 
    and the person who merged it.
    
    """

    url = event.data["pull_request"]["comments_url"]

    # PR can be closed without being merged.
    merged = event.data["pull_request"]["merged"]

    if merged:
        author = event.data["pull_request"]["user"]["login"]
        merged_by = event.data["pull_request"]["merged_by"]
        message = f"Thank for your contribution @{author}! Thank you @{merged_by} for your merging this ! ( I am a bot)."
        await gh.post(url, data={"body": message})


async def main(request):
    # Read the GitHub webhook payload
    body = await request.read()

    # Our authentication token and secret
    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    # A representation of Github webhook event
    event = sansio.Event.from_http(request.headers, body, secret=secret)

    # Create a session
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "xdev-bot", oauth_token=oauth_token)

        # Call the approriate callback for the event
        await router.dispatch(event, gh)

    # Return a "Success"
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()

    # Github will send us POST requests to the webhook
    # instead of GET
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
