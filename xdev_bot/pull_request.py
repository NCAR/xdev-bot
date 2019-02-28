""" Pull requests events """
import gidgethub.routing
from .helpers import read_database, write_database
from .project_board import PROJECT_BOARD
import ast

router = gidgethub.routing.Router()


@router.register('pull_request', action='opened')
async def pull_request_opened_event(event, gh, *args, **kwargs):
    """ Whenever a PR is opened,

    1) create a card in:

        - project_board = "Backlog Queue"
        - column = "In Progress"

    2) Mark new PRs as needing a review

    3) Assign PR's author to the PR

    """

    in_progress_column_id = PROJECT_BOARD['columns']['in_progress']['id']
    project_board_name = PROJECT_BOARD['name']
    pull_request_url = event.data['pull_request']['html_url']
    pull_request_api_url = event.data['pull_request']['url']
    issue_url = event.data['pull_request']['issue_url']
    author = event.data['pull_request']['user']['login']
    column_url = f'/projects/columns/{in_progress_column_id}/cards'
    print(
        f'Creating Card in {project_board_name} project board for pull request : {pull_request_url}'
    )

    # POST /projects/columns/:column_id/cards
    await gh.post(
        column_url,
        data={'note': pull_request_url},
        accept='application/vnd.github.inertia-preview+json',
    )

    # Mark new PRs as needing a review
    # POST /repos/:owner/:repo/issues/:number/labels
    await gh.post(issue_url, data={'labels': ['needs-review']})

    # Assigning PR author
        note_items = card_note.split("/")

    # This returns ['https:', '', 'github.com', 'org_or_user', 'repo_name', 'issues_or_pull', 'number']
    # if note is a html_url to an issue or pull request, len(note_items) == 7
    if len(note_items) == 7:
        _event_type = note_items[-2]

        # Construct Issue or PR API url
        # * Issue url looks like https://api.github.com/repos/NCAR/xdev-bot-testing/issues/2
        # * PR url looks like 'https://api.github.com/repos/NCAR/xdev-bot-testing/pulls/3'
        if _event_type == "issues":
            prefix = "/".join(note_items[-4:])

        elif _event_type == "pull":
            # https://developer.github.com/v3/pulls/#labels-assignees-and-milestones
            # Every pull request is an issue, but not every issue is a pull request.
            p = note_items[-4:]
            p[-2] = "issues"
            prefix = "/".join(p)
    _event_api_url = "https://api.github.com/repos/" + prefix
    await gh.post( _event_api_url, data={'assignees': list(author)})


@router.register('pull_request', action='closed')
async def pull_request_closed_event(event, gh, *args, **kwargs):
    """ Whenever a PR is closed, there are two scenarios:

    - PR is closed after merging
    - PR closed without merging

    When the PR is merged, move card from `In progress` column to
     `Done` column of `Backlog Queue` and assigns label 'merged'

     When the PR is closed without merging, move card again to 'Done'
        column but assign label 'rejected'

    TODO: When the PR is reopened, move column and change labels
    """

    done_column_id = PROJECT_BOARD["columns"]["done"]["id"]
    project_board_name = PROJECT_BOARD["name"]
    issue_url = event.data['pull_request']['issue_url']
    html_url = event.data["pull_request"]["html_url"] #note points to card_id

    df = read_database()
    row = df["note"] == html_url
    card_id = df.loc[row]["card_id"].values[0]

    print(f"Updating database: move card {card_id} to done column")
    print(f"Closing Card in {project_board_name} project board for issue : {issue_url}")
    
    # POST /projects/columns/cards/:card_id/moves
    url = f"/projects/columns/cards/{card_id}/moves"
    await gh.post(
        url,
        data={"position": "top", "column_id": done_column_id},
        accept="application/vnd.github.inertia-preview+json",
        )

    dict_of_labels = event.data["pull_request"]["labels"]
    labels = []
    for item in dict_of_labels:
        labels.append(item['name'])
    labels = set(labels)
    
    if 'needs-review' in labels:
        labels.remove('needs-review')

    merged = event.data['pull_request']["merged"]
    if merged:
        labels.add('merged')
    else:
        labels.add('rejected')
    labels = list(labels)
    await gh.patch(issue_url, data={'labels': labels})
