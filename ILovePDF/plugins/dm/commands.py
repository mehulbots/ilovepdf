# This module is part of https://github.com/nabilanavab/ilovepdf
# Feel free to use and contribute to this project. Your contributions are welcome!
# copyright ©️ 2021 nabilanavab

file_name = "ILovePDF/plugins/dm/commands.py"

from pdf import PDF
from plugins import *
from plugins.utils import *
from configs.db import myID
from configs.beta import BETA
from configs.db import dataBASE
from configs.config import dm, settings

if dataBASE.MONGODB_URI:
    from database import db


# ❌ CANCELS CURRENT PDF TO IMAGES WORK ❌
@ILovePDF.on_message((filters.private | filters.group) & filters.command(["cancel"]) & filters.incoming)
async def cancelP2I(bot, message):
    try:
        await work.work(message, "delete", True)
        return await message.delete()
    except Exception:
        pass


# ❌ DELETS CURRENT IMAGES TO PDF QUEUE (/delete) ❌
@ILovePDF.on_message((filters.private | filters.group) & filters.command(["delete"]) & filters.incoming)
async def _cancelI2P(bot, message):
    try:
        lang_code = await util.getLang(message.chat.id)
        await message.reply_chat_action(enums.ChatAction.TYPING)
        del PDF[message.chat.id]
        trans_txt, trans_btn = await util.translate(
            text="GENERATE['deleteQueue']", lang_code=lang_code
        )
        await message.reply_text(trans_txt, quote=True)
        shutil.rmtree(f"work/{message.chat.id}")
    except Exception:
        trans_txt, trans_btn = await util.translate(
            text="GENERATE['noQueue']", lang_code=lang_code
        )
        await message.reply_text(trans_txt, quote=True)


# ❌ BETA USER (/beta) ❌
@ILovePDF.on_message(filters.private & filters.command(["beta"]) & filters.incoming)
async def _betaMode(bot, message):
    try:
        lang_code = await util.getLang(message.from_user.id)
        CHUNK, _ = await util.translate(text="BETA", lang_code=lang_code)

        if message.chat.id in dm.ADMINS:
            logger.debug(f"Beta Users:\n\n{BETA}\n\n")

        if not dataBASE.MONGODB_URI:
            return await message.reply_text(CHUNK["cant"], quote=True)

        if (not message.chat.id in dm.ADMINS) and settings.REFER_BETA:
            refer_ids = await db.get_key(id=message.chat.id, key="refer")
            if (not refer_ids) or not (len(refer_ids.split("|")) >= 5):
                return await message.reply_text(
                    CHUNK["refer"].format(
                        "0" if not refer_ids else f"`{refer_ids.replace('|', '`, `')}`",
                        f"https://t.me/{myID[0].username}?start=-r{message.from_user.id}",
                    ),
                    quote=True,
                )

        if message.chat.id in dm.ADMINS and len(message.text.split(" ")) == 2:
            await db.set_key(
                id=int(message.text.split(" ")[1]), key="beta", value="True"
            )
            BETA.append(int(message.text.split(" ")[1]))
            return await message.reply_text("Now He is a beta user", quote=True)

        if message.chat.id not in BETA:
            await db.set_key(id=message.chat.id, key="beta", value="True")
            BETA.append(message.chat.id)
            return await message.reply_text(CHUNK["nowbeta"], quote=True)
        else:
            await db.dlt_key(id=message.chat.id, key="banned")
            BETA.remove(message.chat.id)
            return await message.reply_text(CHUNK["nownotbeta"], quote=True)
    except Exception as Error:
        logger.exception("🐞 %s : %s" % (file_name, Error))

# If you have any questions or suggestions, please feel free to reach out.
# Together, we can make this project even better, Happy coding!  XD
