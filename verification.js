const random = require('random');
const smtplib = require('smtplib');
const Fernet = require('cryptography').Fernet;
const myapi = require('./myapi');
const requests = require('requests');

const fernet = new Fernet(myapi.key);
const sinch_api_key = fernet.decrypt(myapi.sinch_api_key).toString();
const sinch_secret_key = fernet.decrypt(myapi.sinch_secret_key).toString();
const sender_email = fernet.decrypt(myapi.sender_email).toString();
const sender_password = fernet.decrypt(myapi.sender_password).toString();
const access_token = fernet.decrypt(myapi.access_token).toString().trim();

async function send_email_verification_code(email, sender_email = sender_email, sender_password = sender_password) {
  const verification_code = String(random.int(1000, 9999));

  const smtp_server = "smtp.gmail.com";
  const smtp_port = 587;
  console.log(sender_email);
  console.log(sender_password);
  const server = smtplib.SMTP(smtp_server, smtp_port);
  server.starttls();
  server.login(sender_email, sender_password);

  const subject = verification_code;
  const body = `Your verification code is <b style='font-size: 15px;'>${verification_code}</b>`;
  const message = `Subject: ${subject}\nContent-type: text/html\n\n${body}`;

  server.sendmail(sender_email, email, message);
  server.quit();

  return verification_code;
}

async function send_sms_verification_code(phone_number, access_token = access_token) {
  const verification_code = String(random.int(1000, 9999));
  const message = `verification code is : ${verification_code}`;
  const headers = {
    "Authorization": `Bearer ${access_token}`,
    "Content-Type": "application/json"
  };
  const json_data = {
    'from': '447520662179',
    'to': [
      `${phone_number}`,
    ],
    'body': `${message}`,
  };
  requests.post(
    'https://sms.api.sinch.com/xms/v1/de01385b033d436997d96ded332d47dd/batches',
    { headers: headers, json: json_data }
  );
  return verification_code;
}
