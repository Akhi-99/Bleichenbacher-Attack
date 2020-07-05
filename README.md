# Bleichenbacher Attack
## Introduction : 
BleichenBacker Attack is an Adaptive Chosen Ciphertext Attack against protocols based on the RSA encryption standard. It is an interesting attack due to real-life implications(HTTPS- SSL/TLS). This attack is based on the assumption that the attacker has access to an oracle such that, for any chosen-ciphertext c, it responds whether the message is PKCS #1 V1.5 conforming or not. Based on the server’s reply, the attacker will choose the subsequent queries and gain information about the complete decryption.

## Background Theory :

### PKCS#1 V1.5 Block format for Encryption :
The encoding message of a message M in this format is as follows:

**PKCS1(M) = 0x00 | 0x02 | [non zero padding bytes] | 0x00 | [M]**

The first 2 bytes are constant (0x00, 0x02) which define the mode of operation (Encryption in our case). Next, there are nonzero padding bytes ( at least 8 bytes) followed by a constant separate byte (0x00) and finally our message. Using this scheme, the message length in bytes must not exceed k – 11 (where k is the total size of the encoded message = size of RSA modulus, in bytes).
	
Under this scheme, the oracle after receiving the ciphertext decrypts it and checks the first 2 bytes with [0x00,0x02]. If it doesn’t match, then the server reports an error message to the client.

**Oracle(c) = True ≡ (c<sup>d</sup> (mod n)) [0:2] == \x00\x02.**

In PKCS #1, the size of the encoded message is the same as the modulus size. The complete encryption algorithm, under this scheme, is the following: first, the message is encoded using PKCS #1; then, the result is converted to an integer value, encrypted using RSA, and then converted back to a byte string. The oracle (i.e. server) receives the encrypted byte string value, converts it back to an integer, applies RSA decryption using (n, d), converts the result to a byte string, and then checks whether the first 2 bytes are \x00\x02.

### Attack :

As described in the paper [1], the attack can be divided into three phases. Simply speaking, Bleichenbacher’s algorithm is the following:

Let c denote the ciphertext that the attacker has intercepted. To construct a query, generate a value s and send 𝑐 ′ = 𝑐𝑠<sup>𝑒</sup> (𝑚𝑜𝑑 𝑛) - this corresponds to multiplying the plain message m by s, because 𝑐𝑠<sup>𝑒</sup> (𝑚𝑜𝑑 𝑛) = (𝑚𝑠)<sup>𝑒</sup> (𝑚𝑜𝑑 𝑛) [ *Homomorphic multiplicative property of RSA* ]

After decryption, the server obtains 𝑚′ = (𝑐𝑠<sup>𝑒</sup> ) 𝑑(𝑚𝑜𝑑 𝑛) and reports whether the first 2 bytes of the byte string conversion of m’ are 0x00 and 0x02, respectively. If a random message m is sent to the server, the probability that m is PKCS conforming is roughly in the interval [2<sup>−15</sup>, 2<sup>−17</sup>]. The exact probability highly depends on the size and value of the RSA modulus n. 

The value s can be found with a non-negligible probability. After finding the value of s such that the ciphertext decrypts to a proper PKCS encoded message, the attacker will know that for this value of s, 𝑚𝑠 (𝑚𝑜𝑑 𝑛) is in a specific range (i.e. the range of integers which begins with \x00\x02 when converted to a byte string, using big-endian representation). 

The attack is said to be adaptive in the sense that future queries are constructed based upon the information obtained from the previous server replies. Thus, the rest of the attack sends queries with carefully chosen values of s and narrows the range of values it can take, up to a point when an interval of the form [𝑎, 𝑎] is found. Finally, the byte string value of a is the plaintext that we are interested in.


### Attack Description( Mathematics involved):

As stated above, there are three phases of the attack (four if we also account for the blinding step, but in this implementation, it is assumed that the attacker has intercepted the ciphertext of a PKCS #1 encoded message, so blinding is not necessary). 
Let 𝐵 = 2<sup>8(𝑘−2)</sup> be the length of the message, in bits, without the first 2 bytes; k is the length of the RSA modulus, in bytes (256 / 8 = 32, in this implementation). Since 𝑚𝑠 is PKCS conforming: 2𝐵 ≤ 𝑚𝑠(𝑚𝑜𝑑 𝑛) < 3𝐵. Let 𝑀 = {[2𝐵, 3𝐵 − 1]} be the initial set of intervals (the interval represents the broadest range of possible s-values).

**1. Searching :**
 We start the search by trying to find the smallest 𝑠<sub>1 </sub> ≥ 𝑛 / 3⋅𝐵, such that 𝑐𝑠<sub>1 </sub><sup>𝑒</sup> (𝑚𝑜𝑑 𝑛) is PKCS conforming. Next, we continue the search based upon the size of M (i.e. the number of intervals in M). 
If M contains at least 2 intervals, then look for the smallest 𝑠<sub>i </sub>≥ 𝑠<sub>i </sub>−1 such that 𝑐𝑠<sub>i </sub><sup>𝑒</sup> (𝑚𝑜𝑑 𝑛) is PKCS conforming. Otherwise, if M contains exactly one interval of the form [𝑎, 𝑏], then use the previously calculated s-value to derive lower and upper bounds for the next s-value, i.e choose until we arrive at a PKCS conforming ciphertext 𝑐𝑠i<sup>𝑒</sup> (𝑚𝑜𝑑 𝑛).

<p align="center">
  <img src="https://github.com/Akhi-99/Bleichenbacher-Attack/blob/master/Images/2020-06-05%20(2).png">
</p>





