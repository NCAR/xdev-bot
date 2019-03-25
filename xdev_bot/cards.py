from .projectboard import PROJECT_BOARD


def create_new_card(event):
    column_id = PROJECT_BOARD['column_ids']['to_do']
    issue_url = event.data['issue']['html_url']
    url = f'/projects/columns/{column_id}/cards'
    data = {'note': issue_url}
    return url, data
