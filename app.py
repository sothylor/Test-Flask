import asyncio
import hypercorn
from quart import Quart, request, render_template, redirect, url_for
from pyrogram import Client, errors
from pyrogram.types import User
import myapi
import database


api_id = myapi.telegram_app_id
api_hash = myapi.telegram_app_api_hash

app = Quart(__name__)
client = Client('my_bot', api_id, api_hash, bot_token=myapi.Token)

@app.route('/')
async def home():
    chatid = 'omsovannrith'
    user = await client.get_users(chatid)
    chatid = user.id
    if database.find_one(chatid):
        return render_template('thanks.html')
    return redirect(f'/addcontact?chatid={chatid}')

@app.route('/addcontact')
async def addcontact():
    chatid = request.args.get('chatid')
    return await render_template('addcontact.html', chatid=chatid)

@app.route('/verify')
async def verify():
    chatid = request.args.get('chatid')
    try:
        await client.add_contact(chatid, "usernameanonymous")
        member = await client.get_users(chatid)
        if isinstance(member, User) and member.is_mutual_contact:
            member_data = member
            name = ""
            if(member_data.username):
                name = member_data.username
            elif(member_data.first_name):
                name = member_data.first_name
            elif(member_data.last_name):
                name = member_data.last_name
            else:
                name = "null"
            return await render_template('verify.html', chatid=chatid, name=name)
        else:
            return redirect(f'/addcontact?chatid={chatid}')
    except Exception as e:
        return f"Error: {e}"

@app.route('/form', methods=['GET', 'POST'])
async def form():
    if request.method == 'GET':
        chatid = request.args.get('chatid')
        name = request.args.get('name')
        return await render_template('form.html', chatid=chatid, name=name)
    else:
        form = await request.form
        chatid = form.get('chatid')
        username = form.get('username')
        phone = "+" + form.get('phone')
        email = form.get('email')
        print('yes')
        database.add_user(chatid, username, phone, email)
        return await render_template('thanks.html')

async def main():
    try:
        await client.start()
    except errors.FloodWait as e:
        wait_time = e.value
        print(f"Flood wait error: waiting for {wait_time} seconds before retrying.")
        await asyncio.sleep(wait_time)
        await main()
    except Exception as e:
        print(f"Error in Telegram client: {e}")
        return

    try:
        await app.run_task(host='localhost', port=5000)
    except Exception as e:
        print(f"Error in Quart app: {e}")
        return


app = asyncio.run(main())

if __name__ == '__main__':
    app
