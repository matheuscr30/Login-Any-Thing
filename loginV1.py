from pexpect import pxssh
import pexpect
import getpass
import sys

def trySSH( hostname, username, password ):
    try:
        conn = pxssh.pxssh()
        conn.login (hostname, username, password, auto_prompt_reset=False)
        print("SSH > Login no hostname " + hostname + " feito com sucesso")
        rootpassword = getpass.getpass('root password: ')
        conn.sendline("enable")
        print(conn)
        conn.prompt()
        conn.sendline(rootpassword)
        conn.logout()
        print("SSH > Root Acess")
        return True
    except Exception as e:
        print("SSH > Login no hostname " + hostname + " falhou")
        print(e)
        return False

def tryTELNET( hostname, username, password ):
    try:
        conn = pexpect.spawn("telnet " + hostname)
        conn.expect(":")
        #conn.logfile=sys.stdout.buffer
        conn.sendline(username)
        conn.expect(":")
        conn.sendline(password)
        conn.expect(">")
        conn.sendline("enable")
        rootpassword = getpass.getpass('root password: ')
        conn.sendline(rootpassword)
        print("TELNET > Login no hostname " + hostname + " feito com sucesso")
        return True
    except Exception as e:
        print("TELNET > Login no hostname " + hostname + " falhou")
        print(e)
        return False

while 1:
    ipaddress = input('ip adress: ')
    result = pexpect.spawn('ping -c 4 ' + ipaddress)

    cont = 0
    while cont != 5:
        line = result.readline()
        if not line: break
        cont += 1
        #print(line)

    if cont < 5:
        print("Nome ou Serviço Desconhecido")
        continue
    else:
        print("IP reconhecido com sucesso")
        username = input('username: ')
        password = getpass.getpass('password: ')

        if trySSH(ipaddress, username, password) == False:
            tryTELNET(ipaddress, username, password)
