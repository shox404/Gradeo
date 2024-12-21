from loader import bot


async def delete_previous_message(chat_id, message_id):
    if message_id:
        try:
            await bot.delete_message(chat_id, message_id)
        except Exception as e:
            print(f"❌ Failed to delete message with ID {message_id}: {e}")
