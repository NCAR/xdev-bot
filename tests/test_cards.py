import os
import json

from gidgethub import sansio

from xdev_bot.cards import create_new_card

PWD = os.path.abspath(os.path.dirname(__file__))


def test_create_new_card():
    with open(os.path.join(PWD, 'payload_examples/issue_opened.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="issues", delivery_id="12345")

    url, data = create_new_card(event)
    assert url == '/projects/columns/4507386/cards'
    assert data == {'note': payload['issue']['html_url']}
