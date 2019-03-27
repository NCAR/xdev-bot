class GHArgs(object):

    def __init__(self, url, data=None):
        self._url = url
        self._data = {} if data is None else data

    @property
    def url(self):
        return self._url

    @property
    def data(self):
        return self._data

    def __eq__(self, other):
        if not isinstance(other, GHArgs):
            return False
        else:
            return self.url == other.url and self.data == other.data
