from pyrogram import Client, enums, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import asyncio

from Zaid import SUDO_USER

from Zaid.modules.help import add_command_help
from cache.data import GROUP, VERIFIED_USERS
NB = GROUP
DEVS = VERIFIED_USERS


def get_arg(message: Message) -> str:
    """Safely extract argument text from a message.

    Original implementation could IndexError on short messages. This
    function is defensive and always returns a string (possibly empty).
    """
    msg = message.text or ""
    if len(msg) > 1 and msg[1] == " ":
        msg = msg.replace(" ", "", 1)
    split = msg[1:].replace("\n", " \n").split(" ") if len(msg) > 0 else []
    if " ".join(split[1:]).strip() == "":
        return ""
    return " ".join(split[1:])


@Client.on_message(
    filters.command(["gcast"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def gcast_cmd(client: Client, message: Message):
    arg = get_arg(message)
    if message.reply_to_message or arg:
        tex = await message.reply_text("`Started global broadcast...`")
    else:
        return await message.edit_text("**Give A Message or Reply**")
    done = 0
    error = 0
    errors = []
    async for dialog in client.get_dialogs():
        if dialog.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
            if message.reply_to_message:
                msg = message.reply_to_message
            elif arg:
                msg = arg
            else:
                continue
            chat = dialog.chat.id
            if chat not in NB:
                try:
                    if message.reply_to_message:
                        await msg.copy(chat)
                    else:
                        await client.send_message(chat, msg)
                    done += 1
                    await asyncio.sleep(0.3)
                except FloodWait as fl:
                    # Respect FloodWait: sleep and retry once
                    await asyncio.sleep(fl.x)
                    try:
                        if message.reply_to_message:
                            await msg.copy(chat)
                        else:
                            await client.send_message(chat, msg)
                        done += 1
                    except Exception as e:
                        error += 1
                        errors.append(f"{chat}: {e}")
                    await asyncio.sleep(0.3)
                except Exception as e:
                    error += 1
                    errors.append(f"{chat}: {e}")
                    await asyncio.sleep(0.3)
    summary = f"**Successfully Sent Message To** `{done}` **Groups, Failed to Send Message To** `{error}` **Groups**"
    if errors:
        summary += "\nErrors:\n" + "\n".join(errors[:10])
    await tex.edit_text(summary)


@Client.on_message(
    filters.command(["gucast"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def gucast(client: Client, message: Message):
    arg = get_arg(message)
    if message.reply_to_message or arg:
        tex = await message.reply_text("`Started global broadcast...`")
    else:
        return await message.edit_text("**Give A Message or Reply**")
    done = 0
    error = 0
    errors = []
    async for dialog in client.get_dialogs():
        if dialog.chat.type == enums.ChatType.PRIVATE and not dialog.chat.is_verified:
            if message.reply_to_message:
                msg = message.reply_to_message
            elif arg:
                msg = arg
            else:
                continue
            chat = dialog.chat.id
            if chat not in DEVS:
                try:
                    if message.reply_to_message:
                        await msg.copy(chat)
                    else:
                        await client.send_message(chat, msg)
                    done += 1
                    await asyncio.sleep(0.3)
                except FloodWait as fl:
                    await asyncio.sleep(fl.x)
                    try:
                        if message.reply_to_message:
                            await msg.copy(chat)
                        else:
                            await client.send_message(chat, msg)
                        done += 1
                    except Exception as e:
                        error += 1
                        errors.append(f"{chat}: {e}")
                    await asyncio.sleep(0.3)
                except Exception as e:
                    error += 1
                    errors.append(f"{chat}: {e}")
                    await asyncio.sleep(0.3)
    summary = f"**Successfully Sent Message To** `{done}` **chat, Failed to Send Message To** `{error}` **chat**"
    if errors:
        summary += "\nErrors:\n" + "\n".join(errors[:10])
    await tex.edit_text(summary)


add_command_help(
    "broadcast",
    [
        [
            "gcast [text/reply]",
            "Sending Global Broadcast messages to all groups you are logged into. (Can Send Media/Sticker)",
        ],
        [
            "gucast [text/reply]",
            "Sending Global Broadcast messages to all incoming Private Massages / PCs. (Can Send Media/Sticker)",
        ],
    ],
)
