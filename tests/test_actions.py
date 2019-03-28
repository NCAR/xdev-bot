import os
import json

from gidgethub import sansio

from xdev_bot.actions import (create_card, get_card, move_card, update_issue,
                              card_is_issue, card_is_pull_request, get_event_type)
from xdev_bot.database import CardDB
from xdev_bot.gidgethub import GHArgs

PWD = os.path.abspath(os.path.dirname(__file__))


def test_get_card():
    with open(os.path.join(PWD, 'payload_examples/card_created.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="project_card", delivery_id="12345")

    card = {'url': 'https://api.github.com/projects/columns/cards/18001901',
            'id': 18001901,
            'note': 'https://github.com/NCAR/xdev-bot-testing/issues/11',
            'column_url': 'https://api.github.com/projects/columns/4507386',
            'column_id': 4507386,
            'created_at': '2019-02-22T20:42:18Z',
            'updated_at': '2019-02-22T20:42:18Z',
            'creator': 'xdev-bot',
            'mover': 'xdev-bot',
            'column_name': 'to_do',
            'type': 'issue'}
    assert get_card(event) == card


def test_card_is_issue():
    card = {'type': 'issue'}
    assert card_is_issue(card)
    card = {'type': 'pull_request'}
    assert not card_is_issue(card)


def test_card_is_pull_request():
    card = {'type': 'issue'}
    assert not card_is_pull_request(card)
    card = {'type': 'pull_request'}
    assert card_is_pull_request(card)


def test_create_new_card():
    with open(os.path.join(PWD, 'payload_examples/issue_opened.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="issues", delivery_id="12345")

    ghargs = GHArgs('/projects/columns/4507386/cards',
                    data={'note': payload['issue']['html_url']},
                    accept='application/vnd.github.inertia-preview+json')
    assert create_card(event) == ghargs


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
    cards = CardDB(card, index='note')

    with open(os.path.join(PWD, 'payload_examples/issue_closed.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="issues", delivery_id="12345")

    ghargs = GHArgs('/projects/columns/cards/18001901/moves',
                    data={'position': 'top', 'column_id': 4_507_393},
                    accept='application/vnd.github.inertia-preview+json')
    assert move_card(event, column='done', database=cards) == ghargs


def test_move_card_not_found():
    cards = CardDB(index='note')

    with open(os.path.join(PWD, 'payload_examples/issue_closed.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="issues", delivery_id="12345")

    ghargs = GHArgs('/projects/columns/4507393/cards',
                    data={'note': payload['issue']['html_url']},
                    accept='application/vnd.github.inertia-preview+json')
    assert move_card(event, column='done', database=cards) == ghargs


def test_get_event_type():
    with open(os.path.join(PWD, 'payload_examples/issue_opened.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="project_card", delivery_id="12345")

    assert get_event_type(event) == 'issue'

    with open(os.path.join(PWD, 'payload_examples/pull_request_opened.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="project_card", delivery_id="12345")

    assert get_event_type(event) == 'pull_request'


def test_update_issue():
    card = {'note': 'https://github.com/NCAR/xdev-bot-testing/issues/11'}

    ghargs = GHArgs('https://api.github.com/repos/NCAR/xdev-bot-testing/issues/11')
    assert update_issue(card) == ghargs

    ghargs = GHArgs('https://api.github.com/repos/NCAR/xdev-bot-testing/issues/11',
                    data={'state': 'open'})
    assert update_issue(card, state='open') == ghargs
