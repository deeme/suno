# deps.py
from cookie import suno_auths
from utils import get_credits
import logging
import asyncio

def get_token():
    while True:
        for suno_auth in suno_auths.values():
            token = suno_auth.get_token()
            try:
                credits_info = get_credits(token)
                credits = credits_info.get('credits', 0)
                logging.info(f"当前账号 {suno_auth.get_session_id()} 积分: {credits}")
                
                if credits > 0:
                    return token
            except Exception as e:
                logging.error(f"获取积分失败: {e}")
        
        logging.warning("所有账号积分已用尽,等待 1 小时后重试...")
        asyncio.sleep(3600)  # 等待1小时 (3600秒)
