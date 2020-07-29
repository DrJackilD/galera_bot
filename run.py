import logging
import os

import inject
import telegram
from telegram.ext import Updater, CommandHandler

from currency_parser import manager as currency_manager
from gas_parser import get_gas_prices
from providers.transport import Transport, CarPlates, AutoAStat, BidfaxGoogleUrlProvider, AuctionUrlProviderBase

logging.basicConfig(format='%(asctime)s %(name)s [%(levelname)s]: %(message)s', level=logging.INFO)
logger = logging.getLogger('galera_bot.run')


def help_(bot, update):
    """
    Show help message
    """
    message = ('/баблишко - курсы валют\n'
               '/бенз - цены на бензин\n'
               '/ping - пинг\n'
               '/help - показать помощь')
    bot.send_message(update.message.chat_id, f'{update.message.from_user.name}\n{message}')


def pong(bot, update):
    """
    Check availability
    """
    bot.send_message(update.message.chat_id, f'{update.message.from_user.name} pong')


def currencies(bot, update):
    """
    Get today's currencies
    """
    message = (f"{update.message.from_user.name}\n"
               f"{currency_manager.get_output()}")
    bot.send_message(update.message.chat_id, message)


def gas_prices(bot, update):
    """
    Get gas prices
    """
    prices = '\n'.join(get_gas_prices())
    message = (f"{update.message.from_user.name}\n"
               f"Бензин на заправках города:\n"
               f"{prices}")
    bot.send_message(update.message.chat_id, message, parse_mode=telegram.ParseMode.MARKDOWN)


def main():
    token = os.getenv('GALERA_API_TOKEN')
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    inject.configure(inject_config)
    car_handler = Transport()
    help_cmd_handler = CommandHandler('help', help_)
    ping_cmd_handler = CommandHandler('ping', pong)
    currencies_cmd_handler = CommandHandler('баблишко', currencies)
    gas_cmd_handler = CommandHandler('бенз', gas_prices)
    cart_cmd_handler = CommandHandler('биток', car_handler.handle)

    dispatcher.add_handler(help_cmd_handler)
    dispatcher.add_handler(ping_cmd_handler)
    dispatcher.add_handler(currencies_cmd_handler)
    dispatcher.add_handler(gas_cmd_handler)
    dispatcher.add_handler(cart_cmd_handler)

    logger.info('Start bot.')
    updater.start_polling()


# Create an optional configuration.
def inject_config(binder):
    binder.bind(CarPlates, CarPlates())
    binder.bind(AuctionUrlProviderBase, BidfaxGoogleUrlProvider())


if __name__ == '__main__':
    main()
