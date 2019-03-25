from .projectboard import PROJECT_BOARD


def create_new_card(event):
    column_id = PROJECT_BOARD['column_ids']['to_do']
    issue_url = event.data['issue']['html_url']
    url = f'/projects/columns/{column_id}/cards'
    data = {'note': issue_url}
    return url, data


def get_card_properties(event):
    keys = ['url', 'id', 'note', 'column_url', 'column_id', 'created_at', 'updated_at']
    properties = {k: event.data['project_card'][k] for k in keys}
    properties['creator'] = event.data['project_card']['creator']['login']
    properties['mover'] = event.data['sender']['login']
    properties['column_name'] = PROJECT_BOARD['column_ids'].inverse[properties['column_id']]
    return properties
