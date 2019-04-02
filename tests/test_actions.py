import os
import json

from gidgethub import sansio

from xdev_bot.actions import (get_create_card_ghargs, get_card_from_card_event, get_move_card_ghargs,
                              get_update_status_ghargs, get_event_type, get_card_type,
                              save_card, save_merged_status, remove_card)
from xdev_bot.database import CardDB
from xdev_bot.gidgethub import GHArgs

PWD = os.path.abspath(os.path.dirname(__file__))


def test_get_create_card_ghargs():
    with open(os.path.join(PWD, 'payload_examples/issue_opened.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="issues", delivery_id="12345")

    ghargs = GHArgs('/projects/columns/4507386/cards',
                    data={'note': payload['issue']['html_url']},
                    accept='application/vnd.github.inertia-preview+json')
    assert get_create_card_ghargs(event) == ghargs


def test_get_move_card_ghargs():
    card = {'url': 'https://api.github.com/projects/columns/cards/18001901',
            'id': 18001901,
            'note': 'https://github.com/NCAR/xdev-bot-testing/issues/76',
            'column_url': 'https://api.github.com/projects/columns/4507386',
            'column_id': 4507386,
            'created_at': '2019-02-22T20:42:18Z',
            'updated_at': '2019-02-22T20:42:18Z',
            'creator': 'xdev-bot',
            'sender': 'xdev-bot',
            'column_name': 'to_do'}
    cards = CardDB(card, index='note')

    with open(os.path.join(PWD, 'payload_examples/issue_closed.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="issues", delivery_id="12345")

    ghargs = GHArgs('/projects/columns/cards/18001901/moves',
                    data={'position': 'top', 'column_id': 4_507_393},
                    accept='application/vnd.github.inertia-preview+json')
    assert get_move_card_ghargs(event, column='done', database=cards) == ghargs


def test_get_move_card_not_found_ghargs():
    cards = CardDB(index='note')

    with open(os.path.join(PWD, 'payload_examples/issue_closed.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="issues", delivery_id="12345")

    ghargs = GHArgs('/projects/columns/4507393/cards',
                    data={'note': payload['issue']['html_url']},
                    accept='application/vnd.github.inertia-preview+json')
    assert get_move_card_ghargs(event, column='done', database=cards) == ghargs


def test_save_new_card_and_remove():
    cards = CardDB(index='note')

    with open(os.path.join(PWD, 'payload_examples/card_created_issue.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="project_card", delivery_id="12345")

    card = get_card_from_card_event(event)

    save_card(event, database=cards)

    assert len(cards) == 1
    assert cards[card['note']] == card

    remove_card(event, database=cards)

    assert len(cards) == 0


def test_save_merged_status():
    cards = CardDB(index='note')

    with open(os.path.join(PWD, 'payload_examples/pull_request_opened.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="pull_request", delivery_id="12345")

    save_merged_status(event, database=cards)

    assert len(cards) == 1
    assert cards[event.data['pull_request']['html_url']]['merged'] == False


def test_get_update_issue_status_ghargs_no_change():
    card = {'note': 'https://github.com/NCAR/xdev-bot-testing/issues/11',
            'column_name': 'to_do', 'merged': None}
    cards = CardDB(card, index='note')

    with open(os.path.join(PWD, 'payload_examples/card_created_issue.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="project_card", delivery_id="12345")

    assert get_update_status_ghargs(event, database=cards) is None


def test_get_update_issue_status_ghargs_opened():
    card = {'note': 'https://github.com/NCAR/xdev-bot-testing/issues/11',
            'column_name': 'done', 'merged': None}
    cards = CardDB(card, index='note')

    with open(os.path.join(PWD, 'payload_examples/card_created_issue.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="project_card", delivery_id="12345")

    ghargs = GHArgs('https://api.github.com/repos/NCAR/xdev-bot-testing/issues/11',
                    data={'state': 'open'}, func='patch')
    assert get_update_status_ghargs(event, database=cards) == ghargs


def test_get_update_pull_status_ghargs_other():
    with open(os.path.join(PWD, 'payload_examples/card_created_other.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="project_card", delivery_id="12345")

    assert get_update_status_ghargs(event) is None


def test_get_card_issue():
    with open(os.path.join(PWD, 'payload_examples/card_created_issue.json')) as f:
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
            'sender': 'xdev-bot',
            'column_name': 'to_do',
            'type': 'issue'}
    assert get_card_from_card_event(event) == card

    assert get_card_type(card) == 'issue'


def test_get_card_pr():
    with open(os.path.join(PWD, 'payload_examples/card_created_pr.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="project_card", delivery_id="12345")

    card = {'url': 'https://api.github.com/projects/columns/cards/19522950',
            'id': 19522950,
            'note': 'https://github.com/NCAR/xdev-bot-testing/pull/91',
            'column_url': 'https://api.github.com/projects/columns/4507392',
            'column_id': 4507392,
            'created_at': '2019-03-28T22:26:13Z',
            'updated_at': '2019-03-28T22:26:13Z',
            'creator': 'xdev-bot',
            'sender': 'xdev-bot',
            'column_name': 'in_progress',
            'type': 'pull_request'}
    assert get_card_from_card_event(event) == card

    assert get_card_type(card) == 'pull_request'


def test_get_card_other():
    with open(os.path.join(PWD, 'payload_examples/card_created_other.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="project_card", delivery_id="12345")

    card = {'url': 'https://api.github.com/projects/columns/cards/18001901',
            'id': 18001901,
            'note': 'Just some text',
            'column_url': 'https://api.github.com/projects/columns/4507386',
            'column_id': 4507386,
            'created_at': '2019-02-22T20:42:18Z',
            'updated_at': '2019-02-22T20:42:18Z',
            'creator': 'xdev-bot',
            'sender': 'xdev-bot',
            'column_name': 'to_do',
            'type': None}
    assert get_card_from_card_event(event) == card

    assert get_card_type(card) is None


def test_get_event_type():
    with open(os.path.join(PWD, 'payload_examples/issue_opened.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="issues", delivery_id="12345")

    assert get_event_type(event) == 'issue'

    with open(os.path.join(PWD, 'payload_examples/pull_request_opened.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="pull_request", delivery_id="12345")

    assert get_event_type(event) == 'pull_request'

    with open(os.path.join(PWD, 'payload_examples/card_created_other.json')) as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="project_card", delivery_id="12345")

    assert get_event_type(event) is None
