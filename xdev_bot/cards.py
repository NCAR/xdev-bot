from .projectboard import PROJECT_BOARD
from .database import PROJECT_CARDS
from .gidgethub import GHArgs


def get_card(card_event):
    keys = ['url', 'id', 'note', 'column_url', 'column_id', 'created_at', 'updated_at']
    card = {k: card_event.data['project_card'][k] for k in keys}
    card['creator'] = card_event.data['project_card']['creator']['login']
    card['mover'] = card_event.data['sender']['login']
    card['column_name'] = PROJECT_BOARD['column_ids'].inverse[card['column_id']]
    card_type = card['note'].split('/')[-2]
    card['type'] = 'pull_request' if card_type == 'pull' else 'issue'
    return card


def card_is_issue(card):
    return card['type'] == 'issue'


def card_is_pull_request(card):
    return card['type'] == 'pull_request'


def create_new_card(issue_event, column='to_do'):
    column_id = PROJECT_BOARD['column_ids'][column]
    issue_url = issue_event.data['issue']['html_url']
    url = f'/projects/columns/{column_id}/cards'
    data = {'note': issue_url}
    accept = 'application/vnd.github.inertia-preview+json'
    return GHArgs(url, data=data, accept=accept)


def move_card(issue_event, column='to_do', database=PROJECT_CARDS):
    issue_url = issue_event.data['issue']['html_url']
    idx = database.where(note=issue_url)
    if len(idx) == 0:
        return create_new_card(issue_event, column=column)
    elif len(idx) == 1:
        card_id = int(database[idx[0]]['id'])
        column_id = PROJECT_BOARD['column_ids'][column]
        url = f'/projects/columns/cards/{card_id}/moves'
        data = {'position': 'top', 'column_id': column_id}
        accept = 'application/vnd.github.inertia-preview+json'
        return GHArgs(url, data=data, accept=accept)
    else:
        raise KeyError(f'could not find unique project card for {issue_url}')
