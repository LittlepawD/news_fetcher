import main as m

dev_chat_id = 449951283

if __name__ == "__main__":
    bot = m.NewsTeleBot(m.N_KEY)
    bot.send_message(dev_chat_id, "Test succesfull")
    print("Test finished without exception.")