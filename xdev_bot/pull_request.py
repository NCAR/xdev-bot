""" Pull requests events """
import gidgethub.routing

from .helpers import (PROJECT_BOARD, get_issue_or_pr_data, read_database, update_assignees,
                      write_database)

router = gidgethub.routing.Router()


@router.register('pull_request', action='opened')
@router.register('pull_request', action='closed')
async def pull_request_event(event, gh, *args, **kwargs):

    project_board_name = PROJECT_BOARD['name']
    issue_url = event.data['pull_request']['issue_url']
    html_url = event.data['pull_request']['html_url']  # note points to card_id

    if event.data['action'] == 'opened':
        card_action = 'Creating'
        column_id = PROJECT_BOARD['columns']['in_progress']['id']

        author = event.data['pull_request']['user']['login']
        await gh.patch(issue_url, data={'labels': ['needs-review'], 'assignees': [author]})

    if event.data['action'] == 'closed':
        card_action = 'Closing'
        column_id = PROJECT_BOARD['columns']['done']['id']

        df = read_database()
        row = df['note'] == html_url
        card_id = df.loc[row]['card_id'].values[0]
        print(f'Updating database: move card {card_id} to done column')

        dict_of_labels = event.data['pull_request']['labels']
        labels = []
        for item in dict_of_labels: labels.append(item['name'])
        labels = set(labels)
        if 'needs-review' in labels: labels.remove('needs-review')

        merged = event.data['pull_request']['merged']
        if merged: labels.add('merged')
        else: labels.add('rejected')
        labels = list(labels)
        await gh.patch(issue_url, data={'labels': labels})

    # POST /projects/columns/cards/:card_id/moves
    url = f'/projects/columns/cards/{card_id}/moves'
    await gh.post(
        url,
        data={'position': 'top', 'column_id': column_id},
        accept='application/vnd.github.inertia-preview+json',
    )
    print(f'{card_action} card in {project_board_name} project board for issue : {issue_url}')


@router.register('pull_request', action='assigned')
@router.register('pull_request', action='unassigned')
async def pull_request_assignment_event(event, gh, *args, **kwargs):
    data = get_issue_or_pr_data(event.data['pull_request'])
    df = read_database()
    df = update_assignees(data, df)
    write_database(df)
