import s3fs
import pandas as pd


class CardDB(object):

    def __init__(self):
        self._df = pd.DataFrame()

    def append(self, **props):
        self._df = self._df.append(props, ignore_index=True)

    def __getitem__(self, card_id):
        return self._df.iloc[card_id].to_dict()

    def where(self, **kwds):
        df = self._df
        for k in kwds:
            df = df.loc[df[k] == kwds[k]]
        return df.to_dict('records')

    def __len__(self):
        return len(self._df)

    @property
    def dataframe(self):
        return self._df


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

    def append(self, **props):
        super().append(**props)
        with self._s3.open(self._fn, 'w') as f:
            self._df.to_csv(f, index=False)


PROJECT_CARDS = S3CardDB('xdev-bot/database.csv')
