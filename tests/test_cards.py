import os
import json

from gidgethub import sansio

from xdev_bot.cards import create_new_card, get_card_properties

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
    event = sansio.Event(payload, event="issues", delivery_id="12345")

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
