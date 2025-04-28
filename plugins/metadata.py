from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from helper.database import codeflixbots
from pyromod.exceptions import ListenerTimeout
from config import Txt, Config
from plugins.file_rename import queue

# AUTH_USERS = Config.AUTH_USERS

ON = [[InlineKeyboardButton('ᴍᴇᴛᴀᴅᴀᴛᴀ ᴏɴ', callback_data='metadata_1'),
       InlineKeyboardButton('✅', callback_data='metadata_1')],
      [InlineKeyboardButton('Sᴇᴛ Cᴜsᴛᴏᴍ Mᴇᴛᴀᴅᴀᴛᴀ', callback_data='custom_metadata')]]

OFF = [[InlineKeyboardButton('ᴍᴇᴛᴀᴅᴀᴛᴀ ᴏғғ', callback_data='metadata_0'),
        InlineKeyboardButton('❌', callback_data='metadata_0')],
       [InlineKeyboardButton('Sᴇᴛ Cᴜsᴛᴏᴍ Mᴇᴛᴀᴅᴀᴛᴀ', callback_data='custom_metadata')]]


@Client.on_message(filters.private & filters.command("metadata"))
async def handle_metadata(bot: Client, message: Message):
    ms = await message.reply_text("**Wait A Second...**", reply_to_message_id=message.id)
    bool_metadata = await codeflixbots.get_metadata(message.from_user.id)
    user_metadata = await codeflixbots.get_metadata_code(message.from_user.id)
    await ms.delete()
    
    if bool_metadata:
        await message.reply_text(
            f"<b>ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ:</b>\n\n➜ `{user_metadata}` ",
            reply_markup=InlineKeyboardMarkup(ON),
        )
    else:
        await message.reply_text(
            f"<b>ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ:</b>\n\n➜ `{user_metadata}` ",
            reply_markup=InlineKeyboardMarkup(OFF),
        )


@Client.on_message(filters.private & filters.command("clear_queue"))
async def clear_queue(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if the user has a queue
    if user_id in queue and queue[user_id]["messages"]:
        # Clear the queue
        queue[user_id]["messages"].clear()
        queue[user_id]["queue_size"] = 0
        await message.reply_text("✅ Your queue has been cleared successfully!")
    else:
        await message.reply_text("⚠️ Your queue is already empty.")

@Client.on_message(filters.private & filters.command("clear"))
async def clear_queue(client: Client, message: Message):
    user_id = message.from_user.id
    index=message.text.split(" ")[1]
    if user_id in queue and queue[user_id]["messages"]:
        if len(queue[user_id]["messages"]) >= 1:
            queue[user_id]["message"].pop(index)
            await message.reply_text(" in queue position -{index} has been Cleared✅")
    else:
        await message.reply_text("⚠️ Your queue is already empty.")

@Client.on_callback_query(filters.regex(".*?(custom_metadata|metadata).*?"))
async def query_metadata(bot: Client, query: CallbackQuery):
    data = query.data

    if data.startswith("metadata_"):
        _bool = data.split("_")[1] == '1'
        user_metadata = await codeflixbots.get_metadata_code(query.from_user.id)

        if _bool:
            await codeflixbots.set_metadata(query.from_user.id, bool_meta=False)
            await query.message.edit(
                f"<b>ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ:</b>\n\n➜ `{user_metadata}` ",
                reply_markup=InlineKeyboardMarkup(OFF),
            )
        else:
            await codeflixbots.set_metadata(query.from_user.id, bool_meta=True)
            await query.message.edit(
                f"<b>ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ:</b>\n\n➜ `{user_metadata}` ",
                reply_markup=InlineKeyboardMarkup(ON),
            )

    elif data == "custom_metadata":
        await query.message.delete()
        try:
            user_metadata = await codeflixbots.get_metadata_code(query.from_user.id)
            metadata_message = f"""
<b>--Metadata Settings:--</b>

➜ <b>ᴄᴜʀʀᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ:</b> `{user_metadata}`

<b>Description</b> : Metadata will change MKV video files including all audio, streams, and subtitle titles.

<b>➲ Send metadata title. Timeout: 60 sec</b>
"""

            metadata = await bot.ask(
                text=metadata_message,
                chat_id=query.from_user.id,
                filters=filters.text,
                timeout=60,
                disable_web_page_preview=True,
            )
        except ListenerTimeout:
            await query.message.reply_text(
                "⚠️ Error!!\n\n**Request timed out.**\nRestart by using /metadata",
                reply_to_message_id=query.message.id,
            )
            return
        
        try:
            ms = await query.message.reply_text(
                "**Wait A Second...**", reply_to_message_id=metadata.id
            )
            await codeflixbots.set_metadata_code(
                query.from_user.id, metadata_code=metadata.text
            )
            await ms.edit("**Your Metadata Code Set Successfully ✅**")
        except Exception as e:
            await query.message.reply_text(f"**Error Occurred:** {str(e)}")
