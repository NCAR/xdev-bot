from warnings import warn

import pandas as pd
import s3fs

# Connect to S3 using default credentials
fs = s3fs.S3FileSystem(anon=False)

PROJECT_BOARD = {
    'name': 'Backlog Queue',
    'columns': {
        'to_do': {'id': 4_507_386},
        'in_progress': {'id': 4_507_392},
        'done': {'id': 4_507_393},
    },
    'columns_reverse': {4_507_386: 'to_do', 4_507_392: 'in_progress', 4_507_393: 'done'},
}


def read_database(DB='xdev-bot/test_database.csv'):
    try:
        # If the databse file exists, open it in
        # a pandas dataframe
        if fs.exists(DB):
            with fs.open(DB, 'r') as f:
                print(f'Reading Existing Database from {DB} S3 bucket')
                df = pd.read_csv(f, index_col=0)
                print(df.head())
        else:
            # create empty dataframe
            columns = [
                'column_name',
                'column_id',
                'column_url',
                'note',
                'card_id',
                'card_url',
                'created_at',
                'updated_at',
                'assignees',
                'event_type',
                'issue_api_url',
                'repo',
            ]
            df = pd.DataFrame(columns=columns)
        return df

    except Exception as exc:
        raise exc


def write_database(df, DB='xdev-bot/test_database.csv'):

    with fs.open(DB, 'w') as f:
        print(f'Saving Database in {DB} S3 bucket')
        print(df.head())
        df.to_csv(f, index=True)


def decipher_note(card_note):
    """ Determine if a card's note is an issue or PR from html_url in the form
    'https://github.com/org_or_user/repo_name/issues_or_pull/number'

     - Construct Issue or PR API url:
        * Issue url: https://api.github.com/repos/NCAR/xdev-bot-testing/issues/2
        * PR url: https://api.github.com/repos/NCAR/xdev-bot-testing/pulls/3
    """

    note_items = card_note.split('/')

    if len(note_items) == 7:
        event_type = note_items[-2]

        if event_type in {'issues', 'pull'}:

            if event_type == 'issues':
                prefix = '/'.join(note_items[-4:])

            elif event_type == 'pull':
                # https://developer.github.com/v3/pulls/#labels-assignees-and-milestones
                # Every pull request is an issue, but not every issue is a pull request.
                p = note_items[-4:]
                p[-2] = 'issues'
                prefix = '/'.join(p)

            repo = note_items[-3]
            issue_api_url = 'https://api.github.com/repos/' + prefix

        else:

            event_type = 'manual'
            issue_api_url = 'N/A'
            repo = 'N/A'

    else:
        event_type = 'manual'
        issue_api_url = 'N/A'
        repo = 'N/A'

    return event_type, issue_api_url, repo


def update_database(df, card_id, **kwargs):
    """ Function to update database
    Parameters
    ----------
    df : pandas.DataFrame
         dataframe containing database information
    card_id : int
          id of the card to update
    kwargs :
           keyword arguments corresponding to colum
           that needs to be updated with the new value.
    """

    try:
        df = df.copy()
        columns = df.columns.tolist()
        if card_id in df['card_id'].unique():
            for key, value in kwargs.items():
                if key in columns:
                    df.loc[df['card_id'] == card_id, key] = value

                else:
                    raise ValueError(f'{key} is not in accepted columns: {columns}')
        else:

            warn(f'{card_id} is not found in database. {card_id} will be added to the database.')
            values = kwargs.copy()
            values['card_id'] = card_id
            temp_df = pd.DataFrame(values, columns=df.columns, index=[0])
            df = pd.concat([df, temp_df], ignore_index=True, sort=False)
        return df
    except Exception as exc:
        raise exc


def get_card_data(event_data):
    card_data = {}
    keys = ['url', 'id', 'note', 'column_url', 'column_id', 'created_at', 'updated_at']
    for key in keys:
        card_data[key] = event_data['project_card'][key]
    card_data['creator'] = event_data['project_card']['creator']['login']
    card_data['mover'] = event_data['sender']['login']
    card_data['column_name'] = PROJECT_BOARD['columns_reverse'][card_data['column_id']]
    return card_data
