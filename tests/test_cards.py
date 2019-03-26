import os
import json

from gidgethub import sansio

from xdev_bot.cards import create_new_card, get_card_properties, move_card
from xdev_bot.database import CardDB

PWD = os.path.abspath(os.path.dirname(__file__))


def test_create_new_card():
    with open(os.path.join(PWD, 'payload_examples/issue_opened.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="issues", delivery_id="12345")

    url, data = create_new_card(event)
    assert url == '/projects/columns/4507386/cards'
    assert data == {'note': payload['issue']['html_url']}


def test_get_card_properties():
    with open(os.path.join(PWD, 'payload_examples/card_created.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="project_card", delivery_id="12345")

    properties = {'url': 'https://api.github.com/projects/columns/cards/18001901',
                  'id': 18001901,
                  'note': 'https://github.com/NCAR/xdev-bot-testing/issues/11',
                  'column_url': 'https://api.github.com/projects/columns/4507386',
                  'column_id': 4507386,
                  'created_at': '2019-02-22T20:42:18Z',
                  'updated_at': '2019-02-22T20:42:18Z',
                  'creator': 'xdev-bot',
                  'mover': 'xdev-bot',
                  'column_name': 'to_do'}
    assert get_card_properties(event) == properties


def test_move_card():
    card = {'url': 'https://api.github.com/projects/columns/cards/18001901',
            'id': 18001901,
            'note': 'https://github.com/NCAR/xdev-bot-testing/issues/76',
            'column_url': 'https://api.github.com/projects/columns/4507386',
            'column_id': 4507386,
            'created_at': '2019-02-22T20:42:18Z',
            'updated_at': '2019-02-22T20:42:18Z',
            'creator': 'xdev-bot',
            'mover': 'xdev-bot',
            'column_name': 'to_do'}
    cards = CardDB(card)

    with open(os.path.join(PWD, 'payload_examples/issue_closed.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="issues", delivery_id="12345")

    url, data = move_card(event, column='done', database=cards)
    assert url == '/projects/columns/cards/18001901/moves'
    assert data == {'position': 'top', 'column_id': 4_507_393}


def test_move_card_not_found():
    cards = CardDB()

    with open(os.path.join(PWD, 'payload_examples/issue_closed.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="issues", delivery_id="12345")

    url, data = move_card(event, column='done', database=cards)
    assert url == '/projects/columns/4507393/cards'
    assert data == {'note': payload['issue']['html_url']}
