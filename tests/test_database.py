from xdev_bot.database import CardDB


def test_init_card_db():
    cards = CardDB()
    assert type(cards) is CardDB


def test_append_new_card():
    cards = CardDB()
    card_info = {'a': 1, 'b': 'c', 'd': 4.5}
    cards.append(**card_info)
    assert cards[0] == card_info


def test_get_card_info_by_value():
    cards = CardDB()
    card0 = {'a': 1, 'b': 'c', 'd': 4.5}
    cards.append(**card0)
    card1 = {'a': 2, 'b': 'd', 'd': 5.6}
    cards.append(**card1)
    card2 = {'a': 3, 'b': 'c', 'd': 7.3}
    cards.append(**card2)
    assert cards.where(b='c') == [card0, card2]
