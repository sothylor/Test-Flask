import random
import smtplib
from cryptography.fernet import Fernet
import myapi
import requests
import asyncio

fernet = Fernet(myapi.key)
sender_email = fernet.decrypt(myapi.sender_email).decode()
sender_password = fernet.decrypt(myapi.sender_password).decode()
access_token = fernet.decrypt(myapi.access_token).decode()


async def send_email_verify(email,
                            verification_code,
                            sender_email=sender_email,
                            sender_password=sender_password):
  smtp_server = "smtp.gmail.com"
  smtp_port = 587
  try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    subject = f"{verification_code}"
    body = f"Your verification code is <b style='font-size: 15px;'>{verification_code}</b>"
    message = f"Subject: {subject}\nContent-type: text/html\n\n{body}"

    server.sendmail(sender_email, email, message)
    server.quit()

    return True
  except:
    return False


async def email_acceptance(verify_code, input_code):
  return verify_code == input_code


import aiohttp


async def send_sms_verify(phone_number, access_token=access_token):
  data = {
    'To': phone_number,
    'Channel': 'sms',
  }

  async with aiohttp.ClientSession() as session:
    async with session.post(
        'https://verify.twilio.com/v2/Services/VAa0dc9f4948e364b535fba416cd767395/Verifications',
        data=data,
        auth=aiohttp.BasicAuth('ACc6b947a7035e567af23ad1215204e89f',
                               access_token),
    ) as response:
      status = (await response.json())["status"]
      return status == "pending"


async def sms_acceptance(phone_number, otp_code, access_token=access_token):
  data = {
    'To': phone_number,
    'Code': otp_code,
  }

  async with aiohttp.ClientSession() as session:
    async with session.post(
        'https://verify.twilio.com/v2/Services/VAa0dc9f4948e364b535fba416cd767395/VerificationCheck',
        data=data,
        auth=aiohttp.BasicAuth('ACc6b947a7035e567af23ad1215204e89f',
                               access_token),
    ) as response:
      status = (await response.json())["status"]
      return status == "approved"

