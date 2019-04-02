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


def test_init_set_accept():
    url = 'https://github.com/NCAR/xdev-bot'
    data = {'note': 'https://github.com/NCAR/xdev-bot/issues/11111'}
    accept = 'application/vnd.github.inertia-preview+json'
    ghargs = GHArgs(url, data=data, accept=accept)
    assert ghargs.url == url
    assert ghargs.data == data
    assert ghargs.accept == accept


def test_kwargs_with_accept():
    url = 'https://github.com/NCAR/xdev-bot'
    data = {'note': 'https://github.com/NCAR/xdev-bot/issues/11111'}
    accept = 'application/vnd.github.inertia-preview+json'
    ghargs = GHArgs(url, data=data, accept=accept)
    assert ghargs.url == url
    assert ghargs.data == data
    assert ghargs.accept == accept
    assert ghargs.kwargs == {'data': data, 'accept': accept}


def test_kwargs_without_accept():
    url = 'https://github.com/NCAR/xdev-bot'
    data = {'note': 'https://github.com/NCAR/xdev-bot/issues/11111'}
    ghargs = GHArgs(url, data=data)
    assert ghargs.url == url
    assert ghargs.data == data
    assert ghargs.kwargs == {'data': data}


def test_func():
    url = 'https://github.com/NCAR/xdev-bot'
    data = {'note': 'https://github.com/NCAR/xdev-bot/issues/11111'}
    func = 'patch'
    ghargs = GHArgs(url, data=data, func=func)
    assert ghargs.url == url
    assert ghargs.data == data
    assert ghargs.func == func


def test_equals():
    url = 'https://github.com/NCAR/xdev-bot'
    data = {'note': 'https://github.com/NCAR/xdev-bot/issues/11111'}
    accept = 'application/vnd.github.inertia-preview+json'
    ghargs1 = GHArgs(url, data=data, accept=accept)
    ghargs2 = GHArgs(url, data=data, accept=accept)
    assert ghargs1 == ghargs2
