import s3fs
import pytest
import pandas as pd

from xdev_bot.database import CardDB, S3CardDB

S3 = s3fs.S3FileSystem(anon=False)


def test_init_card_db():
    cards = CardDB()
    assert type(cards) is CardDB


def test_append_new_card():
    cards = CardDB()
    assert len(cards) == 0
    card0 = {'a': 1, 'b': 'c', 'd': 4.5}
    cards.append(**card0)
    assert cards[0] == card0
    assert len(cards) == 1


def test_cards_where():
    cards = CardDB()
    card0 = {'id': 345, 'a': 1, 'b': 'c', 'd': 4.5}
    cards.append(**card0)
    card1 = {'id': 475, 'a': 2, 'b': 'd', 'd': 5.6}
    cards.append(**card1)
    card2 = {'id': 821, 'a': 3, 'b': 'c', 'd': 7.3}
    cards.append(**card2)
    assert cards.where(b='c') == [card0, card2]
    assert cards.where(b='c', a=1) == [card0]
    assert len(cards) == 3


def test_find_card():
    cards = CardDB()
    card0 = {'id': 345, 'a': 1, 'b': 'c', 'd': 4.5}
    cards.append(**card0)
    card1 = {'id': 475, 'a': 2, 'b': 'd', 'd': 5.6}
    cards.append(**card1)
    card2 = {'id': 821, 'a': 3, 'b': 'c', 'd': 7.3}
    cards.append(**card2)
    assert cards.find(id=345) == card0
    assert cards.find(id=379) is None


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
    card0 = {'a': 1, 'b': 'c', 'd': 4.5}
    cards.append(**card0)
    card1 = {'a': 2, 'b': 'd', 'd': 5.6}
    cards.append(**card1)
    card2 = {'a': 3, 'b': 'c', 'd': 7.3}
    cards.append(**card2)
    assert len(cards) == 3
    assert S3.exists(s3fn)
    with S3.open(s3fn, 'r') as f:
        df = pd.read_csv(f)
    assert cards.dataframe.equals(df)
    cards2 = S3CardDB(s3fn)
    assert cards.dataframe.equals(cards2.dataframe)
