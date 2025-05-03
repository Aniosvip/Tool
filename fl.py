import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot("7411904806:AAFlcNOPb0bKAg8-DVp-SNZq5cdLPvmJCeI")

# Lệnh /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Hướng dẫn sử dụng", callback_data="guide"))
    bot.send_message(message.chat.id,
        "Chào mừng bạn đến với bot tra cứu thông tin!\n\n"
        "Bạn có thể dùng lệnh:\n"
        "/fl <username> để tra cứu người dùng.",
        reply_markup=markup
    )

# Lệnh /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = (
        "Hướng dẫn sử dụng bot:\n\n"
        "• /start - Bắt đầu bot\n"
        "• /help - Hiển thị hướng dẫn\n"
        "• /fl <username> - Tra cứu thông tin người dùng\n\n"
        "Ví dụ: `/fl annek26th11`\n\n"
        "Bot sẽ trả về thông tin chi tiết về tài khoản."
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# Callback cho nút "Hướng dẫn sử dụng"
@bot.callback_query_handler(func=lambda call: call.data == "guide")
def handle_guide(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id,
        "Ví dụ cách dùng:\n/fl annek26th11\n\n"
        "Bot sẽ trả về thông tin chi tiết của tài khoản."
    )

# Lệnh /fl
@bot.message_handler(commands=['fl'])
def handle_fl_command(message):
    try:
        username = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Vui lòng nhập username. Ví dụ: /fl annek26th11")
        return

    bot.reply_to(message, "Đang xử lý, vui lòng đợi một chút...")

    api_url = f"https://ksjdjdmfmxm.x10.mx/api/fl.php?user={username}&key=4I1TK-YXQZ4-GNFPL8&info=true"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        bot.reply_to(message, "Lỗi: Hết thời gian chờ phản hồi từ API.")
        return
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Lỗi kết nối API: {e}")
        return
    except ValueError:
        bot.reply_to(message, "Lỗi phân tích dữ liệu JSON từ API.")
        return

    if data.get('status', False):
        status_text = "✅ Thành công"
    else:
        status_text = "❌ Thất bại"

    reply_text = (
        f"🏖️ Khu Vực: {data.get('khu_vuc', 'N/A')}\n"
        f"👤 Tên: {data.get('name', 'N/A')}\n"
        f"🆔 User ID: {data.get('user_id', 'N/A')}\n"
        f"📸 Avatar: {data.get('avatar', 'N/A')}\n"
        f"📅 Ngày tạo: {data.get('create_time', 'N/A')}\n"
        f"📌 Username: @{data.get('username', 'N/A')}\n"
        f"👥 Followers (Trước): {data.get('followers_before', 0)}\n"
        f"👥 Followers (Sau): {data.get('followers_after', 0)}\n"
        f"✨ Đã thêm: {data.get('followers_add', 0)}\n"
        f"💬 Thông báo: {data.get('message', '')}\n"
        f"🔍 Trạng thái: {status_text}"
    )

    bot.reply_to(message, reply_text)

    # Gửi ảnh đại diện nếu có
    avatar_url = data.get('avatar')
    if avatar_url and avatar_url.startswith("http"):
        try:
            bot.send_photo(message.chat.id, avatar_url, caption="Ảnh đại diện của người dùng")
        except:
            pass
        # Ghi lại lệnh vào file để bot B xử lý
        with open("fl_pending.txt", "a") as f:
            f.write(f"{message.chat.id}|/fl {username}\n")
if __name__ == "__main__":
    bot.polling()