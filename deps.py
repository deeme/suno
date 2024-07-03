# -*- coding:utf-8 -*-

from cookie import get_next_available_auth
from utils import get_credits

class AccountManager:
    def __init__(self):
        self.auth_generator = get_next_available_auth()
        self.current_auth = next(self.auth_generator)

    async def get_token(self):
        while True:
            token = self.current_auth.get_token()
            credits = await get_credits(token)
            if credits > 0:
                return token
            else:
                try:
                    self.current_auth = next(self.auth_generator)
                except StopIteration:
                    raise Exception("所有账号积分已用尽")

account_manager = AccountManager()

async def get_token():
    return await account_manager.get_token()
