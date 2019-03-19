""" Issue related events"""
import gidgethub.routing

from .helpers import (PROJECT_BOARD, get_issue_or_pr_data, read_database, update_assignees,
                      write_database)

router = gidgethub.routing.Router()


@router.register('issues', action='opened')
@router.register('issues', action='reopened')
@router.register('issues', action='closed')
async def issue_event(event, gh, *args, **kwargs):

    issue_url = event.data['issue']['html_url']
    project_board_name = PROJECT_BOARD['name']
    df = read_database()
    row = df['note'] == issue_url
    card_id = df.loc[row]['card_id'].values[0]

    if event.data['action'] == 'opened':
        card_Action = 'Creating'
        column_id = PROJECT_BOARD['columns']['to_do']['id']
        url = f'/projects/columns/{column_id}/cards'
    elif event.data['action'] == 'closed':
        card_action = 'Closing'
        column_id = PROJECT_BOARD['columns']['done']['id']
        url = f'/projects/columns/cards/{card_id}/moves'
    else:
        card_action = 'Reopening'
        column_id = PROJECT_BOARD['columns']['in_progress']['id']
        url = f'/projects/columns/cards/{card_id}/moves'


    await gh.post(
        url,
        data={'position': 'top', 'column_id': column_id},
        accept='application/vnd.github.inertia-preview+json')
    print(f' {card_action} card in {project_board_name} project board for issue : {issue_url}')


@router.register('issues', action='assigned')
@router.register('issues', action='unassigned')
async def issue_assignment_event(event, gh, *args, **kwargs):
    data = get_issue_or_pr_data(event.data['issue'])
    df = read_database()
    df = update_assignees(data, df)
    write_database(df)
