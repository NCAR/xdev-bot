class GHArgs(object):

    def __init__(self, url, data=None, accept=None):
        self._url = url
        self._data = {} if data is None else data
        self._accept = accept

    @property
    def url(self):
        return self._url

    @property
    def data(self):
        return self._data

    @property
    def accept(self):
        return self._accept

    @property
    def kwargs(self):
        kwds = {'data': self.data}
        if self.accept is not None:
            kwds['accept'] = self.accept
        return kwds

    def __eq__(self, other):
        if not isinstance(other, GHArgs):
            return False
        else:
            return self.url == other.url and self.data == other.data and self.accept == other.accept
