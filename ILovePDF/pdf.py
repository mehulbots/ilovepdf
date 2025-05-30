# This module is part of https://github.com/nabilanavab/ilovepdf
# Feel free to use and contribute to this project. Your contributions are welcome!
# copyright ©️ 2021 nabilanavab


file_name = "ILovePDF/pdf.py"

from configs.config import bot
from telebot import async_telebot
import asyncio 


# GLOBAL VARIABLES
PDF = {}  # save images for generating pdf
works = {"u": [], "g": []}  # broken works

pyTgLovePDF = async_telebot.AsyncTeleBot(bot.API_TOKEN, parse_mode="Markdown")
# TELEBOT (pyTelegramBotAPI) Asyncio [for uploading group doc, imgs]

# ILovePDF/pdf.py

from configs.config import bot
from telebot import async_telebot
import asyncio

# GLOBAL VARIABLES
PDF = {}  # save images for generating pdf
works = {"u": [], "g": []}  # broken works

# Async Telebot initialization
pyTgLovePDF = async_telebot.AsyncTeleBot(bot.API_TOKEN, parse_mode="Markdown")

# ---- polling STARTS HERE ----
async def start_polling():
    print("Starting async polling...")
    await pyTgLovePDF.polling()
    print("STARTED POLLING")

def main():
    asyncio.run(start_polling())

    print("RUNNED")

if __name__ == "__main__":
    main()
    print("RUNNING..")

# If you have any questions or suggestions, please feel free to reach out.
# Together, we can make this project even better, Happy coding!  XD

# file_name = "ILovePDF/pdf.py"

# from configs.config import bot
# from telebot import async_telebot
# import asyncio 

# # GLOBAL VARIABLES
# PDF = {}  # save images for generating pdf
# works = {"u": [], "g": []}  # broken works

# # Create bot instance
# pyTgLovePDF = async_telebot.AsyncTeleBot(bot.API_TOKEN, parse_mode="Markdown")

# # Async polling wrapped in an async main function
# async def main():
#     await pyTgLovePDF.polling()

# # Only run polling if this file is executed directly
# if __name__ == "__main__":
#     asyncio.run(main())
