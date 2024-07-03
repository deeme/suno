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

def load_env_cookies():
    suno_auths = {}
    i = 1
    while True:
        session_id = os.getenv(f"SESSION_ID{i}")
        cookie = os.getenv(f"COOKIE{i}")
        if not session_id or not cookie:
            break
        suno_auth = SunoCookie()
        suno_auth.set_session_id(session_id)
        suno_auth.load_cookie(cookie)
        suno_auths[i] = suno_auth
        i += 1
    return suno_auths

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

def start_keep_alive(suno_auths):
    for suno_auth in suno_auths.values():
        t = Thread(target=keep_alive, args=(suno_auth,))
        t.start()

suno_auths = load_env_cookies()
start_keep_alive(suno_auths)

def get_next_available_auth():
    global suno_auths
    for auth in suno_auths.values():
        yield auth