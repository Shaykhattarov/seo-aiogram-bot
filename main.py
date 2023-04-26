from app import dp, executor


if __name__ == "__main__":
    print('[INFO] Бот начал свою работу!')
    executor.start_polling(dp, skip_updates=True)