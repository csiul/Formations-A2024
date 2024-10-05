#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

from pwn import *
import time

# p = process("./chal2")
p = remote("159.203.46.23", 2222)
p.recvuntil("Password:")

output = b"Mauvais password!"
salt = 9
secret = 13371337
while("GOOD JOB!" not in output.decode("utf-8")):
    password = secret ^ salt
    salt = salt + 1
    p.sendline(str(password))
    output = p.recv()
    print(output)
    sleep(0.5)

output = p.recv()
print(output)