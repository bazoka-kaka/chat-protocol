import socket
import json

# change the below ip with the machine's
TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889

class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP, TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid = ""
    
    def connect(self, target_ip, target_port):
        if self.sock:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (target_ip, target_port)
        self.sock.connect(self.server_address)

    def proses(self, cmdline):
        j = cmdline.split(" ")
        try:
            command = j[0].strip()
            if command == 'auth':
                username = j[1].strip()
                password = j[2].strip()
                return self.login(username, password)
            elif command == 'send':
                usernameto = j[1].strip()
                message = " ".join(j[2:])
                return self.sendmessage(usernameto, message)
            elif command == 'inbox':
                return self.inbox()
            elif command == 'create_group':
                groupname = j[1].strip()
                return self.create_group(groupname)
            elif command == 'join_group':
                groupname = j[1].strip()
                return self.join_group(groupname)
            elif command == 'send_group':
                groupname = j[1].strip()
                message = " ".join(j[2:])
                return self.send_group_message(groupname, message)
            elif command == 'group_inbox':
                groupname = j[1].strip()
                return self.group_inbox(groupname)
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
            return "-Maaf, command tidak benar"

    def sendstring(self, string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                if data:
                    receivemsg = "{}{}".format(receivemsg, data.decode())
                    if receivemsg[-4:] == '\r\n\r\n':
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return {'status': 'ERROR', 'message': 'Gagal'}

    def login(self, username, password):
        string = "auth {} {} \r\n".format(username, password)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            self.tokenid = result['tokenid']
            return "username {} berhasil login, token {}".format(username, self.tokenid)
        else:
            return "Error, {}".format(result['message'])

    def sendmessage(self, usernameto="xxx", message="xxx"):
        if self.tokenid == "":
            return "Error, tidak terotorisasi"
        string = "send {} {} {} \r\n".format(self.tokenid, usernameto, message)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "Pesan terkirim ke {}".format(usernameto)
        else:
            return "Error, {}".format(result['message'])

    def inbox(self):
        if self.tokenid == "":
            return "Error, tidak terotorisasi"
        string = "inbox {} \r\n".format(self.tokenid)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "{}".format(json.dumps(result['messages']))
        else:
            return "Error, {}".format(result['message'])

    def create_group(self, groupname):
        if self.tokenid == "":
            return "Error, tidak terotorisasi"
        string = "create_group {} {} \r\n".format(self.tokenid, groupname)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "Group {} created".format(groupname)
        else:
            return "Error, {}".format(result['message'])

    def join_group(self, groupname):
        if self.tokenid == "":
            return "Error, tidak terotorisasi"
        string = "join_group {} {} \r\n".format(self.tokenid, groupname)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "Berhasil join grup {}".format(groupname)
        else:
            return "Error, {}".format(result['message'])

    def send_group_message(self, groupname, message):
        if self.tokenid == "":
            return "Error, tidak terotorisasi"
        string = "send_group {} {} {} \r\n".format(self.tokenid, groupname, message)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "Pesan grup berhasil terkirim ke {}".format(groupname)
        else:
            return "Error, {}".format(result['message'])

    def group_inbox(self, groupname):
        if self.tokenid == "":
            return "Error, tidak terotorisasi"
        string = "group_inbox {} {} \r\n".format(self.tokenid, groupname)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "{}".format(json.dumps(result['messages']))
        else:
            return "Error, {}".format(result['message'])

if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))
