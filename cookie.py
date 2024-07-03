# -*- coding:utf-8 -*-

import os
import time
from http.cookies import SimpleCookie
from threading import Thread, Lock
from datetime import datetime, date #时间

import requests

from utils import COMMON_HEADERS


class SunoCookie:
    def __init__(self):
        self.cookie = SimpleCookie()
        self.session_id = None
        self.token = None
        self.call_count = 0 #计数
        self.last_call_date = None #日期

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

    def increment_call_count(self):
        self.call_count += 1
        self.last_call_date = date.today()

    def reset_call_count(self):
        if self.last_call_date != date.today():
            self.call_count = 0
            self.last_call_date = date.today()

class AccountManager:
    def __init__(self):
        self.accounts = {}
        self.current_index = 0
        self.lock = Lock()

    def load_accounts(self):
        i = 1
        while True:
            session_id = os.getenv(f"SESSION_ID{i}")
            cookie = os.getenv(f"COOKIE{i}")
            if not session_id or not cookie:
                break
            suno_auth = SunoCookie()
            suno_auth.set_session_id(session_id)
            suno_auth.load_cookie(cookie)
            self.accounts[i] = suno_auth
            i += 1

    def get_next_available_account(self):
        with self.lock:
            start_index = self.current_index
            while True:
                self.current_index = (self.current_index % len(self.accounts)) + 1
                account = self.accounts[self.current_index]
                account.reset_call_count()
                if account.call_count < 10:
                    account.increment_call_count()
                    return account
                if self.current_index == start_index:
                    return None  # 所有账号都已达到当日限制

    def start_keep_alive(self):
        for account in self.accounts.values():
            t = Thread(target=self.keep_alive, args=(account,))
            t.start()

    def keep_alive(self, suno_cookie: SunoCookie):
        while True:
            try:
                self.update_token(suno_cookie)
            except Exception as e:
                print(e)
            finally:
                time.sleep(5)

    def update_token(self, suno_cookie: SunoCookie):
        headers = {"cookie": suno_cookie.get_cookie()}
        headers.update(COMMON_HEADERS)
        session_id = suno_cookie.get_session_id()

        resp = requests.post(
            url=f"https://clerk.suno.com/v1/client/sessions/{session_id}/tokens?_clerk_js_version=4.73.3",
            headers=headers,
        )

        resp_headers = dict(resp.headers)
        set_cookie = resp_headers.get("Set-Cookie")
        suno_cookie.load_cookie(set_cookie)
        token = resp.json().get("jwt")
        suno_cookie.set_token(token)

# 主程序
account_manager = AccountManager()
account_manager.load_accounts()
account_manager.start_keep_alive()
