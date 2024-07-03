# -*- coding:utf-8 -*-

import os
import time
from http.cookies import SimpleCookie
from threading import Thread

import requests

from utils import COMMON_HEADERS


class SunoCookie:
    def __init__(self):
        self.cookie = SimpleCookie()
        self.session_id = None
        self.token = None

    def load_cookie(self, cookie_str):
        self.cookie.load(cookie_str)

    def get_cookie(self):
        return ";".join([f"{i}={self.cookie.get(i).value}" for i in self.cookie.keys()])

    def set_session_id(self, session_id):
        self.session_id = session_id

    def get_session_id(self):
        return self.session_id

    def get_token(self):
        return self.token

    def set_token(self, token: str):
        self.token = token

def load_accounts():
    accounts = {}
    i = 1
    while True:
        session_id = os.getenv(f"SESSION_ID{i}")
        cookie = os.getenv(f"COOKIE{i}")
        if not session_id or not cookie:
            break
        suno_auth = SunoCookie()
        suno_auth.set_session_id(session_id)
        suno_auth.load_cookie(cookie)
        accounts[i] = suno_auth
        i += 1
    return accounts

def update_token(suno_cookie: SunoCookie):
    headers = {"cookie": suno_cookie.get_cookie()}
    headers.update(COMMON_HEADERS)
    session_id = suno_cookie.get_session_id()

    resp = requests.post(
        url=f"https://clerk.suno.com/v1/client/sessions/{session_id}/tokens?_clerk_js_version=4.72.0-snapshot.vc141245",
        headers=headers,
    )

    resp_headers = dict(resp.headers)
    set_cookie = resp_headers.get("Set-Cookie")
    suno_cookie.load_cookie(set_cookie)
    token = resp.json().get("jwt")
    suno_cookie.set_token(token)
    # print(set_cookie)
    # print(f"*** token -> {token} ***")


def keep_alive(suno_cookie: SunoCookie):
    while True:
        try:
            update_token(suno_cookie)
        except Exception as e:
            print(e)
        finally:
            time.sleep(5)

# 加载账号并启动保活
accounts = load_accounts()
for account in accounts.values():
    t = Thread(target=keep_alive, args=(account,))
    t.start()