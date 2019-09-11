import turtle as t
import math

l = lambda x: t.left(90*x)
r = lambda x: t.right(90*x)
f = lambda x: t.forward(x)

def hilbert(length, parity, depth):
    if depth==0:
        return
    l(parity)
    hilbert(length, -parity, depth-1)
    f(length)
    r(parity)
    hilbert(length, parity, depth-1)
    f(length)
    hilbert(length, parity, depth-1)
    r(parity)
    f(length)
    hilbert(length, -parity, depth-1)
    l(parity)

#r(1)
t.speed('fastest')
while 1:
    d = int(input('l'))
    o=int(input('o'))
    hilbert(d,1,o)

input()
