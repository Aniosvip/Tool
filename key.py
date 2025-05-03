import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    filters
)
import requests

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API endpoints
CHECK_KEY_API = "https://aypt09.ddns.net/anticrack.php?action=checklogin&user={key}"
GET_KEY_URL = "https://aypt09.ddns.net/getkey.php"  # Đây là URL để người dùng tự lấy key

class KeyManager:
    def __init__(self):
        self.active_keys = {}  # {user_id: key}

    def check_key(self, key: str) -> bool:
        try:
            response = requests.get(CHECK_KEY_API.format(key=key))
            if response.status_code == 200:
                return response.text.strip().lower() == "success"
            return False
        except Exception as e:
            logger.error(f"Error checking key: {e}")
            return False

    def activate_key(self, user_id: int, key: str) -> bool:
        if self.check_key(key):
            self.active_keys[user_id] = key
            return True
        return False

    def has_active_key(self, user_id: int) -> bool:
        return user_id in self.active_keys

key_manager = KeyManager()

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if key_manager.has_active_key(user_id):
        await update.message.reply_text("🎉 Bạn đã có key kích hoạt! Bạn có thể sử dụng các bot trong nhóm.")
    else:
        keyboard = [
            [InlineKeyboardButton("🔑 Lấy Key", url=GET_KEY_URL)],  # Mở URL khi bấm nút
            [InlineKeyboardButton("⌨ Nhập Key", callback_data='input_key')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            '🔒 Vui lòng kích hoạt key để sử dụng bot:\n'
            '1. Bấm "🔑 Lấy Key" để đến trang lấy key\n'
            '2. Sau khi có key, bấm "⌨ Nhập Key" hoặc dùng lệnh /activate <key>',
            reply_markup=reply_markup
        )

async def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'input_key':
        await query.edit_message_text(
            "Vui lòng nhập key của bạn bằng lệnh /activate <key>\n"
            f"Ví dụ: /activate KEY123\n\n"
            f"Nếu chưa có key, hãy truy cập: {GET_KEY_URL}"
        )

async def activate_key(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if len(context.args) < 1:
        await update.message.reply_text(
            "⚠ Vui lòng nhập key sau lệnh /activate\n"
            f"Ví dụ: /activate ABC123XYZ\n\n"
            f"Nếu chưa có key, hãy truy cập: {GET_KEY_URL}"
        )
        return

    key = context.args[0].strip()
    if key_manager.activate_key(user_id, key):
        await update.message.reply_text("✅ Kích hoạt key thành công! Bạn có thể sử dụng các bot trong nhóm.")
    else:
        await update.message.reply_text(
            "❌ Key không hợp lệ hoặc đã hết hạn. Vui lòng thử lại.\n"
            f"Nếu chưa có key, hãy truy cập: {GET_KEY_URL}"
        )

async def check_access(update: Update, context: CallbackContext) -> bool:
    user_id = update.effective_user.id
    if not key_manager.has_active_key(user_id):
        keyboard = [
            [InlineKeyboardButton("🔑 Lấy Key", url=GET_KEY_URL)],
            [InlineKeyboardButton("⌨ Nhập Key", callback_data='input_key')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            '🔒 Vui lòng kích hoạt key để sử dụng tính năng này:\n'
            '1. Bấm "🔑 Lấy Key" để đến trang lấy key\n'
            '2. Sau khi có key, bấm "⌨ Nhập Key" hoặc dùng lệnh /activate <key>',
            reply_markup=reply_markup
        )
        return False
    return True

async def premium_command(update: Update, context: CallbackContext) -> None:
    if not await check_access(update, context):
        return
    
    await update.message.reply_text("🌟 Đây là tính năng premium đã được mở khóa!")

def main() -> None:
    # Thay thế 'YOUR_BOT_TOKEN' bằng token thực của bạn
    application = Application.builder().token("7584357268:AAFZ2vcCuL1KvVB6XW-TTb6vTlaWX7usoeE").build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("activate", activate_key))
    application.add_handler(CommandHandler("premium", premium_command))

    # Button handlers
    application.add_handler(CallbackQueryHandler(button_click))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()