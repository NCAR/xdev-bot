import s3fs
import pandas as pd


class CardDB(object):

    def __init__(self, *cards):
        self._df = pd.DataFrame(cards)

    def __getitem__(self, index):
        cards = self.dataframe.iloc[index]
        if isinstance(cards, pd.DataFrame):
            cards = cards.to_dict('records')
            return cards[0] if len(cards) == 1 else cards
        else:
            return cards.to_dict()

    def __setitem__(self, index, card):
        self.dataframe.iloc[index] = [card[col] for col in self.dataframe.columns]

    def __len__(self):
        return len(self.dataframe)

    @property
    def dataframe(self):
        return self._df

    def append(self, card):
        self._df = self.dataframe.append(card, ignore_index=True, sort=True)

    def where(self, **values):
        df = self.dataframe
        for column in values:
            if column in df:
                value = values[column]
                df = df[df[column] == value]
            else:
                df = pd.DataFrame()
        return df.index

    def update(self, card, key='id'):
        if len(self) == 0:
            self.append(card)
            return
        if key not in self.dataframe:
            raise KeyError(f'key {key} not in database')
        kwargs = {key: card[key]}
        idx = self.where(**kwargs)
        if len(idx) == 0:
            self.append(card)
        else:
            self[idx] = card

    def remove(self, card, key='id'):
        if len(self) == 0:
            raise KeyError(f'cannot remove card from empty database')
        if key not in self.dataframe:
            raise KeyError(f'key {key} not in database')
        kwargs = {key: card[key]}
        idx = self.where(**kwargs)
        if len(idx) == 0:
            raise KeyError(f'card with key {key} {card[key]} not found')
        else:
            self._df = self._df.drop(idx).reset_index(drop=True)


class S3CardDB(CardDB):

    def __init__(self, filename):
        super(S3CardDB, self).__init__()
        self._fn = filename
        self._s3 = s3fs.S3FileSystem(anon=False)
        try:
            if self._s3.exists(self._fn):
                with self._s3.open(self._fn, 'r') as f:
                    self._df = pd.read_csv(f)
            else:
                self._df = pd.DataFrame()
        except Exception:
            raise

    def _save(self):
        print(f'Updating database file {self._fn} on Amazon S3')
        with self._s3.open(self._fn, 'w') as f:
            self._df.to_csv(f, index=False)

    def __setitem__(self, index, card):
        super().__setitem__(index, card)
        self._save()

    def append(self, *cards):
        super().append(*cards)
        self._save()

    def remove(self, card, key='id'):
        super().remove(card, key=key)
        self._save()


PROJECT_CARDS = S3CardDB('xdev-bot/database.csv')
