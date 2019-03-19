""" Issue related events"""
import gidgethub.routing

from .helpers import (PROJECT_BOARD, get_issue_or_pr_data, read_database, update_assignees,
                      write_database)

router = gidgethub.routing.Router()


@router.register('issues', action='opened')
@router.register('issues', action='reopened')
@router.register('issues', action='closed')
@router.register('pull_request', action='opened')
@router.register('pull_request', action='closed')
async def issue_event(event, gh, *args, **kwargs):
    project_board_name = PROJECT_BOARD['name']

    if event.data[0] == 'issues':
        html_url = event.data['issue']['html_url']
    if event.data[0] == 'pull_request':
        issue_url = event.data['pull_request']['issue_url']
        html_url = event.data['pull_request']['html_url']
    

    if event.data['action'] == 'opened':
        card_Action = 'Creating'
        column_id = PROJECT_BOARD['columns']['to_do']['id']
        url = f'/projects/columns/{column_id}/cards'

        if event.data[0] == 'pull_request':
            author = event.data['pull_request']['user']['login']
            await gh.patch(issue_url, data={'labels': ['needs-review'], 'assignees': [author]})

    else:
        df = read_database()
        row = df['note'] == html_url
        card_id = df.loc[row]['card_id'].values[0]

        if event.data['action'] == 'closed':
            card_action = 'Closing'
            column_id = PROJECT_BOARD['columns']['done']['id']

            if event.data[0] == 'pull_request':
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

        elif event.data['action'] == 'reopened':
            card_action = 'Reopening'
            column_id = PROJECT_BOARD['columns']['in_progress']['id']

        url = f'/projects/columns/cards/{card_id}/moves'

    await gh.post(
        url,
        data={'position': 'top', 'column_id': column_id},
        accept='application/vnd.github.inertia-preview+json')
    print(f' {card_action} card in {project_board_name} project board for issue : {html_url}')

@router.register('issues', action='assigned')
@router.register('issues', action='unassigned')
@router.register('pull_request', action='assigned')
@router.register('pull_request', action='unassigned')
async def assignment_event(event, gh, *args, **kwargs):
    if event.data[0] == 'issues': event = 'issue'
    elif event.data[0] == 'pull_request': event = 'pull_request'
    data = get_issue_or_pr_data(event.data[event])
    df = read_database()
    df = update_assignees(data, df)
    write_database(df)
