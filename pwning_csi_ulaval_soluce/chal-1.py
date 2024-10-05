#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

from pwn import *

# p = process("./a.out")
p = remote("159.203.46.23",1234)

p.recvuntil("Attention il faut faire vite!")
output = p.recv()
output_n = output.split(b"\n")
instruction = output_n[1]
response = b"Continue!"
while b"Continue!" in response:   
    instruction_space = instruction.split(b" ")
    first_operande = instruction_space[0]
    first_base = instruction_space[2][:-1]
    second_operande = instruction_space[4]
    second_base = instruction_space[6][:-1]

    first_operande = int(first_operande,int(first_base))
    second_operande = int(second_operande,int(second_base))
    operateur = instruction_space[3]
    result = 0
    if operateur == b"+":
        result = first_operande + second_operande
    elif operateur == b"-":
        result = first_operande - second_operande
    elif operateur == b"*":
        result = first_operande * second_operande
    p.sendline(str(result).encode("utf-8"))
    response = p.recv()
    output = p.recv()
    output_n = output.split(b"\n")
    instruction = output_n[1]
    print(output)