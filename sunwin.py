import json
import random
import time
import os
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler

# Configuration
TOKEN = "7411951054:AAGWlpyFDsvUMAKKnSstjqRT-u3D2lxxX_U"
HISTORY_FILE = "history.json"
LOG_FILE = "lichsu.txt"
RECENT_RESULTS_SIZE = 50
CACHE_EXPIRY = 60

class DiceBot:
    def __init__(self):
        self.recent_results = []
        self.history = {
            "Tài": {"correct": 0, "wrong": 0},
            "Xỉu": {"correct": 0, "wrong": 0},
            "Chẵn": {"correct": 0, "wrong": 0},
            "Lẻ": {"correct": 0, "wrong": 0}
        }
        self.transition_counts = defaultdict(lambda: defaultdict(int))
        self.prediction_cache = {}
        self.load_history()
        self.train_markov_model()

    def load_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r") as f:
                    data = json.load(f)
                    # Ensure recent_results is a list of dictionaries
                    self.recent_results = []
                    for res in data.get("recent_results", []):
                        if isinstance(res, dict):
                            self.recent_results.append(res)
                        else:
                            self.recent_results.append({"result": str(res)})
                    self.recent_results = self.recent_results[-RECENT_RESULTS_SIZE:]
                    self.history = data.get("history", self.history)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.save_history()

    def save_history(self):
        try:
            data = {
                "recent_results": self.recent_results,
                "history": self.history
            }
            with open(HISTORY_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def train_markov_model(self):
        if len(self.recent_results) < 2:
            return

        try:
            for i in range(1, len(self.recent_results)):
                prev = self.recent_results[i-1].get("result", str(self.recent_results[i-1]))
                current = self.recent_results[i].get("result", str(self.recent_results[i]))
                if prev and current:
                    self.transition_counts[prev][current] += 1
        except Exception as e:
            print(f"Error training Markov model: {e}")

    def predict_with_markov(self):
        if not self.recent_results:
            return self.random_prediction()
            
        last_result = self.recent_results[-1].get("result", str(self.recent_results[-1]))
        
        if last_result in self.transition_counts and sum(self.transition_counts[last_result].values()) > 0:
            transitions = self.transition_counts[last_result]
            total = sum(transitions.values())
            probabilities = {k: v/total for k, v in transitions.items()}
            return max(probabilities.items(), key=lambda x: x[1])[0]
        
        return self.random_prediction()

    def random_prediction(self):
        return random.choice(["Tài", "Xỉu", "Chẵn", "Lẻ"])

    def calculate_result(self, dice_values):
        total = sum(dice_values)
        return {
            "Tài": total >= 11,
            "Xỉu": total <= 10,
            "Chẵn": total % 2 == 0,
            "Lẻ": total % 2 != 0
        }, total

    def update_history(self, dice_values):
        result, total = self.calculate_result(dice_values)
        main_result = "Tài" if result["Tài"] else "Xỉu"
        
        self.recent_results.append({
            "result": main_result,
            "dice": dice_values,
            "total": total,
            "timestamp": time.time()
        })
        
        if len(self.recent_results) > RECENT_RESULTS_SIZE:
            self.recent_results.pop(0)
        
        self.train_markov_model()
        self.save_history()
        return result, total

    def get_stats(self):
        stats = []
        for res_type, counts in self.history.items():
            total = counts["correct"] + counts["wrong"]
            accuracy = counts["correct"] / total * 100 if total > 0 else 0
            stats.append(f"{res_type}: {counts['correct']}/{total} ({accuracy:.1f}%)")
        return "\n".join(stats)

bot = DiceBot()

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Dự đoán Tài/Xỉu", callback_data='predict_tx'),
         InlineKeyboardButton("Dự đoán Chẵn/Lẻ", callback_data='predict_cl')],
        [InlineKeyboardButton("Thống kê", callback_data='stats')],
        [InlineKeyboardButton("Lịch sử", callback_data='history')],
        [InlineKeyboardButton("Xóa lịch sử", callback_data='clear')]
    ]
    await update.message.reply_text(
        "🎲 Chào mừng đến với Bot Xúc Xắc! 🎲\nChọn chức năng bạn muốn:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def roll_dice(update: Update, context: CallbackContext):
    dice_values = [random.randint(1, 6) for _ in range(3)]
    result, total = bot.update_history(dice_values)
    await update.message.reply_text(
        f"🎯 Kết quả: {dice_values} (Tổng: {total})\n"
        f"📊 Tài/Xỉu: {'Tài' if result['Tài'] else 'Xỉu'}\n"
        f"🔢 Chẵn/Lẻ: {'Chẵn' if result['Chẵn'] else 'Lẻ'}"
    )

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'predict_tx':
        prediction = bot.predict_with_markov()
        while prediction not in ["Tài", "Xỉu"]:
            prediction = bot.predict_with_markov()
        await query.edit_message_text(text=f"🔮 Dự đoán Tài/Xỉu: {prediction}")
    elif query.data == 'predict_cl':
        prediction = bot.predict_with_markov()
        while prediction not in ["Chẵn", "Lẻ"]:
            prediction = bot.predict_with_markov()
        await query.edit_message_text(text=f"🔮 Dự đoán Chẵn/Lẻ: {prediction}")
    elif query.data == 'stats':
        await query.edit_message_text(text=f"📈 Thống kê:\n{bot.get_stats()}")
    elif query.data == 'clear':
        bot.recent_results = []
        bot.history = {k: {"correct": 0, "wrong": 0} for k in bot.history}
        bot.save_history()
        await query.edit_message_text(text="♻️ Đã xóa lịch sử!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sw", roll_dice))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()