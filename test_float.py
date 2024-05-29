import struct

num = 80.2

def binary(num):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))


print(binary(num))

