import pytest

from xdev_bot.helpers import decipher_note


@pytest.mark.parametrize(
    'note, expected',
    [
        (
            'https://github.com/NCAR/xdev-bot-testing/pull/62',
            (
                'pull',
                'https://api.github.com/repos/NCAR/xdev-bot-testing/issues/62',
                'xdev-bot-testing',
            ),
        ),
        (
            'https://github.com/NCAR/esmlab/issues/77',
            ('issues', 'https://api.github.com/repos/NCAR/esmlab/issues/77', 'esmlab'),
        ),
        (
            'Is your type really arbitrary? If you know it is just going to be a int float or string you could just do',
            ('manual', 'N/A', 'N/A'),
        ),
        ('https://blog.dask.org/2019/01/31/dask-mpi-experiment', ('manual', 'N/A', 'N/A')),
    ],
)
def test_decipher_note(note, expected):
    results = decipher_note(note)
    assert expected == results
