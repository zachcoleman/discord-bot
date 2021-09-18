import asyncio

from bot.utils import url_request


def test_request():
    resp = asyncio.run(url_request("http://www.google.com"))
    assert resp.status_code == 200


def test_leetcode():
    resp = asyncio.run(
        url_request("https://leetcode.com/problems/random-one-question/all")
    )
    assert resp.status_code == 200
