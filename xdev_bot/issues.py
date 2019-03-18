""" Issue related events"""
import gidgethub.routing

from .helpers import PROJECT_BOARD, read_database

router = gidgethub.routing.Router()


@router.register('issues', action='opened')
async def issue_opened_event(event, gh, *args, **kwargs):
    """ Whenever an issue is opened, create a card in

    - project_board = "Backlog Queue"
    - column = "to_do"
    """
    to_do_column_id = PROJECT_BOARD['columns']['to_do']['id']
    project_board_name = PROJECT_BOARD['name']
    issue_url = event.data['issue']['html_url']
    url = f'/projects/columns/{to_do_column_id}/cards'

    print(f'Creating Card in {project_board_name} project board for issue : {issue_url}')

    # POST /projects/columns/:column_id/cards
    await gh.post(
        url, data={'note': issue_url}, accept='application/vnd.github.inertia-preview+json'
    )


@router.register('issues', action='reopened')
@router.register('issues', action='closed')
async def issue_closed_event(event, gh, *args, **kwargs):
    """
    - find card associated with issue (get card ID)
    - construct URL for card

    1. Whenever an issue is closed:
    - get column ID of "done" column
    - retrieve updated_at from payload and update database
    - update card information (new column ID)

    2. Whenever an issue is reopened:
    - get column ID of "in-progess" column
    - update card information (new column ID)


    """
    issue_url = event.data['issue']['html_url']
    project_board_name = PROJECT_BOARD['name']
    df = read_database()
    row = df['note'] == issue_url
    card_id = df.loc[row]['card_id'].values[0]
    url = f'/projects/columns/cards/{card_id}/moves'

    if event.data['action'] == 'closed':
        done_column_id = PROJECT_BOARD['columns']['done']['id']
        print(f'Updating database: move card {card_id} to done column')
        # write_database(df)

        print(f'Closing Card in {project_board_name} project board for issue : {issue_url}')
        # POST /projects/columns/cards/:card_id/moves

        await gh.post(
            url,
            data={'position': 'top', 'column_id': done_column_id},
            accept='application/vnd.github.inertia-preview+json',
        )

    else:
        in_progress_column_id = PROJECT_BOARD['columns']['in_progress']['id']
        print(f'Updating database: move card {card_id} to in-progress column')

        await gh.post(
            url,
            data={'position': 'top', 'column_id': in_progress_column_id},
            accept='application/vnd.github.inertia-preview+json',
        )
        print(f' Reopening card in {project_board_name} project board for issue : {issue_url}')
