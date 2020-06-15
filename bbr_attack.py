from subprocess import *
from binascii import *
import sys
import os

def sO(y):
    rr = hexlify(unhexlify('%0256x' % y))
    #print rr[0:4]
    if (rr[0:4]) == "0002":
        if "00" in rr[4:]:
            return True
        else: 
            return False

    else:
        return False

def ceil(x,y):
    return x/y + (x%y != 0)

def floor(x,y):
    return x//y


# n is obtained by openssl tool followed by translation to hexa format

n = 0x00e133440e6948ba3905e722442723bc5741fef35213731f3871de50c904676fefc836dc9253ead0a79dc89c42647d1614a3e167550e9890c379045e8822451fc83bf53ed66885654e9658bff02d5cdb13d5e28e9ac650c380552195ee5927eb51f9e6fbeef8fde1639f05b15e677958042d922e2f62c024071839e7602ddfed6f
B = 2**1008
m0 = 0x0002a76dd2cdb43e02a0e441552e79e9df2e78f7e85376d73e6cac8fbd54b0dde79b60cc321c4f964bf568263873342f9d541b5a9496fbbd18c78b69a58a526b123229bfd401f4c31c2ff6b24c5fbb92d6c969677420ca586671b233d090f4410fe30c38a57e12bbd693a7efe8d083bd34b68f81c8fc00486920416b68696c0a

# In m0 , our original message(in hexa format) is after 00

#m0 = 0x0002ea42c1185be80e167bc38604acd4ce581127d89ea14bf6251ab9df9e7f7e9967dda136e543da6c65bd2d599d488f0cb06c68a1fdfc627bdc18776bb85ceb7e1e741a6c0da0e931eebfd2275caea7066407a82d9cc9d7ccdf34742d7db0735abf076e99af8e5aaa2f343118c872a3fe26f3c8cba700766973686e7576700a

s1 = ceil(n,3*B) #  starting value for s1

print "[-] Starting search for s1 (from value %i)" % s1
i2a = 1          # counter for iterations
k = 128 # number of bytes of modulus 128 = 1024 bits
fk = '%0'+str(k*2)+'x' # format string to print hex 0 padded
while True:
    m1 = (s1 * m0) % n
#    print "s1 = ",s1
    if sO(m1):   # call the (simulated) oracle
        break    # padding is correct, we have found s1
    i2a += 1
    s1 += 1      # try next value of s1

print "[*] Search done in %i iterations" % i2a
print "    s1: %i" % s1

B2,B3 = 2*B,3*B # constants to avoid recomputing them any time
newM = set([])  # collects new intervals
k = 128 # number of bytes of modulus 128 = 1024 bits
fk = '%0'+str(k*2)+'x' # format string to print hex 0 padded
#print ceil((B2*s1 - B3 + 1),n),floor(((B3-1)*s1 - B2),n) + 1
a = B2
b = B3 - 1
si = s1
print ceil((a*si - B3 + 1),n),floor(((b)*si - B2),n) + 1
#raw_input()
for r in range(ceil((a*si - B3 + 1),n),floor(((b)*si - B2),n) + 1):      
    aa = ceil(B2 + r*n,si)
    bb = floor(B3 - 1 + r*n, si)           
    newa = max(a,aa)
    newb = min(b,bb)                             
    if newa <= newb:                                
        newM |= set([ (newa, newb) ])
print len(newM)
#raw_input()
while True:
    if len(newM) == 1:
        loner = newM.pop()
        newM.add(loner)
        a = loner[0]
        b = loner[1]
        r = ceil((b*si - B2)*2,n) # starting value for r
        i2c,nr = 0,1    # for statistics
        found = False
        while not found:
            #print ceil((B2 + r * n),b),floor((B3-1 + r * n),a)+1

            for si in range(ceil((B2 + r * n),b),floor((B3-1 + r * n),a)+1):
                mi = (si * m0) % n
                i2c += 1
                if sO(mi):
                    found = True
                    break # we found si
            if not found:
                r  += 1   # try next value for r
                nr += 1
            #print "    explored values of r:  %i" % r
        print "[*] Search done in %i iterations" % (i2c)
        print "    explored values of r:  %i" % nr
        print "    s_%i:                    %i" % (i2c,si)
    elif len(newM) > 1:
        si += 1
        while True:
            m1 = (si * m0) % n
#    print "s1 = ",s1
            if sO(m1):   # call the (simulated) oracle
                break    # padding is correct, we have found s1
            si += 1
        print "    si: %i" % si
    newMM = set([])

    for (a,b) in newM: # for all intervals
        for r in range(ceil((a*si - B3 + 1),n),floor((b*si - B2),n) + 1):
            aa = ceil(B2 + r*n,si)
            bb = floor(B3 - 1 + r*n, si)
            newa = max(a,aa)
            newb = min(b,bb)
            if newa <= newb:
                newMM |= set([ (newa, newb) ])
#    print len(newMM)

    if len(newMM)>0:
        newM = newMM

    if len(newM) == 1:
        popped = newM.pop()
        if popped[0] == popped[1]:
            print 'Found a:'+fk % popped[0]
            if(popped[0]==m0):
                print("Attack Successful, Message found")
            break
        newM.add(popped)




