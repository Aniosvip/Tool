import random
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Cấu hình bot
TOKEN = '7616169072:AAHJJWTbQtCLGnN98dxCA4KMd5TaZZqOaL8'.strip()
ADMIN_IDS = [6396925073]
ACCOUNT_FILE = 'acc.txt'
COOLDOWN = 1800  # 30 phút

# Biến toàn cục
accounts = []
used_accounts = set()
user_cooldowns = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f'👋 Xin chào {user.first_name}!\n\n'
        'Tôi là bot cung cấp tài khoản ngẫu nhiên.\n'
        'Sử dụng lệnh /get để nhận 15 tài khoản ngẫu nhiên.'
    )

async def get_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_time = time.time()
    is_admin = user_id in ADMIN_IDS

    if not is_admin and user_id in user_cooldowns:
        remaining = user_cooldowns[user_id] - current_time
        if remaining > 0:
            mins, secs = divmod(int(remaining), 60)
            await update.message.reply_text(
                f"⏳ Bạn cần chờ {mins} phút {secs} giây nữa!"
            )
            return

    available = [acc for acc in accounts if acc not in used_accounts]
    if len(available) < 15:
        await update.message.reply_text("⚠️ Đã hết tài khoản! Vui lòng thử lại sau.")
        return

    selected = random.sample(available, 15)
    used_accounts.update(selected)

    # Gửi tin nhắn
    await update.message.reply_text("🎉 Đây là 15 tài khoản ngẫu nhiên:")
    account_list = "\n".join(selected)
    await update.message.reply_text(f"```{account_list}```", parse_mode='Markdown')

    if not is_admin:
        user_cooldowns[user_id] = current_time + COOLDOWN

async def reset_cooldown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này!")
        return

    if not context.args:
        await update.message.reply_text("ℹ️ Vui lòng nhập ID người dùng cần reset")
        return

    try:
        user_id = int(context.args[0])
        if user_id in user_cooldowns:
            del user_cooldowns[user_id]
            await update.message.reply_text(f"✅ Đã reset cooldown cho user {user_id}")
        else:
            await update.message.reply_text(f"ℹ️ User {user_id} không có cooldown")
    except ValueError:
        await update.message.reply_text("❌ ID người dùng không hợp lệ!")

def load_accounts():
    global accounts
    try:
        with open(ACCOUNT_FILE, 'r', encoding='utf-8') as f:
            accounts = [line.strip() for line in f if '|' in line]
        random.shuffle(accounts)
        print(f"✅ Đã tải {len(accounts)} tài khoản")
    except Exception as e:
        print(f"❌ Lỗi khi đọc file: {e}")
        accounts = []

def main():
    try:
        load_accounts()
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("get", get_accounts))
        application.add_handler(CommandHandler("resetcooldown", reset_cooldown))

        print("🤖 Đang khởi động bot...")
        application.run_polling()
    except Exception as e:
        print(f"❌ Lỗi khởi động bot: {e}")

if __name__ == '__main__':
    main()