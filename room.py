import logging
import random
import os
import time
import json
import ast
import string
import datetime
import requests
import math
from decimal import Decimal
import asyncio
from threading import Thread
from telegram.constants import ChatAction
from bs4 import BeautifulSoup
from functools import wraps
from collections import deque
from telegram.ext import Application, MessageHandler, filters, CallbackContext, CommandHandler, CallbackQueryHandler
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaAnimation, ChatPermissions, User
from telegram.constants import ParseMode
from telegram.error import NetworkError, TelegramError
import threading
import pyfiglet
from colorama import Fore, Style, init

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

init(autoreset=True)

SICBO_GROUP_ID = -1002307642304 
TAIXIU_GROUP_ID = -1002307642304 
CHECKBB_FILE = "checkbb.txt"
groups_info = {}
joined_groups = {}
VIETTEL, VINAPHONE, MOBIPHONE, VIETNAMOBILE = range(4)
MENH_GIA = ["10000", "20000", "30000", "50000", "100000", "200000", "500000"]
mophien = True
inf_balance_user = {}
pending_transactions = {}
MAX_JACKPOT_AMOUNT = 1000000000000000000
huloc_default_amount = 10000000000000000
huloc_amount = 0
lottery_active = False
lottery_tickets = {}
lottery_timer = 0
taixiu_game_active = False
end_game_requested = False
taixiu_bets = {}
taixiu_result = None
jackpot = 0
jackpot_amount = 1000000000000000000
taixiu_timer = 0
recent_results = []
betting_time = 30
betting_timer = betting_time
aviator_lock = threading.Lock()
aviator_game_active = False
aviator_bets = {}
aviator_multiplier = 1.0
banned_groups = []
ket_balance = {}
banned_users = []
chat_id = -1002066327546
betting_records = {}
user_daily_claim = {}
MIN_DAILY_AMOUNT = 1000
MAX_DAILY_AMOUNT = 5000
user_balances = {}
winners = []
codes = {}
rooms = {}
user_code_usage = {}
DAILY_FILE_PATH = "daily.txt"
sodu_file_path = "sodu.txt"
codes_file_path = "code.txt"
user_code_usage_file = "user_code_usage.json"
TOKEN = "7156215167:AAFwsAPwnid9k9UtDfJsY7P8Ks3no3nmT7A"
transaction_history_file = "transaction_history.json"
end_game_requested = False
xocdia_game_active = False
xocdia_bets = {}
xocdia_timer = 30
xocdia_result = None
horse_race_active = False
horse_race_bets = {}
horse_race_timer = 30
horse_race_results = []
admin_ids = 6233606549
ADMIN_IDS = 6233606549
admin_id = 6233606549
ADMIN_ID = 6233606549
authorized_users = 6233606549
sicbo_game_active = False
sicbo_bets = {}
sicbo_timer = 0
GROUP_CHAT_ID = -1002307642304
VERIFIED_USERS_FILE = 'ver_rut.txt'
num_rounds = {}
with open("admin.txt", "w") as admin_file:
    admin_file.write(json.dumps(admin_id))
bet_types = {
    'T': {'name': 'Tài', 'multiplier': 2, 'condition': lambda total: 11 <= total <= 18},
    'X': {'name': 'Xỉu', 'multiplier': 2, 'condition': lambda total: 3 <= total <= 10},
    'L': {'name': 'Lẻ', 'multiplier': 2, 'condition': lambda total: total % 2 == 1},
    'C': {'name': 'Chẵn', 'multiplier': 2, 'condition': lambda total: total % 2 == 0},
    'D1': {'name': '2 Con 1', 'multiplier': 15, 'condition': lambda dice: dice.count(1) == 2},
    'D2': {'name': '2 Con 2', 'multiplier': 15, 'condition': lambda dice: dice.count(2) == 2},
    'D3': {'name': '2 Con 3', 'multiplier': 15, 'condition': lambda dice: dice.count(3) == 2},
    'D4': {'name': '2 Con 4', 'multiplier': 15, 'condition': lambda dice: dice.count(4) == 2},
    'D5': {'name': '2 Con 5', 'multiplier': 15, 'condition': lambda dice: dice.count(5) == 2},
    'D6': {'name': '2 Con 6', 'multiplier': 15, 'condition': lambda dice: dice.count(6) == 2},
    'BBK': {'name': 'Bão Bất Kỳ', 'multiplier': 31, 'condition': lambda dice: len(set(dice)) == 1},
    'B1': {'name': '3 Con 1', 'multiplier': 200, 'condition': lambda dice: dice == [1, 1, 1]},
    'B2': {'name': '3 Con 2', 'multiplier': 200, 'condition': lambda dice: dice == [2, 2, 2]},
    'B3': {'name': '3 Con 3', 'multiplier': 200, 'condition': lambda dice: dice == [3, 3, 3]},
    'B4': {'name': '3 Con 4', 'multiplier': 200, 'condition': lambda dice: dice == [4, 4, 4]},
    'B5': {'name': '3 Con 5', 'multiplier': 200, 'condition': lambda dice: dice == [5, 5, 5]},
    'B6': {'name': '3 Con 6', 'multiplier': 200, 'condition': lambda dice: dice == [6, 6, 6]},
    '4': {'name': 'Xúc xắc 4', 'multiplier': 66, 'condition': lambda total: total == 4},
    '5': {'name': 'Xúc xắc 5', 'multiplier': 33, 'condition': lambda total: total == 5},
    '6': {'name': 'Xúc xắc 6', 'multiplier': 21, 'condition': lambda total: total == 6},
    '7': {'name': 'Xúc xắc 7', 'multiplier': 14, 'condition': lambda total: total == 7},
    '8': {'name': 'Xúc xắc 8', 'multiplier': 10, 'condition': lambda total: total == 8},
    '9': {'name': 'Xúc xắc 9', 'multiplier': 8, 'condition': lambda total: total == 9},
    '10': {'name': 'Xúc xắc 10', 'multiplier': 7, 'condition': lambda total: total == 10},
    '11': {'name': 'Xúc xắc 11', 'multiplier': 7, 'condition': lambda total: total == 11},
    '12': {'name': 'Xúc xắc 12', 'multiplier': 8, 'condition': lambda total: total == 12},
    '13': {'name': 'Xúc xắc 13', 'multiplier': 10, 'condition': lambda total: total == 13},
    '14': {'name': 'Xúc xắc 14', 'multiplier': 14, 'condition': lambda total: total == 14},
    '15': {'name': 'Xúc xắc 15', 'multiplier': 21, 'condition': lambda total: total == 15},
    '16': {'name': 'Xúc xắc 16', 'multiplier': 33, 'condition': lambda total: total == 16},
    '17': {'name': 'Xúc xắc 17', 'multiplier': 66, 'condition': lambda total: total == 17},
    'P12': {'name': 'Xúc xắc 1 và 2', 'multiplier': 7, 'condition': lambda dice: dice.count(1) == 2 and dice.count(2) == 1},
    'P13': {'name': 'Xúc xắc 1 và 3', 'multiplier': 7, 'condition': lambda dice: dice.count(1) == 2 and dice.count(3) == 1},
    'P14': {'name': 'Xúc xắc 1 và 4', 'multiplier': 7, 'condition': lambda dice: dice.count(1) == 2 and dice.count(4) == 1},
    'P15': {'name': 'Xúc xắc 1 và 5', 'multiplier': 7, 'condition': lambda dice: dice.count(1) == 2 and dice.count(5) == 1},
    'P16': {'name': 'Xúc xắc 1 và 6', 'multiplier': 7, 'condition': lambda dice: dice.count(1) == 2 and dice.count(6) == 1},
    'P23': {'name': 'Xúc xắc 2 và 3', 'multiplier': 7, 'condition': lambda dice: dice.count(2) == 2 and dice.count(3) == 1},
    'P24': {'name': 'Xúc xắc 2 và 4', 'multiplier': 7, 'condition': lambda dice: dice.count(2) == 2 and dice.count(4) == 1},
    'P25': {'name': 'Xúc xắc 2 và 5', 'multiplier': 7, 'condition': lambda dice: dice.count(2) == 2 and dice.count(5) == 1},
    'P26': {'name': 'Xúc xắc 2 và 6', 'multiplier': 7, 'condition': lambda dice: dice.count(2) == 2 and dice.count(6) == 1},
    'P34': {'name': 'Xúc xắc 3 và 4', 'multiplier': 7, 'condition': lambda dice: dice.count(3) == 2 and dice.count(4) == 1},
    'P35': {'name': 'Xúc xắc 3 và 5', 'multiplier': 7, 'condition': lambda dice: dice.count(3) == 2 and dice.count(5) == 1},
    'P36': {'name': 'Xúc xắc 3 và 6', 'multiplier': 7, 'condition': lambda dice: dice.count(3) == 2 and dice.count(6) == 1},
    'P45': {'name': 'Xúc xắc 4 và 5', 'multiplier': 7, 'condition': lambda dice: dice.count(4) == 2 and dice.count(5) == 1},
    'P46': {'name': 'Xúc xắc 4 và 6', 'multiplier': 7, 'condition': lambda dice: dice.count(4) == 2 and dice.count(6) == 1},
    'P56': {'name': 'Xúc xắc 5 và 6', 'multiplier': 7, 'condition': lambda dice: dice.count(5) == 2 and dice.count(6) == 1},
    'S1': {'name': 'Xúc xắc 1', 'multiplier': 2, 'condition': lambda dice: 1 in dice},
    'S2': {'name': 'Xúc xắc 2', 'multiplier': 2, 'condition': lambda dice: 2 in dice},
    'S3': {'name': 'Xúc xắc 3', 'multiplier': 2, 'condition': lambda dice: 3 in dice},
    'S4': {'name': 'Xúc xắc 4', 'multiplier': 2, 'condition': lambda dice: 4 in dice},
    'S5': {'name': 'Xúc xắc 5', 'multiplier': 2, 'condition': lambda dice: 5 in dice},
    'S6': {'name': 'Xúc xắc 6', 'multiplier': 2, 'condition': lambda dice: 6 in dice},
}

def retry_on_failure(retries=3, delay=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except NetworkError as e:
                    print(f"Xảy ra lỗi mạng: {e}. Thử lại sau {delay} giây...")
                    time.sleep(delay)
                except TelegramError as e:
                    print(f"Xảy ra lỗi Telegram: {e}")
                    break  
            return None
        return wrapper
    return decorator

def restrict_room(func):
    @wraps(func)
    async def wrapper(update, context):
        if update.message.chat_id == -1002178971014:
            await update.message.reply_text(
                "Đây Không Phải Là 1 Lệnh Có Thể Sài Trong Room\n\nSử dụng mọi lệnh tại\n👉 t.me/aniosvip 👈"
            )
        else:
            return await func(update, context)
    return wrapper

def lock_chat(context, chat_id):
    context.bot.set_chat_permissions(
        chat_id=chat_id,
        permissions=ChatPermissions(
            can_send_messages=False
        )
    )

def unlock_chat(context, chat_id):
    context.bot.set_chat_permissions(
        chat_id=chat_id,
        permissions=ChatPermissions(
            can_send_messages=True
        )
    )

async def add_admin(update, context):
    if update.message.from_user.id != 6793700101:
        await update.message.reply_text("Only the main admin can add other admins.")
        return
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Usage: /themad <admin_id>")
        return
    try:
        new_admin_id = int(args[0])
        all_admin_ids.append(new_admin_id)
        with open("admin.txt", "w") as admin_file:
            admin_file.write(json.dumps(all_admin_ids))
        await update.message.reply_text("Admin added successfully.")
    except ValueError:
        await update.message.reply_text("Invalid admin ID.")

async def remove_admin(update, context):
    if update.message.from_user.id != 6793700101:
        await update.message.reply_text("Only the main admin can remove other admins.")
        return
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Usage: /xoaad <admin_id>")
        return
    try:
        remove_admin_id = int(args[0])
        if remove_admin_id not in all_admin_ids:
            await update.message.reply_text("This user is not an admin.")
            return
        all_admin_ids.remove(remove_admin_id)
        with open("admin.txt", "w") as admin_file:
            admin_file.write(json.dumps(all_admin_ids))
        await update.message.reply_text("Admin removed successfully.")
    except ValueError:
        await update.message.reply_text("Invalid admin ID.")

@restrict_room
async def start_horse_race(update, context):
    global horse_race_active, horse_race_bets, horse_race_timer

    if horse_race_active:
        await update.message.reply_text("Trò chơi Đua Ngựa đang diễn ra! Vui lòng đợi đến khi kết thúc để tham gia.")
        return

    horse_race_active = True
    horse_race_bets = {}
    horse_race_timer = 30

    await update.message.reply_text(
        "🏇 Trò chơi Đua Ngựa đã bắt đầu! 🏇\n\n"
        "Lệnh cược: /h <số tiền cược hoặc 'all'> <con chọn>\n\n"
        "Các con ngựa:\n"
        "1 - Ngựa 1\n"
        "2 - Ngựa 2\n"
        "3 - Ngựa 3\n"
        "4 - Ngựa 4\n"
        "5 - Ngựa 5\n\n"
        f"⏳ Còn {horse_race_timer} giây để đặt cược ⏳"
    )
    asyncio.create_task(start_horse_race_timer(update, context))

async def start_horse_race_timer(update, context):
    global horse_race_timer
    while horse_race_timer > 0:
        await asyncio.sleep(1)
        horse_race_timer -= 1
        if horse_race_timer % 10 == 0:
            await update.message.reply_text(f"⏳ Còn {horse_race_timer} giây để đặt cược ⏳")
    await update.message.reply_text("⏳ Hết thời gian đặt cược! ⏳")
    await generate_horse_race_result(update, context)

async def place_horse_bet(update, context):
    global horse_race_bets, horse_race_active, horse_race_timer

    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return

    if not horse_race_active:
        await update.message.reply_text("Hiện không có trò chơi Đua Ngựa nào đang diễn ra.")
        return

    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Sử dụng: /h <số tiền cược hoặc 'all'> <con chọn>")
        return

    try:
        bet_amount = int(args[0]) if args[0].lower() != 'all' else user_balances.get(user_id, 0)
        horse_choice = int(args[1])
    except ValueError:
        await update.message.reply_text("Số tiền cược phải là một số nguyên hoặc 'all' và con chọn phải là số từ 1 đến 5.")
        return

    if bet_amount <= 0 or horse_choice not in range(1, 6):
        await update.message.reply_text("Số tiền cược hoặc con chọn không hợp lệ.")
        return

    if user_balances.get(user_id, 0) < bet_amount:
        await update.message.reply_text("Số dư của bạn không đủ để đặt cược.")
        return

    if horse_race_timer == 0:
        await update.message.reply_text("Hết thời gian đặt cược. Vui lòng chờ đợi kết quả.")
        return

    if user_id not in horse_race_bets:
        horse_race_bets[user_id] = []

    horse_race_bets[user_id].append((horse_choice, bet_amount))
    await update.message.reply_text(f"Bạn đã đặt cược {format_currency(bet_amount)} vào con ngựa {horse_choice}!")
    user_balances[user_id] -= bet_amount

async def generate_horse_race_result(update, context):
    global horse_race_active, horse_race_bets, horse_race_results

    if not horse_race_active:
        await update.message.reply_text("Hiện không có trò chơi Đua Ngựa nào đang diễn ra.")
        return

    horse_race_active = False

    horse_race_results = random.sample(range(1, 6), 5)
    winner = horse_race_results[0]

    await update.message.reply_text("‼️ Kết quả đua ngựa ‼️")
    await asyncio.sleep(2)
    await update.message.reply_text(f"💢 TOP 5 💢 : Ngựa {horse_race_results[4]}")
    await update.message.reply_text(f"💢 TOP 4 💢 : Ngựa {horse_race_results[3]}")
    await asyncio.sleep(1)
    await update.message.reply_text(f"‼️ GIỜ LÀ ĐẾN CÁC TOP ‼️")
    await asyncio.sleep(1)
    await update.message.reply_text(f"🏆 TOP 3 🏆 : Ngựa {horse_race_results[2]}")
    await update.message.reply_text(f"🏆 TOP 2 🏆 : Ngựa {horse_race_results[1]}")
    await update.message.reply_text(f"🏆 TOP 1 🏆 : Ngựa {horse_race_results[0]}")

    winners = {}
    for user_id, bets in horse_race_bets.items():
        user_total_winnings = 0
        for choice, amount in bets:
            if choice == horse_race_results[0]:
                user_total_winnings += amount * 5
            elif choice == horse_race_results[1]:
                user_total_winnings += amount * 1
            elif choice == horse_race_results[2]:
                user_total_winnings -= amount * 0.5

        if user_total_winnings != 0:
            winners[user_id] = user_total_winnings

    result_message = "🎮 Kết quả cược 🎮 :\n\n"
    if len(winners) == 0:
        result_message += "Không có người chơi nào thắng cược!"
    else:
        result_message += "Người chơi - Tiền thắng\n"
        for user_id, amount_won in winners.items():
            update_user_balance(user_id, amount_won)
            result_message += f"{user_id} - {format_currency(amount_won)}\n"

    await update.message.reply_text(result_message)
    horse_race_bets.clear()

def bang_gia_xu(update, context):
    gia_xu = [
        (10000, 750),
        (20000, 2000),
        (50000, 3500),
        (100000, 7000),
        (200000, 14000)
    ]
    message = "💰 **Bảng Giá Xu** 💰\n\n"
    for gia, xu in gia_xu:
        message += f"{format_currency(gia)} = {xu} MB\n"
    return message

@restrict_room
async def nap(update, context):
    user_id = update.message.from_user.id
    account_info = (
        "💳 **Số Tài Khoản**: 0345421396\n"
        "👤 **Chủ Tài Khoản**: Nguyễn Trường An\n"
        "🏦 **Ngân Hàng**: MOMO BANKING\n"
        f"📄 **Nội Dung**: {user_id}\n"
        "‼️ Vui lòng chuyển > 10,000đ để nạp ‼️"
    )

    bang_gia = bang_gia_xu(update, context)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=account_info + "\n\n" + bang_gia,
        parse_mode="Markdown"
    )

def fix_user_balance():
    global user_balances
    for user_id in user_balances:
        if isinstance(user_balances[user_id], float):
            user_balances[user_id] = int(user_balances[user_id])
            print(
                f"Số dư của người dùng {user_id} đã được chỉnh về số nguyên: {user_balances[user_id]}"
            )

@restrict_room
async def start_xocdia(update, context):
    global xocdia_game_active, xocdia_bets, xocdia_timer

    if xocdia_game_active:
        await update.message.reply_text(
            "Trò chơi Xóc Đĩa đang diễn ra! Vui lòng đợi đến khi kết thúc để tham gia."
        )
        return

    xocdia_game_active = True
    xocdia_bets = {}
    xocdia_timer = 30

    await update.message.reply_text(
        "⚪️⚫️ Trò chơi Xóc Đĩa đã bắt đầu! ⚪️⚫️\n\n"
        "Lệnh cược: /xocdia <Cửa chọn> <Cược hoặc 'all'>\n\n"
        "Các cửa cược:\n"
        "- L : Lẻ (1:2) ⚪️⚪️⚪️⚫️ / ⚫️⚫️⚫️⚪️\n\n"
        "- C : Chẵn (1:2) ⚪️⚫️⚪️⚫️\n\n"
        "- 3T : Lẻ 3 trắng (1:4) ⚪️⚪️⚪️⚫️\n\n"
        "- 3D : Lẻ 3 đen (1:4) ⚫️⚫️⚫️⚪️\n\n"
        "- 4T : Tứ trắng (1:16) ⚪️⚪️⚪️⚪️\n\n"
        "- 4D : Tứ đen (1:16) ⚫️⚫️⚫️⚫️\n\n"
        f"⏳ Còn {xocdia_timer} giây để đặt cược ⏳"
    )
    asyncio.create_task(start_xocdia_timer(update, context))

@restrict_room
async def giaxu(update, context):
    await update.message.reply_text("Nhắn /nap Có Tổng Hợp Giá Xu")

@restrict_room
async def start_xocdia_timer(update, context):
    global xocdia_timer
    while xocdia_timer > 0:
        await asyncio.sleep(1)
        xocdia_timer -= 1
        if xocdia_timer % 10 == 0:
            await update.message.reply_text(
                f"⏳ Còn {xocdia_timer} giây để đặt cược ⏳")
    await update.message.reply_text("⏳ Hết thời gian đặt cược! ⏳")
    await generate_xocdia_result(update, context)

@restrict_room
async def xocdia(update, context):
    global xocdia_game_active, xocdia_timer, xocdia_bets

    if not xocdia_game_active:
        await update.message.reply_text(
            "Hiện không có trò chơi Xóc Đĩa nào đang diễn ra.")
        return

    args = context.args
    if len(args) != 2:
        await update.message.reply_text(
            "Sử dụng: /xocdia <Cửa chọn> <Cược hoặc 'all'>")
        return

    bet_option = args[0].upper()
    bet_amount = 0
    user_id = update.message.from_user.id
    if args[1].lower() == 'all':
        bet_amount = user_balances.get(user_id, 0)
    else:
        try:
            bet_amount = int(args[1])
        except ValueError:
            await update.message.reply_text(
                "Số tiền cược phải là một số nguyên hoặc 'all'.")
            return

    if user_balances.get(user_id, 0) < bet_amount:
        await update.message.reply_text("Số dư của bạn không đủ để đặt cược.")
        return

    if xocdia_timer == 0:
        await update.message.reply_text(
            "Hết thời gian đặt cược. Vui lòng chờ đợi kết quả.")
        return

    valid_options = ['L', 'C', '3T', '3D', '4T', '4D']
    if bet_option not in valid_options:
        await update.message.reply_text("Lựa chọn cửa không hợp lệ.")
        return

    if user_id not in xocdia_bets:
        xocdia_bets[user_id] = []

    xocdia_bets[user_id].append((bet_option, bet_amount))
    await update.message.reply_text(
        f"Bạn đã đặt cược {format_currency(bet_amount)} vào cửa {bet_option}!")
    user_balances[user_id] -= bet_amount

async def generate_xocdia_result(update, context):
    global xocdia_game_active, xocdia_result, xocdia_bets

    if not xocdia_game_active:
        await update.message.reply_text(
            "Hiện không có trò chơi Xóc Đĩa nào đang diễn ra.")
        return

    result_option = random.choice(['L', 'C', '3T', '3D', '4T', '4D'])

    result_message = "KẾT QUẢ: "
    emojis = ""
    if result_option == 'L':
        result_message += "LẺ"
        emojis = "LẺ BẤT KỲ"
    if result_option == 'C':
        result_message += "CHẴN"
        emojis = "⚫️⚪️\n⚫️⚪️"
    elif result_option == '3T':
        result_message += "LẺ 3 TRẮNG"
        emojis = "⚪️⚪️\n⚪️⚫️"
    elif result_option == '3D':
        result_message += "LẺ 3 ĐEN"
        emojis = "⚫️⚫️\n⚫️⚪️"
    elif result_option == '4T':
        result_message += "TỨ TRẮNG"
        emojis = "⚪️⚪️\n⚪️⚪️"
    elif result_option == '4D':
        result_message += "TỨ ĐEN"
        emojis = "⚫️⚫️\n⚫️⚫️"

    await update.message.reply_text(result_message)
    emojis_lines = "\n".join([emojis] * 1)
    await update.message.reply_text(emojis_lines)

    winners = {}
    for user_id, bets in xocdia_bets.items():
        user_total_winnings = 0
        for choice, amount in bets:
            if choice == result_option:
                if choice in ['L', 'C']:
                    user_total_winnings += amount * 2
                elif choice in ['3T', '3D']:
                    user_total_winnings += amount * 4
                elif choice in ['4T', '4D']:
                    user_total_winnings += amount * 16
        if user_total_winnings > 0:
            winners[user_id] = user_total_winnings

    result_message = "Kết quả cược:\n"
    if len(winners) == 0:
        result_message += "Không có người chơi nào thắng cược!"
    else:
        result_message += "Người chơi - Tiền thắng\n"
        for user_id, amount_won in winners.items():
            update_user_balance(user_id, amount_won)
            result_message += f"{user_id} - {format_currency(amount_won)}\n"

    # Đảm bảo khai báo biến toàn cục trước khi sử dụng
async def some_function(update, context):
    global xocdia_game_active  # Khai báo biến toàn cục ở đây
    await update.message.reply_text(result_message)
    xocdia_bets.clear()
    xocdia_game_active = True  # Thay đổi giá trị của biến toàn cục

def convert_floats_to_ints(data):
    if isinstance(data, float):
        return int(data)
    elif isinstance(data, list):
        return [convert_floats_to_ints(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_floats_to_ints(value) for key, value in data.items()}
    else:
        return data

def restrict_private_chats(func):
    @wraps(func)
    async def wrapper(update, context):
        if update.message.chat_id < 0:
            return await func(update, context)
        else:
            await update.message.reply_text(
                "Chỉ có thể sử dụng lệnh này trong nhóm.\nNHÓM CHÍNH CỦA BOT : t.me/aniosvip \nCÁC NHÓM KHÁC ĐỀU LÀ GIẢ MẠO, CƯỚP BOT"
            )
    return wrapper

def restrict_group(func):
    @wraps(func)
    async def wrapper(update, context):
        if update.message.chat_id == -1002066327546:
            return await func(update, context)
        else:
            await update.message.reply_text(
                "Địt mẹ sài sài cái lồn.\nt.me/aniosvip mua source bot ib")
    return wrapper

def update_user_balance(user_id, amount):
    global user_balances
    user_balances[user_id] = user_balances.get(user_id, 0) + amount
    save_user_balances()

def draw_card():
    return random.choice(
        ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'])

def format_cards(cards):
    return ', '.join(cards)

def format_currency(amount):
    return "{:,}".format(amount)

@restrict_room
async def bac(update, context):
    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return
    args = context.args

    if len(args) != 1:
        await update.message.reply_text("Sử dụng: /bac <Số tiền cược hoặc 'all'>")
        return

    if args[0].lower() == 'all':
        bet_amount = user_balances.get(user_id, 0)
    else:
        try:
            bet_amount = int(args[0])
        except ValueError:
            await update.message.reply_text("Số tiền cược phải là một số nguyên hoặc 'all'.")
            return

    if bet_amount <= 0:
        await update.message.reply_text("Số tiền cược phải lớn hơn 0.")
        return

    if user_balances.get(user_id, 0) < bet_amount:
        await update.message.reply_text("Số dư của bạn không đủ để đặt cược.")
        return

    update_user_balance(user_id, -bet_amount)

    player_cards = [draw_card(), draw_card()]
    banker_cards = [draw_card(), draw_card()]
    player_total = calculate_total_value_bac(player_cards)
    banker_total = calculate_total_value_bac(banker_cards)
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    await context.bot.send_photo(chat_id=chat_id, photo=open('bacchaha.jfif', 'rb'))
    await update.message.reply_text(
        f"💰 Bạn đã đặt cược {format_currency(bet_amount)} vào trò chơi Baccarat! 💰\n\n🃏 Bài của bạn: {format_cards(player_cards)}\n🃏 Bài của người chia: {format_cards(banker_cards[0])} và một lá ẩn.\n\n> /bactiep < để rút thêm lá bài"
    )

    context.chat_data[user_id] = {
        "bet_amount": bet_amount,
        "player_cards": player_cards,
        "banker_cards": banker_cards,
        "player_total": player_total,
        "banker_total": banker_total
    }

@restrict_room
async def bactiep(update, context):
    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return
    if user_id not in context.chat_data:
        await update.message.reply_text("Bạn chưa tham gia trò chơi Baccarat nào.")
        return

    player_cards = context.chat_data[user_id]["player_cards"]
    banker_cards = context.chat_data[user_id]["banker_cards"]

    player_cards.append(draw_card())
    player_total = calculate_total_value_bac(player_cards)

    if player_total <= 5:
        banker_cards.append(draw_card())
        banker_total = calculate_total_value_bac(banker_cards)
    else:
        banker_total = calculate_total_value_bac(banker_cards)

    await update.message.reply_text(
        f"🃏 Bài của bạn: {format_cards(player_cards)}\n🃏 Bài của người chia: {format_cards(banker_cards)}"
    )

    player_result = compare_bac(player_total, banker_total)
    if player_result == "win":
        await update.message.reply_text(
            f"🎉 Bạn đã thắng! Số tiền nhận được: {format_currency(context.chat_data[user_id]['bet_amount'] * 2)} 🎉"
        )
        update_user_balance(user_id, context.chat_data[user_id]['bet_amount'] * 2)
    elif player_result == "lose":
        await update.message.reply_text("😔 Bạn đã thua. Thử lại lần sau nhé! ❌")
        update_user_balance(user_id, -context.chat_data[user_id]['bet_amount'])
    else:
        await update.message.reply_text(
            "😐 Hòa. Số điểm của bạn và người chia bằng nhau."
        )
        update_user_balance(user_id, context.chat_data[user_id]['bet_amount'])

    del context.chat_data[user_id]

def calculate_total_value_bac(cards):
    total_value = sum([
        10 if card in ['J', 'Q', 'K'] else 0 if card == 'A' else int(card)
        for card in cards
    ]) % 10
    return total_value

def compare_bac(player_total, banker_total):
    if player_total > banker_total:
        return "win"
    elif player_total < banker_total:
        return "lose"
    else:
        return "tie"

@restrict_room
async def blackjack(update, context):
    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return
    args = context.args

    if len(args) != 1:
        await update.message.reply_text("Sử dụng: /bj <Số tiền cược hoặc 'all'>")
        return

    if args[0].lower() == 'all':
        bet_amount = user_balances.get(user_id, 0)
    else:
        try:
            bet_amount = int(args[0])
        except ValueError:
            await update.message.reply_text("Số tiền cược phải là một số nguyên hoặc 'all'.")
            return

    if bet_amount < 1000:
        await update.message.reply_text("Số tiền cược phải lớn hơn hoặc bằng 1000.")
        return

    if user_balances.get(user_id, 0) < bet_amount:
        await update.message.reply_text("Số dư của bạn không đủ để đặt cược.")
        return

    update_user_balance(user_id, -bet_amount)
    dealer_cards = draw_initial_cards()
    player_cards = draw_initial_cards()
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    await context.bot.send_photo(chat_id=chat_id, photo=open('bjhaha.jfif', 'rb'))
    await update.message.reply_text(
        f"💰 Bạn đã đặt cược {format_currency(bet_amount)} vào game Blackjack! 💰\n\n🃏 Bài của bạn: {format_cards(player_cards)}\n🃏 Bài của nhà cái: {format_cards(dealer_cards[0])} và một lá ẩn.\n\n> /hit < để rút thêm lá bài\n\n> /stand < để dừng cược và xem KQ"
    )

    context.chat_data[user_id] = {
        "bet_amount": bet_amount,
        "dealer_cards": dealer_cards,
        "player_cards": player_cards,
        "stand": False
    }

@restrict_room
async def hit(update, context):
    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return
    if user_id not in context.chat_data:
        await update.message.reply_text("Bạn chưa tham gia game Blackjack nào.")
        return

    if context.chat_data[user_id]["stand"]:
        await update.message.reply_text("Bạn đã chọn Stand, không thể rút thêm.")
        return

    player_cards = context.chat_data[user_id]["player_cards"]
    player_cards.append(draw_card())

    await update.message.reply_text(
        f"🃏 Bạn đã rút thêm một lá: {format_cards([player_cards[-1]])}\n🃏 Bài của bạn: {format_cards(player_cards)}"
    )

    total_value = calculate_total_value(player_cards)
    if total_value > 21:
        await update.message.reply_text(
            f"😔 Bạn đã vượt quá 21! Bạn đã thua {format_currency(context.chat_data[user_id]['bet_amount'])}."
        )
        update_user_balance(user_id, -context.chat_data[user_id]['bet_amount'])
        del context.chat_data[user_id]
    elif total_value == 21:
        await update.message.reply_text(
            f"🎉 Chúc mừng! Bạn đã có 21 điểm! Bạn đã thắng {format_currency(context.chat_data[user_id]['bet_amount'] * 2)}."
        )
        update_user_balance(user_id, context.chat_data[user_id]['bet_amount'] * 2)
        del context.chat_data[user_id]

@restrict_room
async def stand(update, context):
    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return
    if user_id not in context.chat_data:
        await update.message.reply_text("Bạn chưa tham gia game Blackjack nào.")
        return

    if context.chat_data[user_id]["stand"]:
        await update.message.reply_text("Bạn đã chọn Stand, không thể chọn lại.")
        return

    context.chat_data[user_id]["stand"] = True
    dealer_cards = context.chat_data[user_id]["dealer_cards"]
    player_cards = context.chat_data[user_id]["player_cards"]

    while calculate_total_value(dealer_cards) < 17:
        dealer_cards.append(draw_card())
        await asyncio.sleep(0)  # cho phép yield control

    dealer_total = calculate_total_value(dealer_cards)
    player_total = calculate_total_value(player_cards)

    await update.message.reply_text(
        f"🃏 Bài của nhà cái: {format_cards(dealer_cards)}"
    )
    await asyncio.sleep(1)

    if dealer_total > 21 or dealer_total < player_total:
        await update.message.reply_text(
            f"🎉 Chúc mừng! Bạn đã thắng {format_currency(context.chat_data[user_id]['bet_amount'] * 2)}."
        )
        update_user_balance(user_id, context.chat_data[user_id]['bet_amount'] * 2)
    elif dealer_total == player_total:
        await update.message.reply_text(
            f"😐 Hòa. Số điểm của bạn và nhà cái đều là {player_total}."
        )
        update_user_balance(user_id, context.chat_data[user_id]['bet_amount'])
    else:
        await update.message.reply_text(
            f"😔 Bạn đã thua. Số điểm của nhà cái ({dealer_total}) cao hơn số điểm của bạn ({player_total})."
        )
        update_user_balance(user_id, -context.chat_data[user_id]['bet_amount'])

    del context.chat_data[user_id]

def draw_initial_cards():
    return [draw_card(), draw_card()]

def draw_card():
    return random.choice(
        ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'])

def format_cards(cards):
    return ', '.join(cards)

def calculate_total_value(cards):
    total_value = 0
    number_of_aces = 0

    for card in cards:
        if card.isdigit():
            total_value += int(card)
        elif card in ['J', 'Q', 'K']:
            total_value += 10
        elif card == 'A':
            number_of_aces += 1
            total_value += 11

    while total_value > 21 and number_of_aces > 0:
        total_value -= 10
        number_of_aces -= 1

    return total_value

@restrict_room
async def taolistcode(update, context):
    user_id = update.message.from_user.id
    if user_id != 6793700101:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return

    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Sử dụng: /taolistcode <Số tiền 1 code> <Số code>")
        return

    try:
        amount_per_code = int(args[0])
        num_codes = int(args[1])
    except ValueError:
        await update.message.reply_text("Số tiền và số code phải là số nguyên.")
        return

    if amount_per_code <= 0 or num_codes <= 0:
        await update.message.reply_text("Số tiền và số code phải lớn hơn 0.")
        return

    code_list = []
    for _ in range(num_codes):
        code_name = generate_random_code(length=10)
        codes[code_name] = (amount_per_code, 1, False)
        code_list.append(code_name)

    save_codes()

    code_list_text = "\n".join(code_list)
    await context.bot.send_message(
        chat_id=-1002066327546,
        text=f"Đây Là List Code Mới\n\n{code_list_text}\n\nLệnh Sài /code <code> để nhập code\nhttps://t.me/ztrongzcode"
    )

@restrict_room
async def roulette(update, context):
    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return
    args = context.args

    if len(args) != 2:
        await update.message.reply_text(
            "Sử dụng: /rou <C hoặc L hoặc số từ 0 đến 36> <Số tiền cược hoặc 'all'>\nC và L : Tỷ lệ ăn 1:2\n0 - 36 : Tỷ lệ ăn khi trúng số là 1:35\n0 : Nổ JACKPOT"
        )
        return

    choice = args[0].upper()
    valid_choices = ['C', 'L'] + [str(i) for i in range(37)]
    if choice not in valid_choices:
        await update.message.reply_text("Lựa chọn không hợp lệ. Vui lòng chọn 'C', 'L' hoặc số từ 0 đến 36.")
        return

    if args[1].lower() == 'all':
        amount = user_balances.get(user_id, 0)
    else:
        try:
            amount = int(args[1])
        except ValueError:
            await update.message.reply_text("Số tiền cược phải là một số nguyên hoặc 'all'.")
            return

    if amount < 1000:
        await update.message.reply_text("Số tiền cược phải lớn hơn hoặc bằng 1000.")
        return

    if user_balances.get(user_id, 0) < amount:
        await update.message.reply_text("Số dư của bạn không đủ để đặt cược.")
        return

    update_user_balance(user_id, -amount)
    gif_url = "https://media.giphy.com/media/T2JZjjKwucfyZfq6I8/giphy.gif"
    await update.message.reply_animation(animation=gif_url)
    spin_result = random.randint(0, 36)
    is_even = spin_result % 2 == 0 and spin_result != 0
    is_odd = spin_result % 2 != 0
    await update.message.reply_text("🎡 Hãy Chờ Đợi Kết Quả Quay!!")
    await asyncio.sleep(1)
    await update.message.reply_text("🎡 Rolling !!")
    await update.message.reply_text("🎡 Kết Quả Quay Đã Được Xác Định!!")
    await asyncio.sleep(1)
    await update.message.reply_text(f"🎡 Kết quả quay là : {spin_result} 🎡")
    await asyncio.sleep(2)

    win_amount = 0
    if choice == 'C' and is_even:
        win_amount = amount * 2
    elif choice == 'L' and is_odd:
        win_amount = amount * 2
    elif choice == str(spin_result):
        win_amount = amount * 35

    if win_amount > 0:
        update_user_balance(user_id, win_amount)
        await update.message.reply_text(f"🎉 Bạn đã thắng! Số tiền nhận được: {format_currency(win_amount)} 🎉")
    else:
        await update.message.reply_text("❌ Bạn đã thua. Thử lại lần sau nhé! ❌")
        await update.message.reply_text(f"Số dư hiện tại của bạn: {format_currency(user_balances.get(user_id, 0))}")

    if spin_result == 0:
        jackpot_amount = load_jackpot()
        update_user_balance(user_id, jackpot_amount)
        message_text = f"🌟 Bạn đã nổ JACKPOT và nhận được {format_currency(jackpot_amount)}! 🌟"
        sent_message = await update.message.reply_text(message_text)
        await update.message.bot.pin_chat_message(chat_id=update.effective_chat.id, message_id=sent_message.message_id, disable_notification=True)
        save_jackpot(0)
        record_jackpot_winner(user_id, jackpot_amount)

def load_used_codes():
    try:
        with open('used_codes.txt', 'r') as file:
            content = file.read().strip()
            if content == '':
                return {}
            file.seek(0)
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Lỗi JSONDecodeError: {e}")
        return {}

def save_used_code(used_codes):
    with open('used_codes.txt', 'w') as file:
        json.dump(used_codes, file, ensure_ascii=False, indent=4)

def has_used_code(user_id, code_name):
    used_codes = load_used_codes()
    return code_name in used_codes.get(str(user_id), [])

def record_used_code(user_id, code_name):
    used_codes = load_used_codes()
    if str(user_id) not in used_codes:
        used_codes[str(user_id)] = []
    used_codes[str(user_id)].append(code_name)
    save_used_code(used_codes)

def generate_random_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

async def taocode(update, context):
    user_id = update.message.from_user.id
    args = context.args

    if len(args) != 2:
        await update.message.reply_text("Sử dụng: /taocode <số tiền> <số lượt sử dụng>")
        return

    try:
        amount = int(args[0])
        uses_left = int(args[1])
    except ValueError:
        await update.message.reply_text("Số tiền và số lượt sử dụng phải là các số nguyên.")
        return

    if amount <= 0 or uses_left <= 0:
        await update.message.reply_text("Số tiền và số lượt sử dụng phải lớn hơn 0.")
        return

    fee = int(amount * 0.1)
    total_amount = amount - fee

    amount_to_deduct = int(amount * 0.02)
    update_user_balance(user_id, -amount_to_deduct)

    if user_balances.get(user_id, 0) < total_amount:
        await update.message.reply_text("Số dư của bạn không đủ để tạo code.")
        return

    update_user_balance(user_id, -total_amount)

    code_name = generate_random_code()

    code_data = f"{code_name}:{total_amount}:{uses_left}:False\n"
    with open('code.txt', 'a') as file:
        file.write(code_data)

    jackpot_amount = total_amount / 1000  
    update_jackpot(jackpot_amount)

    await update.message.reply_text(
        f"Bạn đã tạo code: {code_name} với số tiền: {format_currency(total_amount)} và số lượt sử dụng: {uses_left}. Số tiền đã được cộng vào hũ."
    )

def load_jackpot():
    if os.path.exists("jackpot.txt"):
        with open("jackpot.txt", "r") as file:
            return ast.literal_eval(file.read())
    return 0

def save_jackpot(jackpot):
    with open("jackpot.txt", "w") as file:
        file.write(str(jackpot))

@restrict_group
async def lsjackpot(update, context):
    jackpot_history = load_jackpot_history()
    if not jackpot_history:
        await update.message.reply_text("Chưa có lịch sử hũ.")
        return

    response = "🎉 Lịch sử hũ 🎉\n"
    for user_id, won_amount in jackpot_history:
        response += f"Người chơi ID {user_id} đã thắng hũ với số tiền\n👉{format_currency(won_amount)}\n\n"
    await update.message.reply_text(response)

async def jackpot_command(update, context):
    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return
    jackpot_amount = load_jackpot()
    if jackpot_amount > MAX_JACKPOT_AMOUNT:
        jackpot_amount = MAX_JACKPOT_AMOUNT 
        save_jackpot(jackpot_amount)
    await update.message.reply_text(
        f"💰 Số tiền hiện có trong Jackpot là:\n\n{format_currency(jackpot_amount)}\n\n"
        "💰Ra Bão = Hũ JACKPOT🎲\n💰Ra 0 Ở Roulette = Hũ JACKPOT 🎡\n\n"
        "Pay : Tổng số tiền tạo chia 1000 và cộng hũ"
    )

def calculate_tax(amount):
    return amount * 10

def load_transaction_history():
    if os.path.exists(transaction_history_file):
        with open(transaction_history_file, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                logger.error("Malformed JSON or empty transaction history file.")
                return []
    return []

def save_transaction_history(history):
    with open(transaction_history_file, "w") as file:
        json.dump(history, file)

def record_transaction(user_id, transaction_type, amount):
    history = load_transaction_history()
    if user_id not in history:
        history[user_id] = []
    history[user_id].append({
        "user_id": user_id,
        "transaction_type": transaction_type,
        "amount": amount,
        "timestamp": time.time()
    })
    save_transaction_history(history)

def load_jackpot_history():
    jackpot_history = []
    if os.path.exists("history.txt"):
        with open("history.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                user_id, won_amount = line.strip().split(":")
                jackpot_history.append((int(user_id), int(won_amount)))
    return jackpot_history

def load_user_balances():
    global user_balances
    user_balances = {}
    try:
        with open("sodu.txt", "r") as file:
            for line in file:
                parts = line.strip().split(":")
                if len(parts) == 2:
                    user_id, balance = parts
                    try:
                        balance_value = float(balance)
                        if balance_value == float('inf'):
                            print(f"Warning: user_id {user_id} has an infinite balance. Setting to default.")
                            balance_value = 123123123123123123123123123
                        user_balances[int(user_id)] = int(balance_value)
                    except ValueError:
                        print(f"Error: Invalid balance value for user_id {user_id}. Skipping.")
                else:
                    print(f"Error: Invalid line format -> {line.strip()}")
    except FileNotFoundError:
        print("User balances file not found. Initializing empty balances.")

def save_user_balances():
    global user_balances
    with open(sodu_file_path, "w") as file:
        for user_id, balance in user_balances.items():
            file.write(f"{user_id}:{balance}\n")

def load_codes():
    global codes
    if os.path.exists(codes_file_path):
        with open(codes_file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                data = line.strip().split(":")
                if len(data) == 4:
                    code_name, amount, uses_left, used = data
                    codes[code_name] = (float(amount), float(uses_left), used == "True")
                else:
                    print(f"Đang bỏ qua dòng không hợp lệ: {line}")
                    
def save_codes():
    global codes
    with open(codes_file_path, "w") as file:
        for code_name, (amount, uses_left, used) in codes.items():
            file.write(f"{code_name}:{amount}:{uses_left}:{used}\n")

def load_user_code_usage():
    global user_code_usage
    if os.path.exists(user_code_usage_file):
        with open(user_code_usage_file, "r") as file:
            user_code_usage = json.load(file)

def save_user_code_usage():
    global user_code_usage
    with open(user_code_usage_file, "w") as file:
        json.dump(user_code_usage, file)

def update_user_balance(user_id, amount):
    global user_balances
    user_balances[user_id] = user_balances.get(user_id, 0) + amount
    save_user_balances()

def format_currency(amount):
    return "{:,}".format(amount)

@restrict_room
async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    user_id = user.id

    if update.message.chat.type != 'private':  
        await update.message.reply_text(
            "Chỉ có thể sử dụng lệnh /start trong chat riêng với bot."
        )
        return

    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return

    if user_id not in user_balances:
        update_user_balance(user_id, 0)

    keyboard = [
        [KeyboardButton("👤 Tài Khoản"), KeyboardButton("💵 Xem Số Dư")],
        [KeyboardButton("🎰 Danh Sách Game"), KeyboardButton("👥 Mời Bạn")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        f"🎲𝙕𝙂𝙧𝙤𝙪𝙥 - 𝘾𝙖𝙨𝙞𝙣𝙤 𝘽𝙤𝙩 𝙏𝙚𝙡𝙚𝙂𝙧𝙖𝙢🎲\n"
        f"👉 t.me/aniosvip  👈 \n"
        f"🎲𝙕𝙍𝙤𝙤𝙢 - 𝙍𝙤𝙤𝙢 𝘽𝙤𝙩 𝙏𝙚𝙡𝙚𝙂𝙧𝙖𝙢🎲\n"
        f"👉 t.me/aniosvip 👈 \n"
        f"🎲𝙕𝘾𝙝𝙖𝙩 - 𝙍𝙤𝙤𝙢 𝘾𝙝𝙖𝙩 𝘼𝙡𝙡🎲\n"
        f"👉 t.me/aniosvipchat 👈 \n"
        f"🍀ADMIN : @aypt09🍀 \n"
        f"𝐒à𝐧 𝐂𝐚𝐬𝐢𝐧𝐨 𝐗𝐮 Ả𝐨 𝐆𝐢ả𝐢 𝐓𝐫í 𝐒ố 𝟏 𝐕𝐍",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if text == "👤 Tài Khoản":
        await profile(update, context)
    elif text == "💵 Xem Số Dư":
        await sd(update, context)
    elif text == "🎰 Danh Sách Game":
        await game(update, context)
    elif text == "👥 Mời Bạn":
        await moi_ban(update, context)
    else:
        return

invited_users = {}

async def moi_ban(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in invited_users:
        invite_link = f"https://t.me/nhacaihungyen_bot?start={user_id}"
        await update.message.reply_text(
            f"👥 Mời bạn bè bằng cách gửi link sau: {invite_link}\n\n"
            f"👥 Khi mời đủ 10 bạn bè bạn sẽ nhận được 10,000 VND từ @aypt09"
        )
        invited_users[user_id] = invited_users.get(user_id, 0) + 1
        save_invited_users()
        if invited_users[user_id] == 1:
            await update.message.reply_text("🎉 Bạn đã mời thành công 1 người.")
        else:
            await update.message.reply_text(f"🎉 Bạn đã mời thành công {invited_users[user_id]} người.")
    else:
        await update.message.reply_text("ℹ️ Bạn đã được mời rồi.")

async def handle_show_invited_count(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in invited_users:
        await update.message.reply_text(f"📄 Số người bạn đã mời: {invited_users[user_id]}")
    else:
        await update.message.reply_text("ℹ️ Bạn chưa mời ai cả.")

def save_invited_users():
    with open(CHECKBB_FILE, "w") as file:
        for user_id, count in invited_users.items():
            file.write(f"{user_id}:{count}\n")

def load_invited_users():
    if os.path.exists(CHECKBB_FILE):
        with open(CHECKBB_FILE, "r") as file:
            for line in file:
                user_id, count = line.strip().split(":")
                invited_users[int(user_id)] = int(count)

async def reset_jackpot(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Cút")
        return
    if len(context.args) != 1:
        await update.message.reply_text("Sử dụng: /resetjackpot <số dư>")
        return

    try:
        new_jackpot_amount = int(context.args[0])
        if new_jackpot_amount < 0:
            raise ValueError("Số dư không thể âm.")
        save_jackpot(new_jackpot_amount)
        await update.message.reply_text(f"Jackpot đã được đặt lại thành: {format_currency(new_jackpot_amount)}")
    except ValueError:
        await update.message.reply_text("Số dư phải là một số nguyên dương.")

@restrict_room
async def send_dice_results(update, context):
    chat_id = update.message.chat_id
    dice_values = []
    for i in range(3):
        dice = (await context.bot.send_dice(chat_id=chat_id)).dice
        await asyncio.sleep(1)
        dice_values.append(dice.value)
    total = sum(dice_values)
    if 18 >= total >= 11:
        result = "T"
    else:
        result = "X"
    await asyncio.sleep(1)
    await update.message.reply_text(f"🎮 Tổng 🎮: {total}\n\n🎁 Kết quả 🎁: {result}")
    return dice_values, result, total

@restrict_room
async def taixiu(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    args = context.args

    if len(args) != 2:
        await update.message.reply_text("Sử dụng: /tx <T hoặc X> <Số tiền cược hoặc 'all'>")
        return

    choice = args[0].upper()
    if choice not in ['T', 'X']:
        await update.message.reply_text("Lựa chọn không hợp lệ. Vui lòng chọn 'T' hoặc 'X'.")
        return

    if args[1].lower() == 'all':
        amount = user_balances.get(user_id, 0)
    else:
        try:
            amount = int(args[1])
        except ValueError:
            await update.message.reply_text("Số tiền cược phải là một số nguyên hoặc 'all'.")
            return

    if amount < 1000:
        await update.message.reply_text("Số tiền cược phải lớn hơn hoặc bằng 1000.")
        return

    if user_balances.get(user_id, 0) < amount:
        await update.message.reply_text("Số dư của bạn không đủ để đặt cược.")
        return

    record_transaction(user_id, "start_taixiu", amount)
    update_user_balance(user_id, -amount)

    dice_values, result, total = await send_dice_results(update, context)

    if result == choice:
        win_amount = amount * 1.95
        update_user_balance(user_id, win_amount)
        await update.message.reply_text(f"🎉 Chúc mừng bạn đã thắng! 🎉\n🏆 Số tiền nhận được: {format_currency(win_amount)}\n💰 Số dư mới: {format_currency(user_balances[user_id])}")
        record_transaction(user_id, "end_taixiu", win_amount)
    else:
        await update.message.reply_text("❌ Rất tiếc, bạn đã thua! 🎲")
        await update.message.reply_text(f"💰 Số dư mới của bạn là: {format_currency(user_balances[user_id])}")
        record_transaction(user_id, "end_taixiu", -amount)

    if len(set(dice_values)) == 1 and dice_values[0] in [1, 2, 3, 4, 5, 6]:
        jackpot_amount = load_jackpot()
        update_user_balance(user_id, jackpot_amount)
        jackpot_message = f"🌟🌟🌟 Chúc mừng! {user_id} đã trúng JACKPOT với số tiền {format_currency(jackpot_amount)} 🌟🌟🌟\nSố dư hiện tại của bạn: {format_currency(user_balances.get(user_id, 0))}"
        jackpot_sent_message = await update.message.reply_text(jackpot_message)
        await context.bot.pin_chat_message(chat_id=update.effective_chat.id, message_id=jackpot_sent_message.message_id, disable_notification=True)
        save_jackpot(0)
        record_jackpot_winner(user_id, jackpot_amount)

@restrict_room
async def open_all_games(update, context):
    global taixiu_game_active, aviator_game_active, roulette_game_active, xocdia_game_active, horse_race_active

    # Kích hoạt tất cả các trò chơi
    taixiu_game_active = True
    aviator_game_active = True
    roulette_game_active = True
    xocdia_game_active = True
    horse_race_active = True

    # Thông báo tất cả trò chơi đã được mở
    await update.message.reply_text(
        "🎮 Tất cả các trò chơi đã được mở:\n"
        "1. Taixiu\n"
        "2. Aviator\n"
        "3. Roulette\n"
        "4. Xóc Đĩa\n"
        "5. Đua Ngựa\n"
        "Bây giờ bạn có thể tham gia bất kỳ trò chơi nào!"
    )

# Các trò chơi khác vẫn giữ nguyên với lệnh riêng của chúng, ví dụ:

# Lệnh /taixiu
@restrict_room
async def start_taixiu(update, context):
    global taixiu_game_active
    if not taixiu_game_active:
        await update.message.reply_text("Trò chơi Taixiu chưa được mở. Vui lòng mở trò chơi trước.")
        return
    # Logic bắt đầu trò chơi Taixiu

# Lệnh /aviator
@restrict_room
async def start_aviator(update, context):
    global aviator_game_active
    if not aviator_game_active:
        await update.message.reply_text("Trò chơi Aviator chưa được mở. Vui lòng mở trò chơi trước.")
        return
    # Logic bắt đầu trò chơi Aviator

# Lệnh /roulette
@restrict_room
async def start_roulette(update, context):
    global roulette_game_active
    if not roulette_game_active:
        await update.message.reply_text("Trò chơi Roulette chưa được mở. Vui lòng mở trò chơi trước.")
        return
    # Logic bắt đầu trò chơi Roulette

# Lệnh /xocdia
@restrict_room
async def start_xocdia(update, context):
    global xocdia_game_active
    if not xocdia_game_active:
        await update.message.reply_text("Trò chơi Xóc Đĩa chưa được mở. Vui lòng mở trò chơi trước.")
        return
    # Logic bắt đầu trò chơi Xóc Đĩa

# Lệnh /horserace
@restrict_room
async def start_horse_race(update, context):
    global horse_race_active
    if not horse_race_active:
        await update.message.reply_text("Trò chơi Đua Ngựa chưa được mở. Vui lòng mở trò chơi trước.")
        return
    # Logic bắt đầu trò chơi Đua Ngựa

@restrict_room
async def chuyentien(update, context):
    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return
    args = context.args

    if update.message.reply_to_message and len(args) == 1:
        recipient_id = update.message.reply_to_message.from_user.id
        try:
            amount = int(args[0])
        except ValueError:
            await update.message.reply_text("Số tiền cần là một số nguyên.")
            return
    elif len(args) == 2:
        try:
            amount = int(args[0])
            recipient_id = int(args[1])
        except ValueError:
            await update.message.reply_text("Số tiền và ID người nhận phải là các số nguyên.")
            return
    else:
        await update.message.reply_text("Có 2 Cách Chuyển :\n✅CÁCH 1 : /pay <số tiền chuyển> <ID> \n\n✅CÁCH 2 : /pay <số tiền chuyển> (Reply Tin Nhắn User Bạn Chuyển Tới)")
        return

    if amount <= 0:
        await update.message.reply_text("Số tiền phải lớn hơn 0.")
        return

    if amount < 10000000:
        await update.message.reply_text("✅ Hạn Mức Chuyển ✅\nMIN = 10,000,000 VND")
        return

    if user_balances.get(user_id, 0) < amount:
        await update.message.reply_text("Số dư của bạn không đủ để thực hiện giao dịch này.")
        return

    if recipient_id == user_id:
        await update.message.reply_text("⁉️ Bot Không Thể Chuyển Cho Bot ⁉️")
        return

    fee = amount * 0.1
    net_amount = amount - fee

    user_balances[user_id] -= amount

    if user_balances[user_id] < 0:
        user_balances[user_id] += amount
        await update.message.reply_text("Giao dịch không thành công. Số dư của bạn không đủ để thực hiện giao dịch này.")
        return

    if recipient_id not in user_balances:
        user_balances[recipient_id] = 0
    user_balances[recipient_id] += net_amount

    update_jackpot(fee)

    try:
        await context.bot.send_message(
            chat_id=recipient_id,
            text=f"✅ Bạn đã nhận được {format_currency(net_amount)} từ người dùng có ID {user_id}."
        )
    except Exception as e:
        username = f"@{update.message.reply_to_message.from_user.username}" if update.message.reply_to_message.from_user.username else f"ID {recipient_id}"
        await update.message.reply_text(f"🚫 Không thể chuyển vì user nhận chưa có contact với bot\n🌐 {username} Vui Lòng Nhắn Bot @nhacaihungyen_bot 🌐")
        user_balances[user_id] += amount  # Revert the transaction
        user_balances[recipient_id] -= net_amount
        update_jackpot(-fee)  # Revert the fee update
        return

    await update.message.reply_text(f"✅ Bạn đã chuyển {format_currency(amount)} tới người dùng có ID {recipient_id}. Phí 10% đã được trích xuống hũ.")
@restrict_room
async def sd(update: Update, context: CallbackContext) -> None:
    """Hiển thị số dư tài khoản"""
    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return
    
    balance = user_balances.get(user_id, 0)
    await update.message.reply_text(f"💰 Số dư hiện tại của bạn: {format_currency(balance)}")

# Định nghĩa hàm profile() nếu chưa có
@restrict_room
async def profile(update: Update, context: CallbackContext) -> None:
    """Hiển thị thông tin cá nhân"""
    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return
    
    balance = user_balances.get(user_id, 0)
    username = update.message.from_user.username or "Không có"
    first_name = update.message.from_user.first_name or "Không có"
    last_name = update.message.from_user.last_name or "Không có"
    
    await update.message.reply_text(
        f"👤 Thông tin tài khoản:\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Tên: {first_name} {last_name}\n"
        f"📛 Username: @{username}\n"
        f"💰 Số dư: {format_currency(balance)}\n\n"
        f"📌 Liên hệ admin: @aypt09"
    )

@restrict_room
async def help_command(update, context):
    user_id = update.message.from_user.id
    if user_id in banned_users:
        await update.message.reply_text("Bạn không được phép sử dụng bot.")
        return
    await update.message.reply_text(
        "🕹️ /start: Lệnh Thường✨\n\n"
        "🕹️ /game : Xem danh sách game và các lệnh🕹️\n\n"
        "🕹️ /sd : Xem số dư 💰\n\n"
        "🕹️ /profile : Xem profile 💰\n\n"
        "🕹️ /code : Nhập mã code 🔄\n\n"
        "🕹️ /jackpot : Xem tiền JACKPOT 💰\n\n"
        "🕹️ /pay : Chuyển tiền 💸\n\n"
        "🕹️ /doitien : Đổi tiền sang code 🔄\n\n"
        "🕹️ /top : Top số dư 💸\n\n"
        "📌 HỖ TRỢ 📌\n"
        "🕹️ ADMIN GAME : @aypt09 ❤️\n"
        "Thắc Mắc/Góp Ý/Báo Lỗi - Mua/Thuê Code Bot IB để được hỗ trợ\n\n"
        "Zalo : 0345421396\n"
        "FB : nguyenan261129"
    )

def game(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💵 Nạp Xu 💵", callback_data='nap')],
        [InlineKeyboardButton("💵 Rút Xu 💵", callback_data='rutmomo')],
        [InlineKeyboardButton("💰 Giá Xu 💰", callback_data='giaxu')],
        [InlineKeyboardButton("🎲 Tài Xỉu 🎲", callback_data='tx'),
         InlineKeyboardButton("🎲 Tài Xỉu Room 🎲", callback_data='room')],
        [InlineKeyboardButton("🃏 Blackjack 🃏", callback_data='bj'),
         InlineKeyboardButton("🎰 Roulette 🎰", callback_data='rou')],
        [InlineKeyboardButton("🎴 Baccarat 🎴", callback_data='bac'),
         InlineKeyboardButton("✈️ Aviator ✈️", callback_data='startav')],
        [InlineKeyboardButton("🎲 Sicbo 🎲", callback_data='sicbo'),
         InlineKeyboardButton("🎱 Keno 🎱", callback_data='keno')],
        [InlineKeyboardButton("⚪️ Xóc Đĩa Room ⚫️", callback_data='xocdia'),
         InlineKeyboardButton("🏇 Đua Ngựa 🏇", callback_data='starth')],
        [InlineKeyboardButton("🎰 Slot 🎰", callback_data='slot'),
         InlineKeyboardButton("⚪️ Chẵn Lẻ ⚫️", callback_data='chanle')],
        [InlineKeyboardButton("🎲 Solo Xúc Xắc 🎲", callback_data='solo')],
        [InlineKeyboardButton("🎫 Xổ Số 30S 🎫", callback_data='xs'),
         InlineKeyboardButton("🧧 Lân Hái Lộc 🧧", callback_data='hailoc')],
        [InlineKeyboardButton("💰 JACKPOT 💰", callback_data='jackpot'),
         InlineKeyboardButton("🧧 HŨ LỘC 🧧", callback_data='huloc')],
        [InlineKeyboardButton("✅ Top Số Dư ✅ ", callback_data='top')],
        [InlineKeyboardButton("🔥 TÀI XỈU ROOM 🔥", url='https://t.me/mieww01')],
        [InlineKeyboardButton("🔥 SICBO ROOM 🔥", url='https://t.me/mieuww01')],
        [InlineKeyboardButton("🔰 Admin Game 🔰", url='https://t.me/aypt09')],
        [InlineKeyboardButton("❤️ Shop Admin ❤️", url='https://t.me/aypt09')],
        [InlineKeyboardButton("✅ Cách Chơi Game ✅", url='https://t.me/aniosvip/')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Dưới đây là các game hiện có và lệnh:", reply_markup=reply_markup)

# Khởi chạy bot
def main() -> None:
    load_invited_users()
    load_user_balances()
    load_codes()
    application = Application.builder().token(TOKEN).build()

    # Đăng ký các CommandHandler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sd", sd))
    application.add_handler(CommandHandler("nap", nap))
    application.add_handler(CommandHandler("bac", bac))
    application.add_handler(CommandHandler("bactiep", bactiep))
    application.add_handler(CommandHandler("bj", blackjack))
    application.add_handler(CommandHandler("hit", hit))
    application.add_handler(CommandHandler("stand", stand))
    application.add_handler(CommandHandler("taolistcode", taolistcode))
    application.add_handler(CommandHandler("rou", roulette))
    application.add_handler(CommandHandler("taocode", taocode))
    application.add_handler(CommandHandler("resetjackpot", reset_jackpot))
    application.add_handler(CommandHandler("jackpot", jackpot_command))
    application.add_handler(CommandHandler("tx", taixiu))
    application.add_handler(CommandHandler("pay", chuyentien))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("taixiu", start_taixiu))
    application.add_handler(CommandHandler("aviator", start_aviator))
    application.add_handler(CommandHandler("roulette", start_roulette))
    application.add_handler(CommandHandler("xocdia", start_xocdia))
    application.add_handler(CommandHandler("horserace", start_horse_race))
    application.add_handler(CommandHandler("all", open_all_games))
    
      
    
    # Đăng ký các handler cho các message không phải lệnh
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Chạy ứng dụng
    application.run_polling()

# Chạy bot khi tệp được thực thi
if __name__ == "__main__":
    main()