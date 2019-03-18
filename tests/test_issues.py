import pytest
import json

from gidgethub import sansio

from xdev_bot import issues


class FakeGH:

    def __init__(self, *, getitem=None, post=None):
        self._getitem_return = getitem
        self.patch_url = None
        self.patch_data = None
        self.delete_url = None
        self.delete_data = None
        self.data = None
        self._post_return = post
        self.post_url = []
        self.post_data = []

    async def patch(self, url, data):
        self.patch_url = url
        self.patch_data = data

    async def delete(self, url, data):
        self.delete_url = url
        self.delete_data = data

    async def post(self, url, *, data):
        self.post_url.append(url)
        self.post_data.append(data)
        return self._post_return


@pytest.mark.asyncio
async def test_card_created_on_opened_issue():
    with open('payload_examples/issue_opened.json') as f:
        payload = json.load(f)
    event = sansio.Event(payload, event="pull_request", delivery_id="12345")

    # FILL THE REST IN HERE

    # pr_data = {
    #     "labels": [
    #         {"name": "non-trivial"},
    #     ]
    # }
    #
    # gh = FakeGH(getitem=pr_data)
    # await issues.router.dispatch(event, gh)
    # patch_data = gh.patch_data
    # assert patch_data["state"] == "closed"
    #
    # assert len(gh.post_url) == 2
    # assert gh.post_url[0] == 'https://api.github.com/org/repo/issues/123/labels'
    # assert gh.post_data[0] == ['invalid']
    # assert gh.post_url[1] == 'https://api.github.com/org/repo/issues/123/comments'
    # assert gh.post_data[1] == {'body': issues.INVALID_PR_COMMENT}
