""" Issue related events"""
import gidgethub.routing

router = gidgethub.routing.Router()


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

    message = (
        f"Thanks for the report @{author}! I will look into it ASAP! ( I am a bot)."
    )
    await gh.post(url, data={"body": message})
