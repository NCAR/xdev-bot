import s3fs
import pytest
import pandas as pd

from xdev_bot.database import CardDB, S3CardDB

S3 = s3fs.S3FileSystem(anon=False)


def test_init_empty_card_db():
    cards = CardDB()
    assert type(cards) is CardDB
    assert len(cards) == 0


def test_init_card_db():
    card0 = {'id': 0, 'a': 1, 'b': 'c', 'd': 4.5}
    card1 = {'id': 3, 'a': 2, 'b': 'e', 'd': 8.5}
    card2 = {'id': 7, 'a': 2, 'b': 'c', 'd': -4.2}
    cards = CardDB(card0, card1, card2)
    assert type(cards) is CardDB
    assert len(cards) == 3


def test_append_to_card_db():
    cards = CardDB()
    card0 = {'id': 0, 'a': 1, 'b': 'c', 'd': 4.5}
    card1 = {'id': 3, 'a': 2, 'b': 'e', 'd': 8.5}
    card2 = {'id': 7, 'a': 2, 'b': 'c', 'd': -4.2}
    cards.append(card0)
    assert cards[0] == card0
    assert len(cards) == 1
    cards.append(card1, card2)
    assert cards[1] == card1
    assert cards[2] == card2
    assert len(cards) == 3


def test_where_in_card_db():
    card0 = {'id': 0, 'a': 1, 'b': 'c', 'd': 4.5}
    card1 = {'id': 3, 'a': 2, 'b': 'e', 'd': 8.5}
    card2 = {'id': 7, 'a': 2, 'b': 'c', 'd': -4.2}
    cards = CardDB(card0, card1, card2)
    idx = cards.where(b='c')
    assert set(idx) == {0, 2}
    idx = cards.where(b='c', a=1)
    assert set(idx) == {0}
    idx = cards.where(id=3)
    assert set(idx) == {1}
    idx = cards.where(id=1111)
    assert set(idx) == set()
    idx = cards.where(x=4)
    assert set(idx) == set()


def test_getitem_of_card_db():
    card0 = {'id': 0, 'a': 1, 'b': 'c', 'd': 4.5}
    card1 = {'id': 3, 'a': 2, 'b': 'e', 'd': 8.5}
    card2 = {'id': 7, 'a': 2, 'b': 'c', 'd': -4.2}
    cards = CardDB(card0, card1, card2)
    assert cards[0] == card0
    idx = cards.where(id=3)
    assert cards[idx] == card1
    idx = cards.where(b='c')
    assert cards[idx] == [card0, card2]


def test_setitem_of_card_db():
    card0 = {'id': 0, 'a': 1, 'b': 'c', 'd': 4.5}
    card1 = {'id': 3, 'a': 2, 'b': 'e', 'd': 8.5}
    card2 = {'id': 7, 'a': 2, 'b': 'c', 'd': -4.2}
    cards = CardDB(card0, card1, card2)
    card1b = {'id': 3, 'a': 3, 'b': 'g', 'd': 6.3}
    idx = cards.where(id=3)
    cards[idx] = card1b
    assert cards[1] == card1b


def test_update_card_in_db():
    card0 = {'id': 0, 'a': 1, 'b': 'c', 'd': 4.5}
    card1 = {'id': 3, 'a': 2, 'b': 'e', 'd': 8.5}
    card2 = {'id': 7, 'a': 2, 'b': 'c', 'd': -4.2}
    cards = CardDB(card0, card1, card2)
    card1b = {'id': 3, 'a': 3, 'b': 'g', 'd': 6.3}
    cards.update(card1b, key='id')
    assert cards[1] == card1b


@pytest.fixture
def s3fn():
    fn = 'xdev-bot/test_database.csv'
    if S3.exists(fn):
        S3.rm(fn)
    yield fn
    if S3.exists(fn):
        S3.rm(fn)


def test_init_s3_card_db(s3fn):
    cards = S3CardDB(s3fn)
    assert not S3.exists(s3fn)
    card0 = {'id': 0, 'a': 1, 'b': 'c', 'd': 4.5}
    card1 = {'id': 3, 'a': 2, 'b': 'e', 'd': 8.5}
    card2 = {'id': 7, 'a': 2, 'b': 'c', 'd': -4.2}
    cards.append(card0, card1, card2)
    assert len(cards) == 3
    assert S3.exists(s3fn)
    with S3.open(s3fn, 'r') as f:
        df = pd.read_csv(f)
    assert cards.dataframe.equals(df)
    cards2 = S3CardDB(s3fn)
    assert cards.dataframe.equals(cards2.dataframe)
