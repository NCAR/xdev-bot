""" Project Board related events """
import gidgethub.routing
import pandas as pd

from .helpers import (decipher_note, get_card_data, read_database,
                      update_database, write_database)

router = gidgethub.routing.Router()


@router.register('project_card', action='created')
async def project_card_created_event(event, gh, *args, **kwargs):
    card_data = get_card_data(event.data)
    event_type, issue_api_url, repo = decipher_note(card_data['note'])

    entry = {
        'card_url': card_data['url'],
        'card_id': card_data['id'],
        'note': card_data['note'],
        'column_url': card_data['column_url'],
        'column_id': card_data['column_id'],
        'column_name': card_data['column_name'],
        'created_at': card_data['created_at'],
        'updated_at': card_data['updated_at'],
        'assignees': card_data['creator'],
        'event_type': event_type,
        'issue_api_url': issue_api_url,
        'repo': repo,
    }
    temp_df = pd.DataFrame([entry])
    df = read_database()

    df = pd.concat([temp_df, df], ignore_index=True, sort=False)

    write_database(df)


@router.register('project_card', action='moved')
async def project_card_moved_event(event, gh, *args, **kwargs):
    """ Whenever a card is moved, assign card mover to the issue or pull request."""
    card_data = get_card_data(event.data)
    df = read_database()
    assignees = df.loc[df['card_id'] == card_data['id']]['assignees'].values[0]

    assignees = assignees.split()

    if assignees == ['xdev-bot']:
        assignees = set()
    else:
        assignees = set(assignees)
    if card_data['mover'] == 'xdev-bot':
        assignees = assignees
    else:
        assignees.add(card_data['mover'])

    assignees = list(assignees)

    event_type, issue_api_url, repo = decipher_note(card_data['note'])

    # Assign card mover to issue or pull request
    print(f'Assigning user={card_data["mover"]} to {card_data["note"]}')
    if event_type == 'issues':
        if card_data['column_name'] == 'done':
            await gh.patch(issue_api_url, data={'state': 'closed', 'assignees': assignees})
        elif card_data['column_name'] == 'to_do':
            await gh.patch(issue_api_url, data={'state': 'open'})
        elif card_data['column_name'] == 'in_progress':
            await gh.patch(issue_api_url, data={'state': 'open', 'assignees': assignees})

    if assignees:
        assignees = ' '.join(assignees)
    else:
        assignees = 'xdev-bot'
    df = update_database(
        df=df,
        card_id=card_data['id'],
        column_name=card_data['column_name'],
        column_url=card_data['column_url'],
        column_id=card_data['column_id'],
        updated_at=card_data['updated_at'],
        assignees=assignees,
    )

    write_database(df)
