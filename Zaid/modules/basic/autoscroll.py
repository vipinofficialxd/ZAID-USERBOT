from pyrogram import filters, Client
from pyrogram.types import Message

from Zaid.modules.help import add_command_help

# Use a normal Python set to track chats where autoscroll is enabled.
AUTOSCROLL_CHATS = set()


@Client.on_message(filters.chat(lambda _, __, message: message.chat.id in AUTOSCROLL_CHATS))
async def auto_read(bot: Client, message: Message):
    try:
        await bot.read_history(message.chat.id)
    except Exception:
        # Don't crash on read failures; skip silently but don't hide errors.
        pass
    # allow other handlers to process the message
    message.continue_propagation()


@Client.on_message(filters.command("autoscroll", ".") & filters.me)
async def add_to_auto_read(bot: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in AUTOSCROLL_CHATS:
        AUTOSCROLL_CHATS.remove(chat_id)
        await message.edit("Autoscroll deactivated")
    else:
        AUTOSCROLL_CHATS.add(chat_id)
        await message.edit("Autoscroll activated")


add_command_help(
    "autoscroll",
    [
        [
            ".autoscroll",
            "Send .autoscroll in any chat to automatically read all sent messages until you call "
            "autoscroll again. This is useful if you have Telegram open on another screen.",
        ],
    ],
)
