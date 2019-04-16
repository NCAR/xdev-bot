from .projectboard import PROJECT_BOARD
from .database import PROJECT_CARDS
from .gidgethub import GHArgs


def issue_opened_call_args(issue_event, column='to_do'):
    return _create_card_call_args_from_issue_event(issue_event, column=column)


def _create_card_call_args_from_issue_event(issue_event, column='to_do'):
    event_type = get_event_type(issue_event)
    if event_type:
        html_url = issue_event.data[event_type]['html_url']
        url = f'/projects/columns/{PROJECT_BOARD["column_ids"][column]}/cards'
        data = {'note': html_url}
        accept = 'application/vnd.github.inertia-preview+json'
        print(f'Creating {event_type} card in {column} column: {data["note"]}')
        return [GHArgs(url, data=data, accept=accept)]
    else:
        print(f'Unrecognized event type')
        return []


def issue_closed_call_args(issue_event, column='to_do', database=PROJECT_CARDS):
    event_type = get_event_type(issue_event)
    if event_type:
        html_url = issue_event.data[event_type]['html_url']
        card = database[html_url]
        if card is None:
            return issue_opened_call_args(issue_event, column=column)
        else:
            return get_move_card_ghargs_from_card(card, column=column)


def get_move_card_ghargs_from_card(card, column='to_do'):
    card_type = get_card_type(card)
    card_id = int(card['id'])
    column_id = PROJECT_BOARD['column_ids'][column]
    url = f'/projects/columns/cards/{card_id}/moves'
    data = {'position': 'top', 'column_id': column_id}
    accept = 'application/vnd.github.inertia-preview+json'
    print(f'Moving {card_type} card to {column} column: {card["note"]}')
    return GHArgs(url, data=data, accept=accept)


def project_card_moved_call_args(card_event, database=PROJECT_CARDS):
    new_card = get_card_from_card_event(card_event)
    old_card = database[new_card['note']]
    if old_card is None:
        print(f'Adding card not found to database: {new_card}')
        save_card(card_event, database=database)
        return get_set_status_ghargs(new_card)
    card_t = get_card_type(new_card)
    if card_t == 'issue':
        return get_update_issue_status_ghargs(old_card, new_card)
    elif card_t == 'pull_request':
        return get_update_pull_status_ghargs(old_card, new_card)


def get_update_pull_status_ghargs(old_card, new_card):
    merged = 'merged' in old_card and old_card['merged']
    moved = old_card['column_name'] != new_card['column_name']
    if merged and moved:
        return get_move_card_ghargs_from_card(new_card, column='done')
    else:
        return get_update_issue_status_ghargs(old_card, new_card)


def get_update_issue_status_ghargs(old_card, new_card):
    column_is_done = new_card['column_name'] == 'done'
    column_was_done = old_card['column_name'] == 'done'
    card_changed_state = column_is_done != column_was_done
    if card_changed_state:
        return get_set_status_ghargs(new_card)


def get_set_status_ghargs(card):
    card_t = get_card_type(card)
    prefix = 'https://api.github.com/repos/'
    suffix_items = card['note'].split('/')[-4:]
    suffix_items[-2] = 'issues'
    suffix = '/'.join(suffix_items)
    url = prefix + suffix
    state = 'closed' if card['column_name'] == 'done' else 'open'
    print(f'Updating {card_t} status to {state}: {card["note"]}')
    return GHArgs(url, data={'state': state}, func='patch')


def save_card(card_event, database=PROJECT_CARDS):
    card = get_card_from_card_event(card_event)
    print(f'Saving card to database: {card["note"]}')
    database.add(card)
    database.save()


def remove_card(card_event, database=PROJECT_CARDS):
    card = get_card_from_card_event(card_event)
    print(f'Removing card from database: {card["note"]}')
    database.remove(card)
    database.save()


def save_merged_status(pr_event, database=PROJECT_CARDS):
    note = pr_event.data['pull_request']['html_url']
    merged = pr_event.data['pull_request']['merged']
    print(f'Saving merged status as {merged} for card: {note}')
    database[note] = {'merged': merged}
    database.save()


def get_card_from_card_event(card_event):
    keys = ['url', 'id', 'note', 'column_url', 'column_id', 'created_at', 'updated_at']
    card = {k: card_event.data['project_card'][k] for k in keys}
    card['creator'] = card_event.data['project_card']['creator']['login']
    card['sender'] = card_event.data['sender']['login']
    card['column_name'] = PROJECT_BOARD['column_ids'].inverse[card['column_id']]
    card['type'] = get_card_type(card)
    return card


def get_event_type(event):
    if not hasattr(event, 'data'):
        return None
    recognized_types = ['issue', 'pull_request']
    for recognized_type in recognized_types:
        if recognized_type in event.data:
            return recognized_type


def get_card_type(card):
    note = card['note']
    if note.startswith('https://github.com/'):
        note_t = note.split('/')[-2]
        return 'pull_request' if note_t == 'pull' else 'issue'
    else:
        return None
