from dataclasses import asdict
import logging
import os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from lib.templates import AddressScanTemplate
from lib.transformers.zero_mev import (
    preprocess,
    get_scan_address_data_from_mev_transactions,
)
from lib.w3 import get_web3_provider
from lib.zero_mev_api.api import get_all_mev_transactions_related_to_address

from telegram.ext import (
    Application,
    CommandHandler,
)


async def scan_address(update: Update, context: CallbackContext):
    invalid_address_response = (
        "Invalid address provided, please provide a valid Ethereum address."
    )
    try:
        address = context.args[0]
        logging.info(f"Scanning {address} address")
        if not get_web3_provider().is_address(address):
            await update.message.reply_text(invalid_address_response)
            return

        mev_txs = await get_all_mev_transactions_related_to_address(address)
        mev_txs_with_user_loss = preprocess(mev_txs)
        if mev_txs_with_user_loss.empty:
            await update.message.reply_text(
                "No MEV transactions found for the provided address."
            )
            return

        scan_data = get_scan_address_data_from_mev_transactions(
            mev_txs_with_user_loss, address
        )
        response = AddressScanTemplate.create_telegram_message(asdict(scan_data))
        await update.message.reply_text(response)
        return

    except (IndexError, ValueError):
        await update.message.reply_text(invalid_address_response)

    except:
        await update.message.reply_text(
            "An error occurred while processing the request."
        )


async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "Welcome to the MEV Scanner Bot! Here are the commands you can use:\n\n"
        "/scan_address <address> - reply with how much MEV a wallet has suffered.\n"
        "/help - Shows this help message."
    )
    await update.message.reply_text(help_text)


def main():
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()  # type: ignore

    application.add_handler(CommandHandler("scan_address", scan_address))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
