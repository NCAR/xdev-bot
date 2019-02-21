""" Issue related events"""
import gidgethub.routing

from .project_board import PROJECT_BOARD

router = gidgethub.routing.Router()


@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    """ Whenever an issue is opened, create a card in Backlog Queue project board.

    Subscribe to the Github issues event and
    specifically to the "opened" issues event
    Two important params:

    - event: the representation of Github webhook event. We
             can access the event payload by doing `event.data`
    - gh: the gidgethub GitHub API, which we use to make API calls
          to GitHub
    """
    to_do_column_id = PROJECT_BOARD["to_do_column_id"]
    project_board_name = PROJECT_BOARD["name"]
    issue_url = event.data["issue"]["html_url"]
    url = f"/projects/columns/{to_do_column_id}/cards"
    print(
        f"Creating Card in {project_board_name} project board for issue : {issue_url}"
    )

    # POST /projects/columns/:column_id/cards
    await gh.post(
        url,
        data={"note": issue_url},
        accept="application/vnd.github.inertia-preview+json",
    )
