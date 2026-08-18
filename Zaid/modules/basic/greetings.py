from pyrogram import Client, filters
from pyrogram.types import Message
from collections import deque, defaultdict
import random

from Zaid.modules.help import add_command_help


class GreetingEngine:
    """Lightweight greeting engine with history protection.

    - templates: dict mapping command keys to list of format strings.
    - recent: dict mapping (chat_id, user_id, cmd) -> deque of recently used indices.

    Selection algorithm:
    - Avoid indices in recent history when possible.
    - If all indices are in recent history, clear history for that key and pick randomly.
    - Keeps per-(chat,user,cmd) history so different users/chats receive different designs.
    """

    def __init__(self, recent_size: int = 3):
        self.templates = self._load_templates()
        self.recent_size = recent_size
        self.recent = defaultdict(lambda: deque(maxlen=self.recent_size))

    def _load_templates(self):
        # Each entry is a list of templates. Templates can include {name}.
        return {
            "hello": [
                "┏━━━━━━━━━━━━━┓\n┃ 👋 <b>Hello, {name}!</b> ┃\n┗━━━━━━━━━━━━━┛\n✨ Welcome back — premium vibes activated.",
                "💠 ••°° Welcome, <b>{name}</b>! °°•• 💠\nMay your day be bold and brilliant.",
                "🌟 Hey {name} — a premium hello just for you! 🌟\n╭─☆ Have a stellar day!",
                "░▒▓ ░▒▓ ░▒▓\n<b>HELLO {name}!</b>\n░▒▓ ░▒▓ ░▒▓\nYou deserve the best today.",
                "✦✦✦ Hey <b>{name}</b> ✦✦✦\nA golden hello with a side of awesome.",
                "🛡️ [Premium Greeting] 🛡️\n<b>{name}</b>, your presence beams — welcome!",
                "༺ ❤ ༻\n<b>{name}</b>, greetings of the highest order.\nMay luck follow you.",
                "•*¨*•.¸¸☆ Hello, <b>{name}</b> ☆¸¸.•*¨*•\nYou're looking premium today!",
                "╭━━━━❖❖━━━━╮\n  <b>{name}!</b>\n╰━━━━❖❖━━━━╯\nA specially crafted hello, just now.",
                "🌈 <b>{name}</b> — hello!\nCatch the colors of a premium moment.",
                "🔷 Premium Hello 🔷\n<b>{name}</b>, may your notifications be kind and your coffee warm.",
                "✨ <b>{name}</b>, hello —\nA curated greeting designed to delight.",
                "╔═.♥.═══╗\n  Hello <b>{name}</b>\n╚══════╝\nSublime. Refined. You.",
                "⚜️ Welcome, <b>{name}</b> ⚜️\nThe day just leveled up.",
                "♛ <b>{name}</b>, a royal hello for a royal soul. ♛\nProceed with confidence.",
            ],
            "hi": [
                "—•— 𝗛𝗜 • {name} —•—\nA crisp, designer hi just dropped for you.",
                "☀️ Hi <b>{name}</b>! ☀️\nFresh energy, handcrafted greeting.",
                "❖ Hi {name} ❖\nConsider this a tiny premium nudge of joy.",
                "┏(＾0＾)┛ Hi <b>{name}</b>!\nYou're officially noticed with style.",
                "•[ Hi {name} ]•\nA bouquet of emojis and warm intent, delivered.",
                "✺ Hi, <b>{name}</b> ✺\nPolished, sincere, and sparkling.",
                "▸ Hi {name} ▸\nThis greeting carries good vibes only.",
                "« Hi <b>{name}</b> »\nA sleek hello for a sleek presence.",
                "═✧ Hi {name} ✧═\nYou've unlocked a curated hello.",
                "╭━• Hi •━╮\n  <b>{name}</b>\n╰━━━☆━━━╯\nStylish hello delivered.",
                "🌿 Hi <b>{name}</b> — may your day grow steadier and brighter.",
                "🔔 Hi {name}!\nA premium ping — you're on the list.",
                "🌀 Hi <b>{name}</b> 🌀\nSwirl into a wonderful moment.",
                "▦ Hi {name} ▦\nTrimmed, neat, and premium — enjoy.",
                "⫷⫸ Hi <b>{name}</b> ⫷⫸\nA warm minimalist greeting for you.",
            ],
            "gm": [
                "🌅 <b>Good morning, {name}!</b>\nA sunbeam of premium energy to start your day.",
                "⚡️ Rise & Shine, <b>{name}</b>! ⚡️\nMay productivity and calm be yours.",
                "╭━✿ Good Morning ✿━╮\n  <b>{name}</b>\n╰━━━━━━━━━━╯\nStep into a crafted morning.",
                "☕️ Good morning, {name}! ☕️\nHere's a premium cup of optimism.",
                "•~• Good Morning <b>{name}</b> •~•\nToday looks promising — go get it.",
                "🌻 Morning {name}!\nPetals of success to you today.",
                "┌─•🌤️•─┐\n Good Morning, <b>{name}</b>\n└────────┘\nBright, calm, premium.",
                "✦ Morning, {name} ✦\nA curated greeting to fuel your morning.",
                "☆彡 Good Morning, <b>{name}</b> ☆彡\nTiny sparkles for a grand day.",
                "☼ Morning {name} — shine on. ☼\nA premium start, handcrafted.",
                "🌞 Hello {name}!\nMay your morning be smooth and your inbox kind.",
                "┍━━━━☀━━━━┑\n  Good Morning, {name}\n┕━━━━━━━━━━┙\nPolished morning for you.",
                "•» Good morning <b>{name}</b> «•\nA gentle premium nudge to begin.",
                "★ Good Morning, {name} ★\nYou’ve got this — elegantly.",
                "╰(°▽°)╯ Morning, <b>{name}</b>!\nA cheerful premium start awaits.",
            ],
            "goodmorning": [],
            "gn": [
                "🌙 Good night, {name}.\nDrift into refined dreams — premium serenity.",
                "🛌 Nighty night, <b>{name}</b> — rest like royalty. 💤",
                "✦ Sleep well, {name} ✦\nMay tomorrow be kinder and brighter.",
                "╭────• 🌙 •────╮\n  Goodnight, <b>{name}</b>\n╰────────────────╯\nCalm and curated rest.",
                "🌌 {name}, goodnight.\nStars aligned for peaceful sleep.",
                "🕯️ Soft night, <b>{name}</b> 🕯️\nA hush of luxury as you rest.",
                "—•— Goodnight {name} —•—\nSlumber with quality tonight.",
                "♒ Good night, <b>{name}</b> ♒\nFloat gently into dreams.",
                "⌁ Goodnight, {name} ⌁\nWarmth, calm, and premium rest.",
                "⋆ Goodnight <b>{name}</b> ⋆\nMay your dreams be vivid and sweet.",
                "✾ Sleep tight, {name} ✾\nA tranquil close to your day.",
                "≋ Goodnight, <b>{name}</b> ≋\nQuiet luxury for your rest.",
                "❂ {name}, rest and renew. ❂\nGood night with premium calm.",
                "‹‹ Goodnight <b>{name}</b> ››\nNestle into a gentle night.",
                "⟆ End the day softly, {name}. ⟆\nGoodnight from this little premium corner.",
            ],
            "goodnight": [],
        }

    def get_greeting(self, cmd: str, user_first_name: str, chat_id: int, user_id: int) -> str:
        cmd_key = cmd.lower()
        if cmd_key == "goodmorning":
            # alias to gm templates for now
            cmd_key = "gm"
        if cmd_key == "goodnight":
            cmd_key = "gn"

        templates = self.templates.get(cmd_key, [])
        if not templates:
            # fallback
            return f"Hello, {user_first_name}!"

        key = (chat_id, user_id, cmd_key)
        recent_indices = set(self.recent[key])
        all_indices = set(range(len(templates)))
        available = list(all_indices - recent_indices)
        if not available:
            # all used recently — clear history for this key to refresh
            self.recent[key].clear()
            available = list(all_indices)
        choice = random.choice(available)
        # record
        self.recent[key].append(choice)
        tpl = templates[choice]
        return tpl.format(name=user_first_name)


# Create a shared engine instance
engine = GreetingEngine(recent_size=3)


@Client.on_message(
    filters.command(["hello", "hi", "gm", "goodmorning", "gn", "goodnight"], ".")
    & filters.me
)
async def premium_greet(client: Client, message: Message):
    cmd = message.command[0].lstrip('.') if message.command else "hello"
    # Pyrogram's message.command provides the command without the prefix when used
    # but to be robust, map common forms
    cmd = cmd.lower()
    # map aliases
    if cmd == "goodmorning":
        cmd_key = "gm"
    elif cmd == "goodnight":
        cmd_key = "gn"
    else:
        cmd_key = cmd

    # Derive user first name
    user_first = None
    if message.reply_to_message and message.reply_to_message.from_user:
        user_first = message.reply_to_message.from_user.first_name or "friend"
    else:
        # use the client's own nickname as default
        user_first = (await client.get_me()).first_name or "friend"

    chat_id = message.chat.id
    # If there was a replied-to user, greet them; otherwise greet self
    target_user_id = (message.reply_to_message.from_user.id
                      if message.reply_to_message and message.reply_to_message.from_user
                      else (await client.get_me()).id)

    text = engine.get_greeting(cmd_key, user_first, chat_id, target_user_id)
    await message.reply_text(text, parse_mode="html", disable_web_page_preview=True)


add_command_help(
    "greetings",
    [
        [".hello / .hi / .gm / .goodmorning / .gn / .goodnight", "Send a premium greeting. Reply to someone to greet them."]
    ],
)
