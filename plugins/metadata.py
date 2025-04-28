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

def generate_keyboard(bool_metadata, bool_queue):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                'Queue ON' if bool_queue else 'Queue OFF',
                callback_data=f'queue_{"1" if bool_queue else "0"}'
            ),
            InlineKeyboardButton(
                '✅' if bool_queue else '❌',
                callback_data=f'queue_{"1" if bool_queue else "0"}'
            )
        ],
        [
            InlineKeyboardButton(
                'ᴍᴇᴛᴀᴅᴀᴛᴀ ᴏɴ' if bool_metadata else 'ᴍᴇᴛᴀᴅᴀᴛᴀ ᴏғғ',
                callback_data=f'metadata_{"1" if bool_metadata else "0"}'
            ),
            InlineKeyboardButton(
                '✅' if bool_metadata else '❌',
                callback_data=f'metadata_{"1" if bool_metadata else "0"}'
            )
        ],
        [
            InlineKeyboardButton('Sᴇᴛ Cᴜsᴛᴏᴍ Mᴇᴛᴀᴅᴀᴛᴀ', callback_data='custom_metadata')
        ]
    ])


@Client.on_message(filters.private & filters.command("metadata"))
async def handle_metadata(bot: Client, message: Message):
    ms = await message.reply_text("**Wait A Second...**", reply_to_message_id=message.id)

    bool_metadata = await codeflixbots.get_metadata(message.from_user.id)
    bool_queue = await codeflixbots.get_queue(message.from_user.id)
    user_metadata = await codeflixbots.get_metadata_code(message.from_user.id)

    await ms.delete()

    await message.reply_text(
        f"<b>Metadata Feature : {'✅' if bool_metadata else '❌'} \n\n Queue Feature : {'✅' if bool_queue else '❌'} \n ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ:</b>\n➜ `{user_metadata}",
        reply_markup=generate_keyboard(bool_metadata, bool_queue),
    )


@Client.on_callback_query(filters.regex(".*?(custom_metadata|metadata|queue).*?"))
async def query_metadata(bot: Client, query: CallbackQuery):
    data = query.data

    # Always fetch the latest states
    bool_metadata = await codeflixbots.get_metadata(query.from_user.id)
    bool_queue = await codeflixbots.get_queue(query.from_user.id)
    user_metadata = await codeflixbots.get_metadata_code(query.from_user.id)

    if data.startswith("metadata_"):
        _bool = data.split("_")[1] == '1'
        await codeflixbots.set_metadata(query.from_user.id, bool_meta=not _bool)
        bool_metadata = not _bool  # update after setting

    elif data.startswith("queue_"):
        _bool = data.split("_")[1] == '1'
        await codeflixbots.set_queue(query.from_user.id, bool_queue=not _bool)
        bool_queue = not _bool  # update after setting

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
                chat_id=query.from_user.id,
                text=metadata_message,
                filters=filters.text,
                timeout=60,
                disable_web_page_preview=True,
            )
        except ListenerTimeout:
            await bot.send_message(
                chat_id=query.from_user.id,
                text="⚠️ Error!!\n\n**Request timed out.**\nRestart by using /metadata",
            )
            return
        
        try:
            ms = await bot.send_message(
                chat_id=query.from_user.id,
                text="**Wait A Second...**",
                reply_to_message_id=metadata.id
            )
            await codeflixbots.set_metadata_code(
                query.from_user.id, metadata_code=metadata.text
            )
            await ms.edit("**Your Metadata Code Set Successfully ✅**")
        except Exception as e:
            await bot.send_message(
                chat_id=query.from_user.id,
                text=f"**Error Occurred:** {str(e)}"
            )
        return  # don't proceed further after custom_metadata

    # Edit the existing message if NOT custom_metadata
    await query.message.edit(
        f"<b>Metadata Feature : {'✅' if bool_metadata else '❌'} \n\n Queue Feature : {'✅' if bool_queue else '❌'} \n ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ:</b>\n➜ `{user_metadata}",
        reply_markup=generate_keyboard(bool_metadata, bool_queue),
    )
