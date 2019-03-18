import os
import hmac
import hashlib
import json

from aiohttp import web

from xdev_bot import __main__ as main


async def test_ping(aiohttp_client):
    app = web.Application()
    app.router.add_post("/", main.main)
    client = await aiohttp_client(app)

    data = {"zen": "testing is good"}
    encoded_data = json.dumps(data).encode('UTF-8')
    secret = os.environ.get('GH_SECRET').encode('UTF-8')
    signature = "sha1=" + hmac.new(secret, encoded_data, hashlib.sha1).hexdigest()

    headers = {"x-github-event": "ping",
               "x-github-delivery": "1234",
               "x-hub-signature": signature}
    response = await client.post("/", headers=headers, json=data)
    assert response.status == 200


async def test_success(aiohttp_client):
    app = web.Application()
    app.router.add_post("/", main.main)
    client = await aiohttp_client(app)
    data = {"action": "created"}
    encoded_data = json.dumps(data).encode('UTF-8')
    secret = os.environ.get('GH_SECRET').encode('UTF-8')
    signature = "sha1=" + hmac.new(secret, encoded_data, hashlib.sha1).hexdigest()
    headers = {"x-github-event": "project",
               "x-github-delivery": "1234",
               "x-hub-signature": signature}
    response = await client.post("/", headers=headers, json=data)
    assert response.status == 200


async def test_failure(aiohttp_client):
    """Even in the face of an exception, the server should not crash."""
    app = web.Application()
    app.router.add_post("/", main.main)
    client = await aiohttp_client(app)
    response = await client.post("/", headers={})
    assert response.status == 500
