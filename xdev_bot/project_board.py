""" Project Board related events """
import gidgethub.routing
import pandas as pd

from .helpers import (decipher_note, read_database, update_database,
                      write_database)

router = gidgethub.routing.Router()


PROJECT_BOARD = {
    'name': 'Backlog Queue',
    'columns': {
        'backlog': {'id': 4_507_386},
        'in_progress': {'id': 4_507_392},
        'done': {'id': 4_507_393},
    },
    'columns_reverse': {4_507_386: 'backlog', 4_507_392: 'in_progress', 4_507_393: 'done'},
}


@router.register('project_card', action='created')
async def project_card_created_event(event, gh, *args, **kwargs):
    card_url = event.data['project_card']['url']
    card_id = event.data['project_card']['id']
    note = event.data['project_card']['note']
    column_url = event.data['project_card']['column_url']
    column_id = event.data['project_card']['column_id']
    column_name = PROJECT_BOARD['columns_reverse'][column_id]
    created_at = event.data['project_card']['created_at']
    updated_at = event.data['project_card']['updated_at']
    card_creator = event.data['project_card']['creator']['login']
    entry = {
        'card_url': card_url,
        'card_id': card_id,
        'note': note,
        'column_url': column_url,
        'column_id': column_id,
        'column_name': column_name,
        'created_at': created_at,
        'updated_at': updated_at,
        'assignees': card_creator,
    }
    temp_df = pd.DataFrame([entry])
    df = read_database()

    df = pd.concat([temp_df, df], ignore_index=True, sort=False)

    write_database(df)


@router.register('project_card', action='moved')
async def project_card_moved_event(event, gh, *args, **kwargs):
    """ Whenever a card is moved, assign card mover to the issue or pull request."""

    card_mover = event.data['sender']['login']
    card_id = event.data['project_card']['id']
    card_note = event.data['project_card']['note']
    column_url = event.data['project_card']['column_url']
    column_id = event.data['project_card']['column_id']
    column_name = PROJECT_BOARD['columns_reverse'][column_id]
    updated_at = event.data['project_card']['updated_at']

    df = read_database()
    assignees = df.loc[df['card_id'] == card_id]['assignees'].values[0]

    assignees = assignees.split()

    if assignees == ['xdev-bot']:
        assignees = set()
    else:
        assignees = set(assignees)
    if card_mover == 'xdev-bot':
        assignees = assignees
    else:
        assignees.add(card_mover)

    assignees = list(assignees)

    event_type, issue_api_url, repo = decipher_note(card_note)

    # Assign card mover to issue or pull request
    print(f'Assigning user={card_mover} to {card_note}')
    if event_type == 'issues':
        if column_name == 'done':
            await gh.patch(issue_api_url, data={'state': 'closed', 'assignees': assignees})
        elif column_name == 'backlog':
            await gh.patch(issue_api_url, data={'state': 'open'})
        elif column_name == 'in_progress':
            await gh.patch(issue_api_url, data={'state': 'open', 'assignees': assignees})

    if assignees:
        assignees = ' '.join(assignees)
    else:
        assignees = 'xdev-bot'
    df = update_database(
        df=df,
        card_id=card_id,
        column_name=column_name,
        column_url=column_url,
        column_id=column_id,
        updated_at=updated_at,
        assignees=assignees,
    )

    write_database(df)
