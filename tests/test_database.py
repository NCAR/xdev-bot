import s3fs
import pytest
import pandas as pd

from xdev_bot.database import CardDB

S3FS = s3fs.S3FileSystem(anon=False)


def test_init_empty():
    cards = CardDB(index='id')
    assert isinstance(cards, CardDB)


def test_init_without_index_raises_index_error():
    with pytest.raises(IndexError):
        CardDB()


def test_len():
    cards = CardDB(index='id')
    assert len(cards) == 0


def test_add():
    card2 = {'id': 2, 'a': 1, 'b': 'c'}
    cards = CardDB(index='id')
    cards.add(card2)
    assert len(cards) == 1


def test_add_invalid_index():
    card2 = {'i': 2, 'a': 1, 'b': 'c'}
    cards = CardDB(index='id')
    with pytest.raises(IndexError):
        cards.add(card2)


def test_add_nonunique():
    cards = CardDB(index='id')
    card2a = {'id': 2, 'a': 1, 'b': 'c'}
    card2b = {'id': 2, 'a': 2, 'b': 'f'}
    cards.add(card2a)
    cards.add(card2b)
    assert len(cards) == 1
    assert cards[2] == card2b


def test_add_overwrite_element():
    cards = CardDB(index='id')
    card2 = {'id': 2, 'a': 1, 'b': 'c'}
    cards.add(card2)
    assert len(cards) == 1
    assert cards[2] == card2
    cards.add({'id': 2, 'a': 2})
    assert cards[2] == {'id': 2, 'a': 2, 'b': 'c'}


def test_init_single():
    card2 = {'id': 2, 'a': 1, 'b': 'c'}
    cards = CardDB(card2, index='id')
    assert len(cards) == 1


def test_getitem():
    card2 = {'id': 2, 'a': 1, 'b': 'c'}
    card3 = {'id': 3, 'a': 2, 'b': 'c'}
    card7 = {'id': 7, 'a': 2, 'b': 'f'}
    cards = CardDB(card2, card3, card7, index='id')

    assert cards[2] == card2
    assert cards[3] == card3
    assert cards[7] == card7
    assert cards[0] is None
    assert cards[1] is None


def test_setitem():
    cards = CardDB(index='id')
    cards[3] = {'id': 2, 'a': 1, 'b': 'c'}
    assert cards[3] == {'id': 3, 'a': 1, 'b': 'c'}
    cards[3] = {'c': 4.5}
    assert len(cards) == 1
    assert cards[3] == {'id': 3, 'a': 1, 'b': 'c', 'c': 4.5}


def test_init_database_with_invalid_index():
    card = {'a': 1, 'b': 'c'}
    with pytest.raises(IndexError):
        CardDB(card, index='id')


def test_remove():
    card2 = {'id': 2, 'a': 1, 'b': 'c'}
    card3 = {'id': 3, 'a': 2, 'b': 'c'}
    card7 = {'id': 7, 'a': 2, 'b': 'f'}
    cards = CardDB(card2, card3, card7, index='id')
    assert len(cards) == 3
    cards.remove(card3)
    assert len(cards) == 2
    assert cards[2] == card2
    assert cards[3] is None
    assert cards[7] == card7


def test_remove_not_found():
    cards = CardDB(index='id')

    with pytest.raises(KeyError):
        cards.remove({'id': 2, 'a': 1, 'b': 'c'})

    with pytest.raises(KeyError):
        cards.remove({'a': 1, 'b': 'c'})


def test_remove_only_matching_index():
    card2 = {'id': 2, 'a': 1, 'b': 'c'}
    card3 = {'id': 3, 'a': 2, 'b': 'c'}
    card7 = {'id': 7, 'a': 2, 'b': 'f'}
    cards = CardDB(card2, card3, card7, index='id')
    assert len(cards) == 3
    cards.remove({'id': 3})
    assert len(cards) == 2
    assert cards[2] == card2
    assert cards[3] is None
    assert cards[7] == card7


def test_save():
    s3fn = 'xdev-bot/test_database.csv'
    if S3FS.exists(s3fn):
        S3FS.rm(s3fn)
    cards = CardDB(index='id', s3filename=s3fn)
    assert not S3FS.exists(s3fn)
    card0 = {'id': 0, 'a': 1, 'b': 'c', 'd': 4.5}
    card3 = {'id': 3, 'a': 2, 'b': 'e', 'd': 8.5}
    card7 = {'id': 7, 'a': 2, 'b': 'c', 'd': -4.2}
    cards.add(card0)
    cards.add(card3)
    cards.add(card7)
    assert len(cards) == 3
    cards.remove(card3)
    cards.save()
    assert S3FS.exists(s3fn)
    with S3FS.open(s3fn, 'r') as f:
        df = pd.read_csv(f)
    assert cards._df.equals(df)
    cards2 = CardDB(index='id', s3filename=s3fn)
    assert cards._df.equals(cards2._df)
    if S3FS.exists(s3fn):
        S3FS.rm(s3fn)
