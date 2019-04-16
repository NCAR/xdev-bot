import s3fs
import pandas as pd

S3FS = s3fs.S3FileSystem(anon=False)


class CardDB(object):
    """Database for cards on the project board"""

    def __init__(self, *cards, index=None, s3filename=None):
        if index is None:
            raise IndexError(f'Must set an unique index column name')
        self._idxcol = index
        self._s3fn = s3filename
        self._df = self._read() if s3filename else pd.DataFrame()
        for card in cards:
            self.add(card)

    def __len__(self):
        return len(self._df)

    def __getitem__(self, index):
        if len(self._df) == 0:
            return None
        elif self._idxcol in self._df:
            df = self._df[self._df[self._idxcol] == index]
            return df.iloc[0].to_dict() if len(df) == 1 else None
        else:
            raise IndexError(f'Index {self._idxcol} not found in database')

    def __setitem__(self, index, card):
        _card = card.copy()
        _card[self._idxcol] = index
        if self[index] is None:
            self._df = self._df.append(_card, ignore_index=True)
        else:
            card_cols = set(_card)
            for col in card_cols.difference(self._df.columns):
                self._df[col] = None
            for col in card_cols:
                i_row = self._df[self._df[self._idxcol] == index].index
                j_col = self._df.columns.get_loc(col)
                self._df.iloc[i_row, j_col] = _card[col]

    def add(self, card):
        if self._idxcol not in card:
            raise IndexError(f'Index {self._idxcol} not present in card {card}')
        else:
            index = card[self._idxcol]
            self[index] = card

    def remove(self, card):
        if self._idxcol not in card or self[card[self._idxcol]] is None:
            raise KeyError(f'Card {card} not found in database')
        idx = self._df[self._df[self._idxcol] == card[self._idxcol]].index
        self._df = self._df.drop(idx).reset_index(drop=True)

    def search(self, **kwargs):
        if not all([kwarg in self._df for kwarg in kwargs]):
            return []
        df = self._df
        for kwarg in kwargs:
            df = df.loc[df[kwarg] == kwargs[kwarg]]
        return df.to_dict('records')

    def _read(self):
        try:
            if S3FS.exists(self._s3fn):
                print(f'Initializing database from file {self._s3fn} on Amazon S3')
                with S3FS.open(self._s3fn, 'r') as f:
                    return pd.read_csv(f)
            else:
                return pd.DataFrame()
        except Exception:
            raise

    def save(self):
        if self._s3fn:
            print(f'Saving database to file {self._s3fn} on Amazon S3')
            with S3FS.open(self._s3fn, 'w') as f:
                self._df.to_csv(f, index=False)


PROJECT_CARDS = CardDB(index='note', s3filename='xdev-bot/database.csv')
