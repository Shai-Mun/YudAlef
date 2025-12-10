import base64
import random
import string

def encrypt1(message, key):
    return "".join([chr(ord(x) + int(key[0])) for x in message])


def decrypt1(message, key):
    return "".join([chr(ord(x) - int(key[0])) for x in message])


msg1 = "Wkh#dwwdfn#zloo#vwduw#dw#vxqvhw"
key1 = "309"
print(decrypt1(msg1, key1))


def encrypt2(message,key):
    return base64.b64encode("".join([chr(ord(message [i]) ^ ord(key [i % len(key)])) for i in range(len(message ))]).encode())


def decrypt2(message):

    for k in range(10000):
        key2 = str(k).zfill(4)
        dec_b64 = base64.b64decode(message).decode()
        dec_msg2 = "".join([chr(ord(dec_b64 [i]) ^ ord(key2 [i % len(key2)])) for i in range(len(dec_b64 ))])
        if "The" in dec_msg2.split():
            return dec_msg2
    return ""


msg2 = "YVxcGVRATVhWXxlOXFhVGUZAWEtBFFZXFWBMXEZQWEAVWVZLW11XXg=="
print(decrypt2(msg2))


def encrypt3(message, key):
    random.seed(key)
    l = list(range(len(message)))
    random.shuffle(l)
    return "".join([message[x] for x in l])


def sort(message, key):
    random.seed(key)
    l = list(range(len(message)))
    random.shuffle(l)
    new_list = [-1 for i in range(len(message))]
    for x in range(len(l)):
        new_list[l[x]] = message[x]
    print("".join(new_list))


def decrypt3(message):
    letters = string.ascii_lowercase + string.ascii_uppercase
    key3 = ""
    for a in letters:
        for b in letters:
            for c in letters:
                random.seed(a + b + c)
                l = list(range(len(message)))
                random.shuffle(l)
                if message[l.index(0)] == "T":
                    if message[l.index(1)] == "h":
                        if message[l.index(2)] == "e":
                            sort(message, a + b + c)


msg3 = "kth tntTeia0lt a lua1 dtt: ro5 Scasa0 wary"
print(decrypt3(msg3))