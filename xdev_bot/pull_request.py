""" Pull requests events """
import gidgethub.routing

router = gidgethub.routing.Router()


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
        merged_by = event.data["pull_request"]["merged_by"]["login"]
        message = f"Thank for your contribution @{author}! Thank you @{merged_by} for your merging this ! ( I am a :octocat: bot )."
        await gh.post(url, data={"body": message})
