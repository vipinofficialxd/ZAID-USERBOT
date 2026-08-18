import os

from pyrogram import *
from pyrogram.types import *


from Zaid.helper.basic import edit_or_reply, get_text, get_user

from Zaid.modules.help import *

OWNER = os.environ.get("OWNER", None)
BIO = os.environ.get("BIO", "404 : Bio Lost")


@Client.on_message(filters.command("clone", ".") & filters.me)
async def clone(client: Client, message: Message):
    text = get_text(message)
    op = await message.edit_text("`Cloning`")
    userk = get_user(message, text)[0]
    try:
        user_ = await client.get_users(userk)
    except Exception:
        await op.edit("`Whom i should clone:(`")
        return

    if not user_:
        await op.edit("`Whom i should clone:(`")
        return

    # Safely get chat/bio
    try:
        get_bio = await client.get_chat(user_.id)
        c_bio = get_bio.bio if getattr(get_bio, 'bio', None) else ""
    except Exception:
        c_bio = ""

    f_name = user_.first_name or ""

    # Safely handle profile photo
    poto = None
    try:
        if getattr(user_, 'photo', None) and getattr(user_.photo, 'big_file_id', None):
            pic = user_.photo.big_file_id
            poto = await client.download_media(pic)
    except Exception:
        poto = None

    try:
        if poto:
            await client.set_profile_photo(photo=poto)
        await client.update_profile(
            first_name=f_name,
            bio=c_bio,
        )
        await message.edit(f"**From now I'm** __{f_name}__")
    finally:
        # cleanup downloaded photo file if present
        try:
            if poto and isinstance(poto, str) and os.path.exists(poto):
                os.remove(poto)
        except Exception:
            pass


@Client.on_message(filters.command("revert", ".") & filters.me)
async def revert(client: Client, message: Message):
    await message.edit("`Reverting`")
    r_bio = BIO if BIO is not None else ""

    # Get ur Name back
    try:
        await client.update_profile(
            first_name=OWNER,
            bio=r_bio,
        )
    except Exception:
        # Even if update_profile fails, attempt to continue and delete photo safely
        pass

    # Delete first photo to get ur identity (if any)
    try:
        photos = [p async for p in client.get_chat_photos("me")]
        if photos:
            await client.delete_profile_photos(photos[0].file_id)
    except Exception:
        # If deletion fails or no photos exist, continue silently
        pass

    await message.edit("`I am back!`")


add_command_help(
    "clone",
    [
        ["clone", "To Clone someone Profile."],
        ["revert", "To Get Your Account Back."],
    ],
)
