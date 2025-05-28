# This module is part of https://github.com/nabilanavab/ilovepdf
# Feel free to use and contribute to this project. Your contributions are welcome!
# copyright ©️ 2021 nabilanavab

file_name = "ILovePDF/plugins/dm/document.py"

import fitz
import convertapi
from pdf import PDF
from plugins import *
from PIL import Image
from ..utils import *
from configs import *
from .photo import HD
from configs import beta

try:
    import aspose.words as word

    wordSupport = True
except Exception:
    wordSupport = False

#  MAXIMUM FILE SIZE (IF IN config var.)
if config.settings.MAX_FILE_SIZE:
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE"))
    MAX_FILE_SIZE_IN_kiB = int(config.settings.MAX_FILE_SIZE) * (10**6)
else:
    MAX_FILE_SIZE = False

#  FILES TO PDF [SUPPORTED CODECS]
img2pdf = [
    ".jpg",
    ".png",
    ".jpeg"
]  # Img to pdf file support

pymu2PDF = [
    ".xps",
    ".cbz",
    ".fb2",
    ".epub",
    ".oxps"
]  # files to pdf (zero limits)

wordFiles = [
    ".ps",
    ".md",
    ".dot",
    ".bmp",
    ".gif",
    ".pcl",
    ".xps",
    ".svg",
    ".txt",
    ".chm",
    ".emf",
    ".mobi",
    ".tiff",
    ".dotx",
    ".dotm",
    ".html",
    ".mhtml",
    ".flatOpc",
]

cnvrt_api_2PDF = [
    ".csv",
    ".log",
    ".mpp",
    ".xml",
    ".doc",
    ".mpt",
    ".odt",
    ".pot",
    ".pps",
    ".ppt",
    ".pub",
    ".rtf",
    ".txt",
    ".vdx",
    ".vsd",
    ".vst",
    ".wpd",
    ".wps",
    ".wri",
    ".xlt",
    ".xls",
    ".ppsx",
    ".pptx",
    ".xlsb",
    ".xlsx",
    ".docx",
    ".xltx",
    ".potx",
    ".vsdx",
    ".vstx",
]  # file to pdf (ConvertAPI limit)

#  PYMUPDF FILES TO PDF 
async def pymuConvert2PDF(cDIR, edit, input_file, lang_code):
    try:
        with fitz.open(input_file) as doc:
            with fitz.open("pdf", doc.convert_to_pdf()) as pdf:
                pdf.save(
                    f"{cDIR}/outPut.pdf",
                    garbage=4,
                    deflate=True,
                )
        return True
    except Exception as e:
        tTXT, tBTN = await translate(text="DOCUMENT['error']", lang_code=lang_code)
        await edit.edit(
            text=tTXT.format(e),
            reply_markup=await createBUTTON(btn={"👍": "try+", "👎": "try-"}),
        )
        return False


#  ConvertAPI FILES TO PDF 
async def cvApi2PDF(cDIR, edit, input_file, lang_code, API):
    try:
        convertapi.api_secret = API
        fileNm, fileExt = os.path.splitext(input_file)
        convertapi.convert(
            "pdf",
            {"File": f"{input_file}"},
            from_format=fileExt[1:],
        ).save_files(f"{cDIR}/outPut.pdf")
        return True
    except Exception as e:
        tTXT, tBTN = await translate(text="DOCUMENT['error']", lang_code=lang_code)
        await edit.edit(tTXT.format(e))
        return False


#  WORD FILES TO PDF 
async def word2PDF(cDIR, edit, input_file, lang_code):
    try:
        doc = word.Document(input_file)
        doc.save(f"{cDIR}/outPut.pdf")
        return True
    except Exception as e:
        tTXT, tBTN = await translate(text="DOCUMENT['error']", lang_code=lang_code)
        await edit.edit(tTXT.format(e))
        return False


#  REPLY TO DOC. FILES 
@ILovePDF.on_message(filters.private & filters.incoming & filters.document)
async def documents(bot, message):
    try:
        # refresh causes error ;) so, try
        try:
            await message.reply_chat_action(enums.ChatAction.TYPING)
        except Exception:
            pass
        lang_code = await util.getLang(message.chat.id)
        CHUNK, _ = await util.translate(text="DOCUMENT", lang_code=lang_code)
        if await work.work(message, "check", True):
            tBTN = await util.createBUTTON(
                await util.editDICT(inDir=CHUNK["refresh"], value="refresh")
            )  # sends refresh msg if any
            return await message.reply_text(
                CHUNK["inWork"], reply_markup=tBTN, quote=True
            )  # work exists
        fileNm, fileExt = os.path.splitext(
            message.document.file_name
        )  # seperate name & extension

        # REPLY TO LAGE FILES/DOCUMENTS
        if MAX_FILE_SIZE and message.document.file_size >= int(MAX_FILE_SIZE_IN_kiB):
            tBTN = await util.createBUTTON(CHUNK["bigCB"])
            return await message.reply_photo(
                photo=config.images.BIG_FILE,
                caption=CHUNK["big"].format(MAX_FILE_SIZE, MAX_FILE_SIZE),
                reply_markup=tBTN,
            )
        # REPLY TO .PDF FILE EXTENSION
        elif fileExt.lower() == ".pdf":
            pdfMsgId = await message.reply_text(CHUNK["process"], quote=True)
            await asyncio.sleep(0.5)
            await pdfMsgId.edit(CHUNK["process"] + ".")
            await asyncio.sleep(0.5)
            tBTN = await util.createBUTTON(
                CHUNK["replyCB"] if message.chat.id in beta.BETA else CHUNK["_replyCB"]
            )
            await pdfMsgId.edit(
                text=CHUNK["reply"].format(
                    message.document.file_name,
                    await render.gSF(message.document.file_size),
                ),
                reply_markup=tBTN,
            )
            logFile = message

        # IMAGE AS FILES (ADDS TO PDF FILE)
        elif fileExt.lower() in img2pdf:
            try:
                if message.chat.id in HD:
                    if len(HD[message.chat.id]) >= 16:
                        return
                    HD[message.chat.id].append(message.document.file_id)
                    generateCB = (
                        "document['generate']"
                        if config.settings.DEFAULT_NAME
                        else "document['generateRN']"
                    )
                    tTXT, tBTN = await util.translate(
                        text="document['imageAdded']",
                        button=generateCB,
                        lang_code=lang_code,
                    )
                    return await message.reply_text(
                        tTXT.format(len(HD[message.chat.id]) - 1, message.chat.id)
                        + " [HD] 🔰",
                        reply_markup=tBTN,
                        quote=True,
                    )
                imageDocReply = await message.reply_text(CHUNK["download"], quote=True)
                if not isinstance(PDF.get(message.from_user.id), list):
                    PDF[message.from_user.id] = []
                path = await message.download(
                    f"{message.from_user.id}/{message.id}.jpg"
                )
                img = Image.open(path).convert("RGB")
                PDF[message.from_user.id].append(img)
                generateCB = (
                    "generate" if config.settings.DEFAULT_NAME else "generateRN"
                )
                tBTN = await util.createBUTTON(CHUNK[generateCB])
                await imageDocReply.edit(
                    text=CHUNK["imageAdded"].format(
                        len(PDF[message.from_user.id]), message.from_user.id
                    ),
                    reply_markup=tBTN,
                )
                os.remove(path)
                return
            except Exception as e:
                return await imageDocReply.edit(CHUNK["error"].format(e))

        # FILES TO PDF
        elif (
            (fileExt.lower() in pymu2PDF)
            or (fileExt.lower() in cnvrt_api_2PDF)
            or (fileExt.lower() in wordFiles)
        ):

            if (fileExt.lower() in cnvrt_api_2PDF) and (
                (
                    (
                        not db.DATA.get(message.chat.id, 0)
                        or (
                            db.DATA.get(message.chat.id, 0)
                            and not db.DATA.get(message.chat.id, 0)[0]
                        )
                    )
                    and config.settings.CONVERT_API is False
                )
            ):
                return await message.reply_text(CHUNK["noAPI"], quote=True)

            if (fileExt.lower() in wordFiles) and not wordSupport:
                return await message.reply_text(CHUNK["useDOCKER"], quote=True)

            cDIR = await work.work(message, "create", True)
            tBTN = await util.createBUTTON(CHUNK["cancelCB"])
            pdfMsgId = await message.reply_text(
                CHUNK["download"], reply_markup=tBTN, quote=True
            )
            input_file = f"{cDIR}/input_file{fileExt}"
            # DOWNLOAD PROGRESS
            downloadLoc = await bot.download_media(
                message=message.document.file_id,
                file_name=input_file,
                progress=render.progress,
                progress_args=(message.document.file_size, pdfMsgId, time.time()),
            )
            # CHECKS PDF DOWNLOADED OR NOT
            if os.path.getsize(downloadLoc) != message.document.file_size:
                return await work.work(message, "delete", True)

            await pdfMsgId.edit(CHUNK["takeTime"], reply_markup=tBTN)

            # WHERE REAL CODEC CONVERSATION OCCURS
            if fileExt.lower() in pymu2PDF:
                FILE_NAME, FILE_CAPT, THUMBNAIL = await fncta.thumbName(
                    message, f"{fileNm}.pdf"
                )
                isError = await pymuConvert2PDF(cDIR, pdfMsgId, input_file, lang_code)

            elif fileExt.lower() in cnvrt_api_2PDF:
                FILE_NAME, FILE_CAPT, THUMBNAIL, API = await fncta.thumbName(
                    message, f"{fileNm}.pdf", getAPI=True
                )
                API = API if not (API == False) else config.settings.CONVERT_API
                isError = await cvApi2PDF(cDIR, pdfMsgId, input_file, lang_code, API)

            elif fileExt.lower() in wordFiles:
                FILE_NAME, FILE_CAPT, THUMBNAIL = await fncta.thumbName(
                    message, f"{fileNm}.pdf"
                )
                isError = await word2PDF(cDIR, pdfMsgId, input_file, lang_code)

            if not isError:
                return await work.work(message, "delete", True)

            if config.images.PDF_THUMBNAIL != THUMBNAIL:
                location = await bot.download_media(
                    message=THUMBNAIL, file_name=f"{cDIR}/thumb.jpeg"
                )
                THUMBNAIL = await fncta.formatThumb(location)

            await pdfMsgId.edit(CHUNK["upFile"], reply_markup=tBTN)
            await message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
            logFile = await message.reply_document(
                file_name=FILE_NAME,
                document=open(f"{cDIR}/outPut.pdf", "rb"),
                caption=CHUNK["fromFile"].format(fileExt, "pdf") + f"\n\n{FILE_CAPT}",
                quote=True,
                progress=render._progress,
                progress_args=(pdfMsgId, time.time()),
                thumb=THUMBNAIL,
                reply_markup=await util.createBUTTON(btn={"👍": "try+", "👎": "try-"})
                if fileExt.lower() in pymu2PDF
                else None,
            )
            await pdfMsgId.delete()
            await work.work(message, "delete", True)

        # UNSUPPORTED FILES
        else:
            return await message.reply_text(CHUNK["unsupport"], quote=True)

        await log.log.footer(message, output=logFile, lang_code=lang_code)
    except Exception as e:
        logger.exception("🐞 %s: %s" % (file_name, e), exc_info=True)
        await work.work(message, "delete", True)

# If you have any questions or suggestions, please feel free to reach out.
# Together, we can make this project even better, Happy coding!  XD
