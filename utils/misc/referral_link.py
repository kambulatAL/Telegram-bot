# Функция, созданная для кодирования user_id (до того, как я узнал от такой возможности сразу из коробки). Уже не нужна, но решил оставить
import base64

from aiogram.utils.deep_linking import get_start_link


async def make_ref_link(user_id: int):
    encoded = base64.b64encode(str(user_id).encode('utf-8', errors='strict'))
    link = await get_start_link(encoded.decode('utf-8'))
    return link
