import pandas as pd
import s3fs

# Connect to S3 using default credentials
fs = s3fs.S3FileSystem(anon=False)


def read_database(DB='xdev-bot/database.csv'):
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
            ]
            df = pd.DataFrame(columns=columns)
        return df

    except Exception as exc:
        raise exc


def write_database(df, DB='xdev-bot/database.csv'):

    with fs.open(DB, 'w') as f:
        print(f'Saving Database in {DB} S3 bucket')
        print(df.head())
        df.to_csv(f, index=True)


def decipher_note(card_note):
    # Determine if a card's note is an issue or PR
    # from html_url in the form
    # 'https://github.com/org_or_user/repo_name/issues_or_pull/number'

    note_items = card_note.split('/')

    # This returns ['https:', '', 'github.com', 'org_or_user', 'repo_name', 'issues_or_pull', 'number']
    # if note is a html_url to an issue or pull request, len(note_items) == 7
    if len(note_items) == 7:
        event_type = note_items[-2]

        if event_type in {'issues', 'pull'}:
            # Construct Issue or PR API url
            # * Issue url looks like https://api.github.com/repos/NCAR/xdev-bot-testing/issues/2
            # * PR url looks like 'https://api.github.com/repos/NCAR/xdev-bot-testing/pulls/3'
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
