from pyrogram import Client
import myapi

api_id = myapi.telegram_app_id
api_hash = myapi.telegram_app_api_hash

client = Client('my_bot', api_id, api_hash, phone_number="+85569218098")
client.run()
client.add_chat_members("+zgn2tXV5TXU5NGI9", "1022230710")