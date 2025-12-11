import asyncio
from pyrogram import Client, filters
import json
import random
import os

# گرفتن اطلاعات از Railway Environment
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
API_ID = 28483087
API_HASH = "a7cd18d2a60c2c2ffcc23ddfb6c06983"

# فایل‌ها برای ذخیره‌سازی
CHANNELS_FILE = "channels.json"
POSTS_FILE = "posts.json"

# ایجاد فایل‌ها اگر وجود نداشتند
if not os.path.exists(CHANNELS_FILE):
    with open(CHANNELS_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(POSTS_FILE):
    with open(POSTS_FILE, "w") as f:
        json.dump([], f)

# لود لیست ها
def load_channels():
    with open(CHANNELS_FILE, "r") as f:
        return json.load(f)

def save_channels(channels):
    with open(CHANNELS_FILE, "w") as f:
        json.dump(channels, f)

def load_posts():
    with open(POSTS_FILE, "r") as f:
        return json.load(f)

def save_posts(posts):
    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f)

app = Client("bot", bot_token=TOKEN, api_id=API_ID, api_hash=API_HASH)

forwarding = False


# شروع ربات
@app.on_message(filters.command("start") & filters.user(ADMIN_ID))
async def start(_, message):
    await message.reply("ربات فعال شد.\ndیستورات:\n/addchannel\n/removechannel\n/list\n/addpost\n/on\n/off")


# اضافه کردن کانال
@app.on_message(filters.command("addchannel") & filters.user(ADMIN_ID))
async def add_channel(_, message):
    try:
        channel = message.text.split(" ", 1)[1]
    except:
        return await message.reply("فرمت درست:\n/addchannel @channel")

    channels = load_channels()
    if channel in channels:
        return await message.reply("این کانال قبلاً اضافه شده.")
    channels.append(channel)
    save_channels(channels)

    await message.reply(f"کانال {channel} اضافه شد ✔️")


# حذف کانال
@app.on_message(filters.command("removechannel") & filters.user(ADMIN_ID))
async def remove_channel(_, message):
    try:
        channel = message.text.split(" ", 1)[1]
    except:
        return await message.reply("فرمت درست:\n/removechannel @channel")

    channels = load_channels()
    if channel not in channels:
        return await message.reply("این کانال در لیست نبود.")

    channels.remove(channel)
    save_channels(channels)
    await message.reply(f"کانال {channel} حذف شد ❌")


# لیست کانال‌ها
@app.on_message(filters.command("list") & filters.user(ADMIN_ID))
async def list_channels(_, message):
    channels = load_channels()
    if not channels:
        return await message.reply("هیچ کانالی اضافه نشده.")
    text = "کانال‌های فعال:\n" + "\n".join(channels)
    await message.reply(text)


# اضافه کردن پست (هر نوع پیام)
@app.on_message(filters.private & filters.user(ADMIN_ID))
async def save_post(_, message):
    if message.text and message.text.startswith("/"):
        return  # نذار دستورات ذخیره شن

    posts = load_posts()
    posts.append(message.id)

    save_posts(posts)

    await message.reply("پست ذخیره شد ✔️")


# روشن/خاموش کردن
@app.on_message(filters.command("on") & filters.user(ADMIN_ID))
async def turn_on(_, message):
    global forwarding
    forwarding = True
    await message.reply("فوروارد خودکار روشن شد ✔️")


@app.on_message(filters.command("off") & filters.user(ADMIN_ID))
async def turn_off(_, message):
    global forwarding
    forwarding = False
    await message.reply("فوروارد خودکار خاموش شد ❌")


# سیستم فوروارد هر 5 دقیقه
async def auto_forward():
    global forwarding

    await app.start()

    while True:
        if forwarding:
            channels = load_channels()
            posts = load_posts()

            if channels and posts:
                post_id = random.choice(posts)
                for ch in channels:
                    try:
                        await app.copy_message(ch, ADMIN_ID, post_id)
                    except:
                        pass

        await asyncio.sleep(300)  # 5 دقیقه

app.run(auto_forward())
