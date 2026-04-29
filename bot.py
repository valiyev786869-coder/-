import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === НАСТРОЙКИ ===
OWNER_ID = 986736263279304755

ALLOWED_ROLE = "Управление ФСВНГ"

ROLES_TO_GIVE = [
    "Рядовой",
    "- - - Звание - - -",
    "Сотрудник УФСВНГ РФ по Ростовской Области"
]

USTAV_LINK = "https://rfo-rp.ru/forum/index.php?threads/federal-naya-sluzhba-voisk-natsional-noi-gvardii-ustav.37/"
FORUM_LINK = "https://rfo-rp.ru/forum/index.php"

LOG_CHANNEL_NAME = "bot-logs"

SPAM_THRESHOLD = 3
SPAM_TIME = 10
MUTE_TIME = 10800  # 3 часа

user_messages = {}

# === ОБЩАЯ ФРАЗА ДОКЛАДА ===
REPORT_LINE = "\n\n⚠️ Это залёт, воин. Доклад начальству уже направлен."

# === ЗАПУСК ===
@bot.event
async def on_ready():
    print(f'Бот запущен как {bot.user}')


def get_log_channel(guild):
    return discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)


# === УВЕДОМЛЕНИЕ В ЛС ===
async def notify_owner(user, reason):
    try:
        owner = await bot.fetch_user(OWNER_ID)
        await owner.send(
            f"📋 КОМЕНДАНТ ДОКЛАДЫВАЕТ\n\n"
            f"👤 Боец: {user} ({user.id})\n"
            f"⚠️ Причина: {reason}\n\n"
            f"Комендант фиксирует нарушение."
        )
    except:
        pass


# === МУТ ===
async def mute_member(member):
    role = discord.utils.get(member.guild.roles, name="Muted")
    if not role:
        return

    await member.add_roles(role)

    log_channel = get_log_channel(member.guild)
    if log_channel:
        await log_channel.send(f"🚫 {member} получил мут за спам")

    await asyncio.sleep(MUTE_TIME)

    if role in member.roles:
        await member.remove_roles(role)
        if log_channel:
            await log_channel.send(f"✅ {member} автоматически размучен")


# === ОСНОВНАЯ ЛОГИКА ===
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    text = message.content.lower()
    now = datetime.utcnow()
    user_id = message.author.id

    # === АНТИСПАМ ===
    if user_id not in user_messages:
        user_messages[user_id] = []

    user_messages[user_id].append((text, message.channel.id, now))

    user_messages[user_id] = [
        m for m in user_messages[user_id]
        if (now - m[2]).seconds < SPAM_TIME
    ]

    same_msgs = {}
    for msg_text, channel_id, _ in user_messages[user_id]:
        if msg_text not in same_msgs:
            same_msgs[msg_text] = set()
        same_msgs[msg_text].add(channel_id)

    for msg_text, channels in same_msgs.items():
        if len(channels) >= SPAM_THRESHOLD:
            await mute_member(message.author)
            break

    # === УСТАВ ===
    if any(x in text for x in ["устав", "где устав"]):
        phrases = [
            "Боец, устав обязан быть в голове.",
            "Воин, это база. Не знаешь — значит не готов.",
            "Солдат, такие вещи спрашивать недопустимо.",
            "Боец, устав учится наизусть.",
            "Воин, фиксирую незнание основ."
        ]

        embed = discord.Embed(
            title="📄 УСТАВ",
            description=(
                f"{random.choice(phrases)}\n\n"
                f"👉 [Открыть устав]({USTAV_LINK})"
                f"{REPORT_LINE}"
            ),
            color=0x8B0000
        )

        await message.channel.send(embed=embed)
        await notify_owner(message.author, "Не знает устав")

    # === ФОРУМ ===
    elif any(x in text for x in ["форум", "где форум", "ссылка на форум"]):
        phrases = [
            "Боец, форум обязан знать.",
            "Воин, вся информация уже есть.",
            "Солдат, это базовые вещи.",
            "Боец, не заставляй повторять.",
            "Воин, работай с материалами."
        ]

        embed = discord.Embed(
            title="🌐 ФОРУМ",
            description=(
                f"{random.choice(phrases)}\n\n"
                f"👉 [Перейти на форум]({FORUM_LINK})"
            ),
            color=0x8B0000
        )

        await message.channel.send(embed=embed)

    # === КОНСТИТУЦИЯ ===
    elif "конституция" in text:
        phrases = [
            "Воин, это основа всего.",
            "Боец, начинаешь отсюда.",
            "Солдат, база обязательна.",
            "Воин, игнорировать запрещено.",
            "Боец, изучить полностью."
        ]

        embed = discord.Embed(
            title="📜 КОНСТИТУЦИЯ",
            description=(
                f"{random.choice(phrases)}\n\n"
                f"👉 [Открыть документ](https://rfo-rp.ru/forum/index.php?threads/konstitutsiya-rossiiskoi-federatsii.122/)"
            ),
            color=0x8B0000
        )

        await message.channel.send(embed=embed)

    # === УК ===
    elif any(x in text for x in ["ук", "уголовный"]):
        phrases = [
            "Боец, ответственность обязан знать.",
            "Воин, последствия изучаются заранее.",
            "Солдат, без этого работать нельзя.",
            "Боец, это практика.",
            "Воин, усвоить."
        ]

        embed = discord.Embed(
            title="⚖️ УГОЛОВНЫЙ КОДЕКС",
            description=(
                f"{random.choice(phrases)}\n\n"
                f"👉 [Открыть УК](https://rfo-rp.ru/forum/index.php?threads/ugolovnyi-kodeks-rossiiskoi-federatsii.120/)"
            ),
            color=0x8B0000
        )

        await message.channel.send(embed=embed)

    # === УПК ===
    elif "упк" in text:
        phrases = [
            "Воин, порядок обязателен.",
            "Боец, работа по процедурам.",
            "Солдат, самодеятельность запрещена.",
            "Воин, изучить и применять.",
            "Боец, контроль обязателен."
        ]

        embed = discord.Embed(
            title="⚖️ УПК РФ",
            description=(
                f"{random.choice(phrases)}\n\n"
                f"👉 [Открыть УПК](https://rfo-rp.ru/forum/index.php?threads/ugolovno-protsessual-nyi-kodeks-rossiiskoi-federatsii.121/)"
            ),
            color=0x8B0000
        )

        await message.channel.send(embed=embed)

    # === КОАП ===
    elif any(x in text for x in ["коап", "административ"]):
        phrases = [
            "Боец, административку знать обязан.",
            "Воин, это повседневная база.",
            "Солдат, ошибки недопустимы.",
            "Боец, применяй грамотно.",
            "Воин, контроль знаний."
        ]

        embed = discord.Embed(
            title="⚖️ КоАП РФ",
            description=(
                f"{random.choice(phrases)}\n\n"
                f"👉 [Открыть КоАП](https://rfo-rp.ru/forum/index.php?threads/kodeks-ob-administrativnykh-pravonarusheniyakh-rossiiskoi-federatsii.117/)"
            ),
            color=0x8B0000
        )

        await message.channel.send(embed=embed)

    # === ФЗ ===
    elif any(x in text for x in ["фз", "росгвардии"]):
        phrases = [
            "Воин, это основа службы.",
            "Боец, закон обязателен.",
            "Солдат, без этого не работаешь.",
            "Воин, изучить и соблюдать.",
            "Боец, контроль исполнения."
        ]

        embed = discord.Embed(
            title="🛡️ ФЗ О РОСГВАРДИИ",
            description=(
                f"{random.choice(phrases)}\n\n"
                f"👉 [Открыть закон](https://rfo-rp.ru/forum/index.php?threads/federal-nyi-zakon-o-voiskakh-natsional-noi-gvardii-no-18-fz.113/)"
            ),
            color=0x8B0000
        )

        await message.channel.send(embed=embed)

    # === ТУПЫЕ ВОПРОСЫ ===
    elif any(x in text for x in ["что делать", "как играть", "помогите"]):
        phrases = [
            "Боец, сначала изучаешь — потом спрашиваешь.",
            "Воин, инструкции уже даны.",
            "Солдат, такие вопросы недопустимы.",
            "Боец, думай прежде чем писать.",
            "Воин, фиксирую неподготовленность."
        ]

        embed = discord.Embed(
            title="⚠️ ПОРЯДОК",
            description=(
                f"{random.choice(phrases)}\n\n"
                f"Изучить устав и форум."
                f"{REPORT_LINE}"
            ),
            color=0x8B0000
        )

        await message.channel.send(embed=embed)
        await notify_owner(message.author, "Задает базовые вопросы")

    await bot.process_commands(message)


# === ДОСТУП ===
def has_access(member):
    return any(role.name == ALLOWED_ROLE for role in member.roles)


# === ВЫДАЧА РОЛЕЙ ===
@bot.command()
async def выдать(ctx, member: discord.Member):
    if not has_access(ctx.author):
        return

    roles = []
    for r in ROLES_TO_GIVE:
        role = discord.utils.get(ctx.guild.roles, name=r)
        if role:
            roles.append(role)

    await member.add_roles(*roles)
    await ctx.send(f"✅ Выдано {member.mention}")

    log_channel = get_log_channel(ctx.guild)
    if log_channel:
        await log_channel.send(f"{ctx.author} выдал роли {member}")


# === СБОР ===
@bot.command()
async def сбор(ctx):
    if not has_access(ctx.author):
        return

    role = discord.utils.get(ctx.guild.roles, name="Сотрудник УФСВНГ РФ по Ростовской Области")

    text = (
        "🚨 ОБЩИЙ СБОР 🚨\n\n"
        "Всем сотрудникам срочно зайти в спецсвязь.\n"
        "Канал: Рация №1"
    )

    for m in role.members:
        try:
            await m.send(text)
        except:
            pass

    await ctx.send(text)

bot.run("MTQ5ODgyOTE3NzQ4MTE5OTY4Nw.GWZYP_.ja7TO_v5XIH-1e-AJB8tyP-BXlWmN2n2L7fL6M")