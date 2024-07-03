import uuid
import logging
from queue import Queue

class Chat:
    def __init__(self):
        self.sessions = {}
        self.users = {
            'messi': {
                'nama': 'Lionel Messi',
                'negara': 'Argentina',
                'password': 'surabaya',
                'incoming': {},
                'outgoing': {}
            },
            'henderson': {
                'nama': 'Jordan Henderson',
                'negara': 'Inggris',
                'password': 'surabaya',
                'incoming': {},
                'outgoing': {}
            },
            'lineker': {
                'nama': 'Gary Lineker',
                'negara': 'Inggris',
                'password': 'surabaya',
                'incoming': {},
                'outgoing': {}
            }
        }
        self.groups = {}

    def proses(self, data):
        j = data.split(" ")
        try:
            command = j[0].strip()
            if command == 'auth':
                username = j[1].strip()
                password = j[2].strip()
                logging.warning("AUTH: auth {} {}".format(username, password))
                return self.autentikasi_user(username, password)
            elif command == 'send':
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                message = " ".join(j[3:])
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("SEND: session {} send message from {} to {}".format(sessionid, usernamefrom, usernameto))
                return self.send_message(sessionid, usernamefrom, usernameto, message)
            elif command == 'inbox':
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                logging.warning("INBOX: {}".format(sessionid))
                return self.get_inbox(username)
            elif command == 'create_group':
                sessionid = j[1].strip()
                groupname = j[2].strip()
                return self.create_group(sessionid, groupname)
            elif command == 'join_group':
                sessionid = j[1].strip()
                groupname = j[2].strip()
                return self.join_group(sessionid, groupname)
            elif command == 'send_group':
                sessionid = j[1].strip()
                groupname = j[2].strip()
                message = " ".join(j[3:])
                usernamefrom = self.sessions[sessionid]['username']
                return self.send_group_message(sessionid, usernamefrom, groupname, message)
            elif command == 'group_inbox':
                sessionid = j[1].strip()
                groupname = j[2].strip()
                return self.get_group_inbox(sessionid, groupname)
            else:
                return {'status': 'ERROR', 'message': 'Protocol Tidak Benar'}
        except KeyError:
            return {'status': 'ERROR', 'message': 'Informasi tidak ditemukan'}
        except IndexError:
            return {'status': 'ERROR', 'message': 'Protocol Tidak Benar'}

    def autentikasi_user(self, username, password):
        if username not in self.users:
            return {'status': 'ERROR', 'message': 'User Tidak Ada'}
        if self.users[username]['password'] != password:
            return {'status': 'ERROR', 'message': 'Password Salah'}
        tokenid = str(uuid.uuid4())
        self.sessions[tokenid] = {'username': username, 'userdetail': self.users[username]}
        return {'status': 'OK', 'tokenid': tokenid}

    def get_user(self, username):
        return self.users.get(username, False)

    def send_message(self, sessionid, username_from, username_dest, message):
        if sessionid not in self.sessions:
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)
        
        if not s_fr or not s_to:
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

        message = {'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message}
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        
        if username_from not in outqueue_sender:
            outqueue_sender[username_from] = Queue()
        outqueue_sender[username_from].put(message)

        if username_from not in inqueue_receiver:
            inqueue_receiver[username_from] = Queue()
        inqueue_receiver[username_from].put(message)

        return {'status': 'OK', 'message': 'Pesan terkirim'}

    def get_inbox(self, username):
        s_fr = self.get_user(username)
        incoming = s_fr['incoming']
        msgs = {users: [] for users in incoming}
        
        for user in incoming:
            msgs[user] = list(incoming[user].queue)

        return {'status': 'OK', 'messages': msgs}

    def create_group(self, sessionid, groupname):
        username = self.sessions[sessionid]['username']
        if groupname in self.groups:
            return {'status': 'ERROR', 'message': 'Grup sudah ada'}
        self.groups[groupname] = {'members': [username], 'messages': Queue()}
        return {'status': 'OK', 'message': 'Grup berhasil dibuat'}

    def join_group(self, sessionid, groupname):
        username = self.sessions[sessionid]['username']
        if groupname not in self.groups:
            return {'status': 'ERROR', 'message': 'Grup tidak ditemukan'}
        if username in self.groups[groupname]['members']:
            return {'status': 'ERROR', 'message': 'Sudah menjadi member grup'}
        self.groups[groupname]['members'].append(username)
        return {'status': 'OK', 'message': 'Berhasil join grup'}

    def send_group_message(self, sessionid, username_from, groupname, message):
        if groupname not in self.groups:
            return {'status': 'ERROR', 'message': 'Grup tidak ditemukan'}
        if username_from not in self.groups[groupname]['members']:
            return {'status': 'ERROR', 'message': 'Bukan seorang member dari grup'}
        group_message = {'msg_from': username_from, 'msg': message}
        self.groups[groupname]['messages'].put(group_message)
        return {'status': 'OK', 'message': 'Pesan grup terkirim'}

    def get_group_inbox(self, sessionid, groupname):
        username = self.sessions[sessionid]['username']
        if groupname not in self.groups:
            return {'status': 'ERROR', 'message': 'Grup tidak ditemukan'}
        if username not in self.groups[groupname]['members']:
            return {'status': 'ERROR', 'message': 'Bukan seorang member dari grup'}
        messages = list(self.groups[groupname]['messages'].queue)
        return {'status': 'OK', 'messages': messages}

if __name__=="__main__":
	j = Chat()
	sesi = j.proses("auth messi surabaya")
	print(sesi)
	#sesi = j.autentikasi_user('messi','surabaya')
	#print sesi
	tokenid = sesi['tokenid']
	print(j.proses("send {} henderson hello gimana kabarnya son " . format(tokenid)))
	print(j.proses("send {} messi hello gimana kabarnya mess " . format(tokenid)))

	#print j.send_message(tokenid,'messi','henderson','hello son')
	#print j.send_message(tokenid,'henderson','messi','hello si')
	#print j.send_message(tokenid,'lineker','messi','hello si dari lineker')

	print("isi mailbox dari messi")
	print(j.get_inbox('messi'))
	print("isi mailbox dari henderson")
	print(j.get_inbox('henderson'))
