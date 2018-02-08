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

errors = {}
errors["TIMEOUT"] = "TIMEOUT"
errors["BAD LOGIN"] = "Wrong Credentials"

def access(hostname, username, password, type):
    try:
        conn = None
        if type == 1:
            conn = pexpect.spawnu("ssh " + username + "@" + hostname, timeout = 5)
            conn.expect([pexpect.TIMEOUT, "[Pp]assword: "])

            if conn.match_index == 0:
                print("SSH > " + errors["TIMEOUT"])
                return False

            conn.sendline(password)
            conn.expect([pexpect.TIMEOUT, "[Pp]assword: ", ">"])
            pos = conn.match_index
            if pos == 0:
                print("SSH > " + errors["TIMEOUT"])
                return False
            elif pos == 1:
                print("SSH > " + errors["BAD LOGIN"])
                return False
            elif pos == 2:
                print("SSH > Login on hostname " + hostname + " done with sucess")

        elif type == 2:
            conn = pexpect.spawnu("telnet " + hostname, timeout = 5)
            conn.expect([pexpect.TIMEOUT, "[Uu]sername: "])

            if(conn.match_index == 0):
                print("TELNET > " + errors["TIMEOUT"])
                return False

            conn.sendline(username)
            conn.expect([pexpect.TIMEOUT, "[Pp]assword: "])

            if conn.match_index == 0:
                print("TELNET > " + errors["TIMEOUT"])
                return False

            conn.sendline(password)
            conn.expect([pexpect.TIMEOUT, "% Login invalid" ,">"])
            pos = conn.match_index

            if pos == 0:
                print("TELNET > " + errors["TIMEOUT"])
                return False
            elif pos == 1:
                print("TELNET > " + errors["BAD LOGIN"])
                return False
            elif pos == 2:
                print("TELNET > Login on hostname " + hostname + " done with sucess")

        rootpassword = getpass.getpass('root password: ')
        conn.sendline("enable")
        conn.expect([pexpect.TIMEOUT, "[Pp]assword: "])
        pos = conn.match_index

        if pos == 0:
            print("Root Access > " + errors["TIMEOUT"])
            return False

        conn.sendline(rootpassword)
        conn.expect([pexpect.TIMEOUT, "timeout expired", "% Bad secrets", "#"])

        if pos == 0 || pos == 1:
            print("Root Access > " + errors["TIMEOUT"])
            return False
        elif pos == 2:
            print("Root Access > " + errors["BAD LOGIN"])
            return False

        print("Root Access Guaranteed")

        """ Other Commands """
        return True

    except Exception as e:
        error = "SSH ERROR" if type == 1 else "TELNET ERROR"
        print(error)
        print(e)
        return False

def trySocket( hostname, port ):
    flag = None
    s = socket.socket()
    try:
        s.settimeout(5)
        s.connect((hostname, port))
        s.settimeout(None)

        if port == 22:
            return False
            print("SSH Socket Open")
        else: print("TELNET Socket Open")

        flag = True
    except Exception as e:
        print(e)
        flag = False
    finally:
        s.close()
        return flag

while 1:
    ipaddress = input('ip adress: ')

    #Returns non-zero value if fails
    response = os.system("ping -c 3 " + ipaddress + " > /dev/null")
    if response != 0:
        print("IP don't reachable")
        continue

    username = input('username: ')
    password = getpass.getpass('password: ')

    if trySocket(ipaddress, 22):
        access(ipaddress, username, password, 1)
    elif trySocket(ipaddress, 23) :
        access(ipaddress, username, password, 2)
