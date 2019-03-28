import pandas as pd


class CardDB(object):
    """Database for cards on the project board"""

    def __init__(self, *cards, index='id'):
        self._df = pd.DataFrame()
        self._index = index
        for card in cards:
            self.add(card)

    def __len__(self):
        return len(self._df)

    def __getitem__(self, item):
        if len(self._df) == 0:
            return None
        elif self._index in self._df:
            df = self._df[self._df[self._index] == item]
            return df.iloc[0].to_dict() if len(df) == 1 else None
        else:
            raise IndexError(f'Index {self._index} not found in database')

    def add(self, card):
        if self._index not in card:
            raise IndexError(f'Index {self._index} not present in card {card}')
        elif self[card[self._index]] is None:
            self._df = self._df.append(card, ignore_index=True)
        else:
            idx = self._df[self._df[self._index] == card[self._index]].index
            self._df.iloc[idx] = [card[col] for col in self._df.columns]

    def remove(self, card):
        if self._index not in card or self[card[self._index]] != card:
            raise KeyError(f'Card {card} not found in database')
        idx = self._df[self._df[self._index] == card[self._index]].index
        self._df = self._df.drop(idx).reset_index(drop=True)
