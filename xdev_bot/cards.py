from .projectboard import PROJECT_BOARD
from .database import PROJECT_CARDS


def create_new_card(issue_event, column='to_do'):
    column_id = PROJECT_BOARD['column_ids'][column]
    issue_url = issue_event.data['issue']['html_url']
    url = f'/projects/columns/{column_id}/cards'
    data = {'note': issue_url}
    return url, data


def get_card_properties(card_event):
    keys = ['url', 'id', 'note', 'column_url', 'column_id', 'created_at', 'updated_at']
    properties = {k: card_event.data['project_card'][k] for k in keys}
    properties['creator'] = card_event.data['project_card']['creator']['login']
    properties['mover'] = card_event.data['sender']['login']
    properties['column_name'] = PROJECT_BOARD['column_ids'].inverse[properties['column_id']]
    return properties


def move_card(issue_event, column='to_do', database=PROJECT_CARDS):
    issue_url = issue_event.data['issue']['html_url']
    cards = database.where(note=issue_url)
    if len(cards) == 0:
        return create_new_card(issue_event, column=column)
    elif len(cards) == 1:
        card_id = int(cards[0]['id'])
        column_id = PROJECT_BOARD['column_ids'][column]
        url = f'/projects/columns/cards/{card_id}/moves'
        data = {'position': 'top', 'column_id': column_id}
        return url, data
    else:
        raise KeyError(f'could not find unique project card for {issue_url}')
