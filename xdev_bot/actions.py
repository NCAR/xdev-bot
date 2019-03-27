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


def create_card(issue_or_pr_event, column='to_do'):
    column_id = PROJECT_BOARD['column_ids'][column]
    event_type = get_event_type(issue_or_pr_event)
    html_url = issue_or_pr_event.data[event_type]['html_url']
    url = f'/projects/columns/{column_id}/cards'
    data = {'note': html_url}
    accept = 'application/vnd.github.inertia-preview+json'
    return GHArgs(url, data=data, accept=accept)


def move_card(issue_or_pr_event, column='to_do', database=PROJECT_CARDS):
    event_type = get_event_type(issue_or_pr_event)
    html_url = issue_or_pr_event.data[event_type]['html_url']
    idx = database.where(note=html_url)
    if len(idx) == 0:
        return create_card(issue_or_pr_event, column=column)
    elif len(idx) == 1:
        card_id = int(database[idx[0]]['id'])
        column_id = PROJECT_BOARD['column_ids'][column]
        url = f'/projects/columns/cards/{card_id}/moves'
        data = {'position': 'top', 'column_id': column_id}
        accept = 'application/vnd.github.inertia-preview+json'
        return GHArgs(url, data=data, accept=accept)
    else:
        raise KeyError(f'could not find unique project card for {html_url}')


def get_event_type(event):
    if 'issue' in event.data:
        return 'issue'
    elif 'pull_request' in event.data:
        return 'pull_request'
    else:
        return None


def update_issue(card, state=None):
    prefix = 'https://api.github.com/repos/'
    suffix = '/'.join(card['note'].split('/')[-4:])
    url = prefix + suffix
    data = {}
    if state:
        data['state'] = state
    return GHArgs(url, data=data)
