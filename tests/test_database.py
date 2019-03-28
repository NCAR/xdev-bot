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
    card0 = {'id': 2, 'a': 1, 'b': 'c'}
    cards = CardDB(index='id')
    cards.add(card0)
    assert len(cards) == 1


def test_add_invalid_index():
    card0 = {'i': 2, 'a': 1, 'b': 'c'}
    cards = CardDB(index='id')
    with pytest.raises(IndexError):
        cards.add(card0)


def test_add_nonunique():
    cards = CardDB(index='id')
    card0 = {'id': 2, 'a': 1, 'b': 'c'}
    card1 = {'id': 2, 'a': 2, 'b': 'f'}
    cards.add(card0)
    cards.add(card1)
    assert len(cards) == 1
    assert cards[2] == card1


def test_init_single():
    card0 = {'id': 2, 'a': 1, 'b': 'c'}
    cards = CardDB(card0, index='id')
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


def test_remove_only_matching_index():
    card0 = {'id': 2, 'a': 1, 'b': 'c'}
    card1 = {'id': 3, 'a': 2, 'b': 'c'}
    card2 = {'id': 7, 'a': 2, 'b': 'f'}
    cards = CardDB(card0, card1, card2, index='id')
    assert len(cards) == 3
    cards.remove({'id': 3})
    assert len(cards) == 2
    assert cards[2] == card0
    assert cards[3] is None
    assert cards[7] == card2


def test_s3_backend():
    s3fn = 'xdev-bot/test_database.csv'
    if S3FS.exists(s3fn):
        S3FS.rm(s3fn)
    cards = CardDB(index='id', s3filename=s3fn)
    assert not S3FS.exists(s3fn)
    card0 = {'id': 0, 'a': 1, 'b': 'c', 'd': 4.5}
    card1 = {'id': 3, 'a': 2, 'b': 'e', 'd': 8.5}
    card2 = {'id': 7, 'a': 2, 'b': 'c', 'd': -4.2}
    cards.add(card0)
    cards.add(card1)
    cards.add(card2)
    assert len(cards) == 3
    cards.remove(card1)
    assert S3FS.exists(s3fn)
    with S3FS.open(s3fn, 'r') as f:
        df = pd.read_csv(f)
    assert cards._df.equals(df)
    cards2 = CardDB(index='id', s3filename=s3fn)
    assert cards._df.equals(cards2._df)
    if S3FS.exists(s3fn):
        S3FS.rm(s3fn)
