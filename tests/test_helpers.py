import json
import os

import pandas as pd
import pytest

from xdev_bot.helpers import (decipher_note, get_card_data, read_database,
                              update_database, write_database)

here = os.path.abspath(os.path.dirname(__file__))
test_data = [
    (
        'https://github.com/NCAR/xdev-bot-testing/pull/62',
        (
            'pull',
            'https://api.github.com/repos/NCAR/xdev-bot-testing/issues/62',
            'xdev-bot-testing',
        ),
    ),
    (
        'https://github.com/NCAR/esmlab/issues/77',
        ('issues', 'https://api.github.com/repos/NCAR/esmlab/issues/77', 'esmlab'),
    ),
    (
        'Is your type really arbitrary? If you know it is just going to be a int float or string you could just do',
        ('manual', 'N/A', 'N/A'),
    ),
    ('https://blog.dask.org/2019/01/31/dask-mpi-experiment', ('manual', 'N/A', 'N/A')),
]


@pytest.mark.parametrize('note, expected', test_data)
def test_decipher_note(note, expected):
    results = decipher_note(note)
    assert expected == results


def test_read_database(DB='xdev-bot/test_database.csv'):
    df = read_database(DB)
    assert isinstance(df, pd.DataFrame)


def test_update_database():
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
    entry = {'card_id': [123], 'column_name': ['to-do']}
    df = pd.DataFrame(entry, columns=columns)
    temp_df = update_database(df, card_id=123, column_name='in-progress')
    expected = 'in-progress'
    results = temp_df.loc[temp_df['card_id'] == 123, 'column_name'].values[0]
    assert expected == results

    with pytest.raises(ValueError):
        temp_df = update_database(df, card_id=123, column_='to-do')

    with pytest.warns(UserWarning):
        temp_df = update_database(df, card_id=1000, column_name='done')


def test_get_card_data():
    card_payload_file = os.path.join(here, 'payloads_examples/card_moved.json')
    with open(card_payload_file) as f:
        event_data = json.load(f)

    card_data = get_card_data(event_data)
    assert isinstance(card_data, dict)
    assert len(card_data) > 1
