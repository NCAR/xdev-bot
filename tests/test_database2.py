import pytest

from xdev_bot.database2 import CardDB


def test_init_empty():
    cards = CardDB()
    assert isinstance(cards, CardDB)


def test_len():
    cards = CardDB()
    assert len(cards) == 0


def test_add():
    card0 = {'id': 2, 'a': 1, 'b': 'c'}
    cards = CardDB()
    cards.add(card0)
    assert len(cards) == 1


def test_add_invalid_index():
    card0 = {'i': 2, 'a': 1, 'b': 'c'}
    cards = CardDB()
    with pytest.raises(IndexError):
        cards.add(card0)


def test_add_nonunique():
    cards = CardDB()
    card0 = {'id': 2, 'a': 1, 'b': 'c'}
    card1 = {'id': 2, 'a': 2, 'b': 'f'}
    cards.add(card0)
    cards.add(card1)
    assert len(cards) == 1
    assert cards[2] == card1


def test_init_single():
    card0 = {'id': 2, 'a': 1, 'b': 'c'}
    cards = CardDB(card0)
    assert len(cards) == 1


def test_getitem():
    card0 = {'id': 2, 'a': 1, 'b': 'c'}
    card1 = {'id': 3, 'a': 2, 'b': 'c'}
    card2 = {'id': 7, 'a': 2, 'b': 'f'}
    cards = CardDB(card0, card1, card2, index='id')

    assert cards[2] == card0
    assert cards[3] == card1
    assert cards[7] == card2
    assert cards[0] is None
    assert cards[1] is None


def test_init_database_with_invalid_index():
    card0 = {'a': 1, 'b': 'c'}
    with pytest.raises(IndexError):
        CardDB(card0, index='id')


def test_remove():
    card0 = {'id': 2, 'a': 1, 'b': 'c'}
    card1 = {'id': 3, 'a': 2, 'b': 'c'}
    card2 = {'id': 7, 'a': 2, 'b': 'f'}
    cards = CardDB(card0, card1, card2, index='id')
    assert len(cards) == 3
    cards.remove(card1)
    assert len(cards) == 2
    assert cards[2] == card0
    assert cards[3] is None
    assert cards[7] == card2
