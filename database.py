import json

USERS_FILE = 'users.json'

def users_io(operation, user_data=None):
    with open(USERS_FILE, 'r+') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = []

        if operation == 'add':
            users.append({user_data['chatid']: user_data})
        elif operation == 'update':
            users = [{u['chatid']: user_data} if u['chatid'] == user_data['chatid'] else u for u in users]
        elif operation == 'delete':
            users = [u for u in users if u['chatid'] != user_data['chatid']]
        elif operation == 'find':
            return [u for u in users if u['chatid'] == user_data['chatid']]
        
        f.seek(0)
        json.dump(users, f)
        f.truncate()

def add_user(chatid, username, phone, email):
    user_data = {
        'chatid': chatid,
        'data': [username, phone, email]
    }
    users_io('add', user_data)

def update_user(chatid, username, phone, email):
    user_data = {
        'chatid': chatid,
        'data': [username, phone, email]
    }
    users_io('update', user_data)

def delete_user(chatid):
    user_data = {'chatid': chatid}
    users_io('delete', user_data)

def find_one(chatid):
    user_data = {'chatid': chatid}
    return users_io('find', user_data)





# object oriented operations
class User:
    def __init__(self, chatid, username, phone, email):
        self.chatid = chatid
        self.data = [username, phone, email]

    def to_dict(self):
        return {'chatid': self.chatid, 'data': self.data}

class UserManager:
    def __init__(self, filename):
        self.filename = filename

    def _read_users(self):
        with open(self.filename, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = []
        return users

    def _write_users(self, users):
        with open(self.filename, 'w') as f:
            json.dump(users, f)

    def add_user(self, chatid, username, phone, email):
        user = User(chatid, username, phone, email)
        users = self._read_users()
        users.append(user.to_dict())
        self._write_users(users)

    def update_user(self, chatid, username, phone, email):
        users = self._read_users()
        for i, user in enumerate(users):
            if user['chatid'] == chatid:
                users[i] = User(chatid, username, phone, email).to_dict()
        self._write_users(users)

    def delete_user(self, chatid):
        users = self._read_users()
        users = [user for user in users if user['chatid'] != chatid]
        self._write_users(users)