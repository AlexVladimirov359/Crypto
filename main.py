import asyncio
import time

from notifiers import get_notifier
from aiogram import Bot, executor, Dispatcher
from aiogram.types import Message
from binance import AsyncClient
from binance.exceptions import BinanceAPIException

from TOKEN import token, chatId

bot = Bot('6269990596:AAEDCZU9minrSq1lWjJXTa1GLg4JFXJzedc')
dispatcher = Dispatcher(bot)
binance_client = AsyncClient()


async def get_coin_price(coin: str):
    try:
        ticker_data = await binance_client.get_ticker(symbol=coin)
        return ticker_data['lastPrice'], ticker_data['priceChangePercent']
    except BinanceAPIException:
        raise ValueError("Not found")


async def update_coin_price(message: Message, coin: str):
    while True:
        new_price = await get_coin_price(coin)
        await message.edit_text(text=new_price)
        await asyncio.sleep(5)


async def notification(proc: str):
    while True:
        percent = await binance_client.get_ticker(symbol=proc)
        if percent['priceChangePercent'] > 1:
            t = input('Через сколько минут напомнить?\n')
            t = int(t) * 60
            time.sleep(t)
            telegram = get_notifier('telegram')
            telegram.notify(token=token, chat_id=chatId, message=percent)
            return percent['priceChangePercent']


@dispatcher.message_handler()
async def handle_coin_price(message: Message):
    try:
        price = await get_coin_price(coin=message.text)
        reply_message = await message.reply(text=price)
        await update_coin_price(message=reply_message, coin=message.text)
        await notification(message=reply_message, proc=message.text)
    except ValueError:
        await message.reply(text="Not found")


if __name__ == '__main__':
    executor.start_polling(dispatcher)
