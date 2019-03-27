from xdev_bot.gidgethub import GHArgs


def test_init():
    url = 'https://github.com/NCAR/xdev-bot'
    ghargs = GHArgs(url)
    assert ghargs.url == url


def test_init_set_data():
    url = 'https://github.com/NCAR/xdev-bot'
    data = {'note': 'https://github.com/NCAR/xdev-bot/issues/11111'}
    ghargs = GHArgs(url, data=data)
    assert ghargs.url == url
    assert ghargs.data == data


def test_equals():
    url = 'https://github.com/NCAR/xdev-bot'
    data = {'note': 'https://github.com/NCAR/xdev-bot/issues/11111'}
    ghargs1 = GHArgs(url, data=data)
    ghargs2 = GHArgs(url, data=data)
    assert ghargs1 == ghargs2
