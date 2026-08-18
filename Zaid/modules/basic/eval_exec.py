"""
WARNING: eval_exec module

This module exposes two powerful commands that execute arbitrary code/shell:
- .eval <python code> — executes Python code in an async function and returns output/traceback
- .exec <shell command> — executes a shell command and returns stdout/stderr

Security note:
- These commands are extremely powerful and dangerous. They execute arbitrary code and have access to the running process,
  filesystem, and the `Zaid.database` object (which is intentionally passed into the eval environment).
- They MUST remain owner-only. This file currently restricts usage with filters.me; do not weaken this restriction.
- Consider enabling auditing/logging for each use if you plan to run them in a production account.
"""

import asyncio
import io
import os
import sys
import traceback

from pyrogram import filters, Client
from pyrogram.types import Message

from Zaid.database import cli as database
from Zaid.helper.PyroHelpers import ReplyCheck


@Client.on_message(
    filters.command("eval", ".")
    & filters.me
    & ~filters.forwarded
    & ~filters.via_bot
)
async def eval_func_init(bot, message):
    await evaluation_func(bot, message)


@Client.on_edited_message(
    filters.command("eval", ".")
    & filters.me
    & ~filters.forwarded
    & ~filters.via_bot
)
async def eval_func_edited(bot, message):
    await evaluation_func(bot, message)


async def evaluation_func(bot: Client, message: Message):
    status_message = await message.reply_text("Processing ...")

    # Guard: ensure an expression was provided after the command
    text = message.text or ""
    parts = text.split(" ", maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await status_message.edit("Provide a Python expression to evaluate, e.g. `.eval 1+1`")
        return
    cmd = parts[1]

    reply_to_id = message.id
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.id

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        reply = message.reply_to_message or None
        await aexec(cmd, bot, message, reply, database)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    final_output = "<b>Expression</b>:\n<code>{}</code>\n\n<b>Result</b>:\n<code>{}</code> \n".format(
        cmd, evaluation.strip()
    )

    if len(final_output) > 4096:
        with open("eval.txt", "w", encoding="utf8") as out_file:
            out_file.write(str(final_output))

        await message.reply_document(
            "eval.txt",
            caption=cmd,
            disable_notification=True,
            reply_to_message_id=ReplyCheck(message),
        )
        os.remove("eval.txt")
        await status_message.delete()
    else:
        await status_message.edit(final_output)


async def aexec(code, b, m, r, d):
    sys.tracebacklimit = 0
    exec(
        "async def __aexec(b, m, r, d): "
        + "".join(f"\n {line}" for line in code.split("\n"))
    )
    return await locals()["__aexec"](b, m, r, d)


@Client.on_edited_message(
    filters.command("exec", ".")
    & filters.me
    & ~filters.forwarded
    & ~filters.via_bot
)
async def execution_func_edited(bot, message):
    await execution(bot, message)


@Client.on_message(
    filters.command("exec", ".")
    & filters.me
    & ~filters.forwarded
    & ~filters.via_bot
)
async def execution_func(bot, message):
    await execution(bot, message)


async def execution(bot: Client, message: Message):
    # Guard: ensure a shell command was provided after the command
    text = message.text or ""
    parts = text.split(" ", maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.reply_text("Provide a shell command to execute, e.g. `.exec ls -la`")
        return
    cmd = parts[1]

    reply_to_id = message.id
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.id

    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    e = stderr.decode()
    if not e:
        e = "No errors"
    o = stdout.decode()
    if not o:
        o = "No output"

    OUTPUT = ""
    OUTPUT += f"<b>Command:</b>\n<code>{cmd}</code>\n\n"
    OUTPUT += f"<b>Output</b>: \n<code>{o}</code>\n"
    OUTPUT += f"<b>Errors</b>: \n<code>{e}</code>"

    if len(OUTPUT) > 4096:
        with open("exec.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(OUTPUT))
        await message.reply_document(
            document="exec.text",
            caption=cmd,
            disable_notification=True,
            reply_to_message_id=ReplyCheck(message),
        )
        os.remove("exec.text")
    else:
        await message.reply_text(OUTPUT)
