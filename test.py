"""
Tests connection to telegram via TelegramBotAPI
"""

import main as m

dev_chat_id = 449951283

if __name__ == "__main__":
    bot = m.NewsTeleBot(m.T_KEY)
    bot.send_message(str(dev_chat_id), "Test succesfull")
    print("Test finished without exception.")