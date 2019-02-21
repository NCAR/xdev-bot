""" Pull requests events """
import gidgethub.routing

from .project_board import PROJECT_BOARD

router = gidgethub.routing.Router()


@router.register("pull_request", action="opened")
async def pull_request_opened_event(event, gh, *args, **kwargs):
    """ Whenever a PR is opened, create a card in:

    - project_board = "Backlog Queue"
    - column = "In Progress"

    """
    in_progress_column_id = PROJECT_BOARD["columns"]["in_progress"]["id"]
    project_board_name = PROJECT_BOARD["name"]
    pull_request_url = event.data["pull_request"]["html_url"]
    url = f"/projects/columns/{in_progress_column_id}/cards"
    print(
        f"Creating Card in {project_board_name} project board for pull request : {pull_request_url}"
    )
    url = event.data["pull_request"]["comments_url"]

    # POST /projects/columns/:column_id/cards
    await gh.post(
        url,
        data={"note": pull_request_url},
        accept="application/vnd.github.inertia-preview+json",
    )
