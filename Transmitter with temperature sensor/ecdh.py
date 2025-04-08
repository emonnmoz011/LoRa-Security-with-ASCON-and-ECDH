import os
import ubinascii
import uhashlib
from x25519 import base_point_mult,multscalar,bytes_to_int,int_to_bytes


a = os.urandom(32)
b = os.urandom(32)
#a = int_to_bytes(8,32) # just for testing a=10 (32 bytes - 256 bits)
#b = int_to_bytes(8,32) # just for testing b=12 (32 bytes - 256 bits)


print ("Alice Private:",a)
print ("Bob Private:",b)


#print (f"\n\nBob private (b):\t{bytes_to_int(b)}")
#print (f"Alice private (a): \t{bytes_to_int(a)}")


# Traditional ECDH: 
a_pub = base_point_mult(a)
b_pub = base_point_mult(b)

print ("\n\nBob public (bG):\t",ubinascii.hexlify(b_pub.encode()))

print ("Alice public (aG):\t",ubinascii.hexlify(a_pub.encode()))



k_a = multscalar(a, b_pub) # a (bG)
k_b = multscalar(b, a_pub) # b (aG)

#print('emon:',k_a.encode())





# Generate a SHA-256 hash of the shared secret
hash_a = uhashlib.sha256(k_a).digest()
hash_b = uhashlib.sha256(k_b).digest()

# Take the first 16 bytes of the hash to get a 128-bit key
key_a = hash_a[:16]
key_b = hash_b[:16]

print("\n\nBob shared (b)aG:\t", key_b)
print("Alice shared (a)bG:\t", key_a)

print("\n\nBob shared (b)aG:\t", ubinascii.hexlify(key_b))
print("Alice shared (a)bG:\t", ubinascii.hexlify(key_a))

'''print ("\n\nBob shared (b)aG:\t",ubinascii.hexlify(k_b.encode()))
print ("Alice shared (a)bG:\t",ubinascii.hexlify(k_a.encode()))


print ("\n\nJust checking ...")

res=int_to_bytes(64,32)
k = base_point_mult(res)
print ("\n\nChecking shared (ab)G:\t",ubinascii.hexlify(k.encode()))'''