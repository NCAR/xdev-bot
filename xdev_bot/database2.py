import s3fs
import pandas as pd

S3FS = s3fs.S3FileSystem(anon=False)


class CardDB(object):
    """Database for cards on the project board"""

    def __init__(self, *cards, index=None, s3filename=None):
        if index is None:
            raise IndexError(f'Must set an unique index column name')
        self._index = index
        self._s3fn = s3filename
        self._df = self._read() if s3filename else pd.DataFrame()
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
        if self._s3fn:
            self._save()

    def remove(self, card):
        if self._index not in card or self[card[self._index]] != card:
            raise KeyError(f'Card {card} not found in database')
        idx = self._df[self._df[self._index] == card[self._index]].index
        self._df = self._df.drop(idx).reset_index(drop=True)
        if self._s3fn:
            self._save()

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

    def _save(self):
        print(f'Saving database to file {self._s3fn} on Amazon S3')
        with S3FS.open(self._s3fn, 'w') as f:
            self._df.to_csv(f, index=False)
