from .projectboard import PROJECT_BOARD
from .database import PROJECT_CARDS
from .gidgethub import GHArgs


def get_create_card_ghargs(issue_or_pr_event, column='to_do'):
    column_id = PROJECT_BOARD['column_ids'][column]
    event_type = get_event_type(issue_or_pr_event)
    html_url = issue_or_pr_event.data[event_type]['html_url']
    url = f'/projects/columns/{column_id}/cards'
    data = {'note': html_url}
    accept = 'application/vnd.github.inertia-preview+json'
    print(f'Creating {event_type} card in column {column}: {data["note"]}')
    return GHArgs(url, data=data, accept=accept)


def get_move_card_ghargs(issue_or_pr_event, column='to_do', database=PROJECT_CARDS):
    event_type = get_event_type(issue_or_pr_event)
    html_url = issue_or_pr_event.data[event_type]['html_url']
    card = database[html_url]
    if card is None:
        return get_create_card_ghargs(issue_or_pr_event, column=column)
    else:
        card_id = int(card['id'])
        column_id = PROJECT_BOARD['column_ids'][column]
        url = f'/projects/columns/cards/{card_id}/moves'
        data = {'position': 'top', 'column_id': column_id}
        accept = 'application/vnd.github.inertia-preview+json'
        print(f'Moving {event_type} card to column {column}: {card["note"]}')
        return GHArgs(url, data=data, accept=accept)


def get_update_status_ghargs(card_event):
    card = get_card_from_card_event(card_event)
    prefix = 'https://api.github.com/repos/'
    suffix_items = card['note'].split('/')[-4:]
    suffix_items[-2] = 'issues'
    suffix = '/'.join(suffix_items)
    url = prefix + suffix
    state = 'closed' if card['column_name'] == 'done' else 'open'
    data = {'state': state}
    print(f'Updating issue status to {state}: {card["note"]}')
    return GHArgs(url, data=data)


def save_new_card(card_event, database=PROJECT_CARDS):
    card = get_card_from_card_event(card_event)
    database.add(card)
    database.save()


def remove_card(card_event, database=PROJECT_CARDS):
    card = get_card_from_card_event(card_event)
    database.remove(card)
    database.save()


def save_merged_status(pr_event, database=PROJECT_CARDS):
    note = pr_event.data['pull_request']['html_url']
    merged = pr_event.data['pull_request']['merged']
    database[note] = {'merged': merged}
    database.save()


def get_card_from_card_event(card_event):
    keys = ['url', 'id', 'note', 'column_url', 'column_id', 'created_at', 'updated_at']
    card = {k: card_event.data['project_card'][k] for k in keys}
    card['creator'] = card_event.data['project_card']['creator']['login']
    card['sender'] = card_event.data['sender']['login']
    card['column_name'] = PROJECT_BOARD['column_ids'].inverse[card['column_id']]
    card['type'] = get_card_type(card)
    card['merged'] = None
    return card


def get_event_type(event):
    if 'issue' in event.data:
        return 'issue'
    elif 'pull_request' in event.data:
        return 'pull_request'
    else:
        return None


def get_card_type(card):
    note = card['note']
    if note.startswith('https://github.com/'):
        note_t = note.split('/')[-2]
        return 'pull_request' if note_t == 'pull' else 'issue'
    else:
        return None
