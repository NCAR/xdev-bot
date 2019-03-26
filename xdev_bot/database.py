import s3fs
import pandas as pd


class CardDB(object):

    def __init__(self, *cards):
        self._df = pd.DataFrame(cards)

    def __getitem__(self, index):
        cards = self._df.iloc[index]
        if isinstance(cards, pd.DataFrame):
            cards = cards.to_dict('records')
            return cards[0] if len(cards) == 1 else cards
        else:
            return cards.to_dict()

    def __len__(self):
        return len(self._df)

    @property
    def dataframe(self):
        return self._df

    def append(self, *cards):
        for card in cards:
            self._df = self._df.append(card, ignore_index=True, sort=True)

    def where(self, **values):
        df = self._df
        for column in values:
            value = values[column]
            df = df[df[column] == value]
        return df.index


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

    def append(self, *cards):
        super().append(*cards)
        with self._s3.open(self._fn, 'w') as f:
            self._df.to_csv(f, index=False)


PROJECT_CARDS = S3CardDB('xdev-bot/database.csv')
