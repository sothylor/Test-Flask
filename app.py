import asyncio
from quart import Quart, request, render_template, redirect, url_for
from pyrogram import Client, errors
from pyrogram.types import User
import myapi
import database
import random
from verification import send_email_verify, send_sms_verify, email_acceptance, sms_acceptance
from cryptography.fernet import Fernet

fernet = Fernet(myapi.key)

api_id = fernet.decrypt(myapi.telegram_app_id).decode()
api_hash = fernet.decrypt(myapi.telegram_app_api_hash).decode()
app = Quart(__name__)
client = Client('my_bot', api_id, api_hash, phone_number="+85569218098")
app.jinja_env.enable_async = True


@app.route('/invite')
async def invite():
  chat_id = request.args.get('chatid')
  chat = await client.get_users(int(chat_id))
  try:
    await client.send_message(chat.id, "Please add me to contact!")
    return redirect("https://t.me/Safialor")
  except:
    return 'Errors Occur, Please try again later'


@app.route('/')
async def home():
  chat = request.args.get('chatid')
  try:
    chatid = int(chat)
  except:
    chatid = chat
  try:
    user = await client.get_users(chatid)
  except:
    return 'Invalid User'
  is_duplicate = database.find_one(str(user.id))
  print(is_duplicate)
  if is_duplicate:
    return redirect(url_for('thanks', chatid=user.id))
  return redirect(url_for('addcontact', chatid=user.id))


@app.route('/addcontact')
async def addcontact():
  chat = request.args.get('chatid')
  try:
    chatid = int(chat)
  except:
    chatid = chat
  try:
    user = await client.get_users(chatid)
  except:
    return 'Invalid User'
  chatid = user.id
  return await render_template('addcontact.html', chatid=chatid)


@app.route('/verify')
async def verify():
  chatid = int(request.args.get('chatid'))
  group_id = "@giveawayfortesting"
  group = await client.get_chat(group_id)
  member = await client.get_users(chatid)
  try:
    await client.add_contact(member.id, "usernameanonymous")
    if isinstance(member, User) and member.is_mutual_contact:
      await client.add_chat_members(group.id, member.id)
      await client.send_message(
        member.id,
        "Thanks you! Now you have added to my channel\nhttps://t.me/+zgn2tXV5TXU5NGI9"
      )
      return await render_template('verify.html', chatid=chatid)
    else:
      return redirect(url_for('addcontact', chatid=chatid))
  except errors.UserPrivacyRestricted:
    await client.send_message(
      member.id, f"Thanks you, Please Join my channel\n{group.invite_link}")
    return redirect(url_for('channel', chatid=member.id, groupid=group.id))
  except Exception as e:
    return f"Error: {e}"


@app.route('/channelverify')
async def channelverify():
  chatid = int(request.args.get('chatid'))
  groupid = int(request.args.get('groupid'))
  try:
    member = await client.get_chat_member(groupid, chatid)
    return await render_template('verify.html', chatid=chatid)
  except:
    return redirect(url_for('channel', chatid=chatid, groupid=groupid))


@app.route('/channel')
async def channel():
  chatid = int(request.args.get('chatid'))
  groupid = int(request.args.get('groupid'))
  return await render_template('channel.html', chatid=chatid, groupid=groupid)


@app.route('/form', methods=['GET', 'POST'])
async def form():
  if request.method == 'GET':
    chatid = int(request.args.get('chatid'))
    member_data = await client.get_users(chatid)
    name = ""
    if (member_data.username):
      name = member_data.username
    elif (member_data.first_name):
      name = member_data.first_name
    elif (member_data.last_name):
      name = member_data.last_name
    return await render_template('form.html', chatid=member_data.id, name=name)
  else:
    global forms
    forms = await request.form
    return redirect(url_for('verify_phone_email', resend=""))


@app.route("/verify-phone-email", methods=['GET', 'POST'])
async def verify_phone_email():
  global forms, code, email_send, phone_send
  resend = request.args.get('resend')
  chatid = forms.get('chatid')
  username = forms.get('username')
  phone = "+" + forms.get('phone')
  email = forms.get('email')
  if request.method == 'GET':
    email = forms.get('email')
    phone = "+" + forms.get('phone')
    email_send = phone_send = False
    if resend == 'email':
      code = str(random.randint(1000, 9999))
      email_send = await send_email_verify(email, code)
      phone_send = True
    elif resend == 'phone':
      phone_send = await send_sms_verify(phone)
      email_send = True
    else:
      code = str(random.randint(1000, 9999))
      email_send = await send_email_verify(email, code)
      phone_send = await send_sms_verify(phone)
    if not email_send or not phone_send:
      return await render_template('wrong-information.html', chatid=chatid)
    return await render_template('verification.html')
  else:
    form_code = await request.form
    phone_code = form_code.get('phone')
    email_code = form_code.get('email')
    phone_verify = await sms_acceptance(phone, phone_code)
    email_verify = await email_acceptance(code, email_code)
    if not email_verify and not phone_verify:
      status = 'both_error'
      return await render_template('verification.html', status=status)
    elif not email_verify:
      status = 'email_error'
      return await render_template('verification.html', status=status)
    elif not phone_verify:
      status = 'phone_error'
      return await render_template('verification.html', status=status)
    else:
      database.add_user(chatid, username, phone, email)
      return redirect('/thanks')


@app.route('/thanks')
async def thanks():
  return await render_template('thanks.html')


async def main():
  await client.start()
  await app.run_task(host='0.0.0.0', port=5000)


app = asyncio.run(main())

if __name__ == '__main__':
  app
