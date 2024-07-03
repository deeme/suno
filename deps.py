# -*- coding:utf-8 -*-

from cookie import accounts
from datetime import datetime, date
from threading import Lock

class AccountManager:
    def __init__(self, accounts):
        self.accounts = accounts
        self.current_index = 0
        self.call_counts = {i: 0 for i in accounts.keys()}
        self.last_call_dates = {i: None for i in accounts.keys()}
        self.lock = Lock()

    def get_next_available_account(self):
        with self.lock:
            start_index = self.current_index
            while True:
                self.current_index = (self.current_index % len(self.accounts)) + 1
                account_id = self.current_index
                
                # 重置每日调用次数
                if self.last_call_dates[account_id] != date.today():
                    self.call_counts[account_id] = 0
                    self.last_call_dates[account_id] = date.today()
                
                if self.call_counts[account_id] < 10:
                    self.call_counts[account_id] += 1
                    return self.accounts[account_id]
                
                if self.current_index == start_index:
                    return None  # 所有账号都已达到当日限制

account_manager = AccountManager(accounts)

def get_token():
    account = account_manager.get_next_available_account()
    if account:
        token = account.get_token()
        try:
            yield token
        finally:
            pass
    else:
        raise Exception("No available accounts")
