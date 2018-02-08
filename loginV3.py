from pexpect import pxssh
import pexpect
import getpass
import sys
import os
import socket

""" Types
1 - SSH
2 - TELNET
"""

"""
funcao que executa um comando
parametros conexao, comando, timeout, logfile funcao, logfile conexao
"""

"""
interface grafica que tem arquivos pra usuarios, senha de roots e comando e lista de ip's
"""

errors = {}
errors["TIMEOUT"] = "TIMEOUT"
errors["GENERIC"] = "Error"
errors["BAD LOGIN"] = "Wrong Credentials"

def loginRoot(conn, rootpasswords):
    conn.sendline("enable")
    conn.expect("[Pp]assword: ")

    flag = False
    for i in range(0, len(rootpasswords)):
        conn.sendline(rootpasswords[i])
        conn.expect(["#", "% Bad secrets", "[Pp]assword: ", "timeout expired", pexpect.TIMEOUT, pexpect.EOF])
        pos = conn.match_index

        if pos == 0:
            print("Root Access Guaranteed")
            print("Used " + rootpasswords[i])
            flag = True
            break;
        elif pos == 1:
            print("Root Access > " + errors["BAD LOGIN"])
            conn.sendline("enable")
            conn.expect("[Pp]assword: ")
        elif pos == 2:
            print("Root Access > " + errors["BAD LOGIN"])
        elif pos == 3 or pos == 4:
            print("Root Access > " + errors["TIMEOUT"])
        elif pos == 5:
            print("Root Access > " + errors["GENERIC"])

    if flag == False:
        print("Root Inaccessible")
        return False

def SSH(conn, hostname, username, password):
    conn = pexpect.spawnu("ssh " + username + "@" + hostname, timeout = 5)
    conn.expect(["[Pp]assword: ", pexpect.EOF, pexpect.TIMEOUT])

    if conn.match_index == 1:
        print("SSH > " + errors["GENERIC"])
        return conn, False, False
    elif conn.match_index == 2:
        print("SSH > " + errors["TIMEOUT"])
        return conn, False, False

    conn.sendline(password)
    conn.expect(["#", ">", "[Pp]assword: ", pexpect.TIMEOUT, pexpect.EOF])
    pos = conn.match_index

    if pos == 0 or pos == 1:
        print("SSH > Login on hostname " + hostname + " done with sucess")
        print("Used: " + username + "@" + password)
        loggedRoot = True if pos == 0 else False
        return conn, True, loggedRoot
    elif pos == 2:
        print("SSH > " + errors["BAD LOGIN"])
    elif pos == 3:
        print("SSH > " + errors["TIMEOUT"])
    elif pos == 4:
        print("SSH > " + errors["GENERIC"])
    return conn, False, False

def TELNET(conn, hostname, username, password):
    conn = pexpect.spawnu("telnet " + hostname, timeout = 5)
    conn.expect(["[Uu]sername: ", pexpect.TIMEOUT, pexpect.EOF])

    if conn.match_index == 1:
        print("TELNET > " + errors["TIMEOUT"])
        return conn, False, False
    elif conn.match_index == 2:
        print("TELNET > " + errors["GENERIC"])
        return conn, False, False

    conn.sendline(username)
    conn.expect(["[Pp]assword: ", pexpect.TIMEOUT, pexpect.EOF])

    if conn.match_index == 1:
        print("TELNET > " + errors["TIMEOUT"])
        return conn, False, False
    elif conn.match_index == 2:
        print("TELNET > " + errors["GENERIC"])
        return conn, False, False

    conn.sendline(password)
    conn.expect(["#", ">", "% Login invalid", pexpect.TIMEOUT, pexpect.EOF])
    pos = conn.match_index

    if pos == 0 or pos == 1:
        print("TELNET > Login on hostname " + hostname + " done with sucess")
        print("Used: " + username + "@" + password)
        loggedRoot = True if pos == 0 else False
        return conn, True, loggedRoot
    elif pos == 2:
        print("TELNET > " + errors["BAD LOGIN"])
    elif pos == 3:
        print("TELNET > " + errors["TIMEOUT"])
    elif pos == 4:
        print("TELNET > " + errors["GENERIC"])
    return conn, False, False

def access(hostname, usernames, passwords, rootpasswords, type):
    try:
        conn = None
        flag = False
        loggedRoot = False

        if type == 1:
            for i in range(0, len(usernames)):
                conn, flag, loggedRoot = SSH(conn, hostname, usernames[i], passwords[i])
                if flag: break;
        elif type == 2:
            for i in range(0, len(usernames)):
                conn, flag, loggedRoot = TELNET(conn, hostname, usernames[i], passwords[i])
                if flag: break;

        if flag == False:
            print("No one user/password match")
            return None, False

        if loggedRoot == False and loginRoot(conn, rootpasswords) == False:
            print("No one root password match")
            return None, False

        return conn, True

    except Exception as e:
        error = "SSH ERROR" if type == 1 else "TELNET ERROR"
        print(error)
        print(e)
        return None, False

def trySocket( hostname, port ):
    flag = None
    s = socket.socket()
    try:
        s.settimeout(5)
        s.connect((hostname, port))
        s.settimeout(None)

        if port == 22: print("SSH Socket Open")
        else: print("TELNET Socket Open")

        flag = True
    except Exception as e:
        print(e)
        flag = False
    finally:
        s.close()
        return flag

def executeCommand(conn, command, timeout, logfunction, logconnection):
    conn.logfile = open(logconnection, 'w')
    conn.sendline(command)
    conn.expect(["#", pexpect.EOF, pexpect.TIMEOUT], timeout=timeout)

    if conn.match_index == 0:
        output = conn.before.split("\r\n")
        return output;
    elif conn.match_index == 1:
        print(errors["TIMEOUT"])


while 1:
    ipaddress = input('ip adress: ')
    usernames = []
    passwords = []
    rootpasswords = []

    #Just for tests
    data = open("users.txt", "r")
    for line in data:
        aux = line.split()
        usernames.append(aux[0])
        passwords.append(aux[1])
    data.close()

    data = open("roots.txt", "r")
    for line in data:
        rootpasswords.append(line.split()[0])

    #Returns non-zero value if fails
    response = os.system("ping -c 3 " + ipaddress + " > /dev/null")
    if response != 0:
        print("IP don't reachable")
        continue

    #splitlines();

    if trySocket(ipaddress, 22):
        conn, flag = access(ipaddress, usernames, passwords, rootpasswords, 1)
    elif trySocket(ipaddress, 23) :
        conn, flag = access(ipaddress, usernames, passwords, rootpasswords, 2)

    if flag == False:
        break

    timeout = int(input("Commands Timeout:"))
    nameFile = input("Log File: ")
    commands = open("commands.txt", "r")
    for command in commands:
        output = executeCommand(conn, command, timeout, None, nameFile)
        print(output[1])
