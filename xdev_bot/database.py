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


PROJECT_CARDS = CardDB()
