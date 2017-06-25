# -*- coding: utf-8 -*-

import socket
import sys
import os
import select
import termios
import tty
import time

HOST = 'ptt.cc'
PORT = 443 

def get_ch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ECHO
    try:
        #termios.tcsetattr(fd, termios.TCSADRAIN, new)
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def get_key():
    ch = get_ch()
    if '\x1b' == ch:
        data = get_ch()
        data = data + get_ch()
        if data == '[A':
            return "\E[A"
        elif data == '[B':
            return "\E[B"
        elif data == '[C':
            return "\E[C"
        elif data == '[D':
            return "\E[D"
    elif '\x03' == ch:
        print  "%r" % get_ch()
        exit(0)  
    else:
        return ch


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
data = s.recv(1024)

login = False

while True:
    socket_list = [sys.stdin, s]
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    for sock in read_sockets:
        if sock == s:
            data = sock.recv(4096)
            if not data:
                print "Log: Data End"
                s.close()
                break
            else:
                udata =  data.decode('big5', errors="ignore")
                print udata
                if u"請輸入代號" in udata:
                  print "Enter user:"
                  msg = raw_input()
                  s.send(msg + "\r\n")
                elif u"請輸入您的密碼" in udata:
                  print "Enter password"
                  msg = raw_input()
                  s.send(msg + "\r\n")  
                elif u"上次您是從" in udata:
                  login = True 
                    
        if login:
            time.sleep(1)
            msg = get_key()
            print "Send %r" % msg
            s.send(msg)
            s.send("^l")
s.close()
