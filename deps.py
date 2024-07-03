# deps.py
from cookie import get_next_available_auth
from utils import get_credits
import logging

class AccountManager:
    def __init__(self):
        self.auth_generator = get_next_available_auth()
        self.current_auth = next(self.auth_generator)

    async def get_token(self):
        while True:
            token = self.current_auth.get_token()
            try:
                credits_info = await get_credits(token)
                credits = credits_info.get('credits', 0)
                logging.info(f"当前账号积分: {credits}")
                
                if credits > 0:
                    return token
                else:
                    logging.warning(f"账号积分为0，尝试切换到下一个账号")
                    self.current_auth = next(self.auth_generator)
            except Exception as e:
                logging.error(f"获取积分时出错: {str(e)}")
                try:
                    self.current_auth = next(self.auth_generator)
                except StopIteration:
                    raise Exception("所有账号积分已用尽或出现错误")

account_manager = AccountManager()

async def get_token():
    return await account_manager.get_token()
