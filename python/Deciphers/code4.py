def strip_non_letters_filter(w):
    return ''.join(filter(w.isalpha, w))


ABCD = "abcdefghijklmnopqrstuvwxyz"     # also same     string.ascii_lowercase
valids = {}
for ch in ABCD:
    valids[ch] = [x for x in ABCD]

with open('ex4_dictionary', 'r') as d:
    with open('ex4_cipher', 'r') as c:
        for word in c:
            stripped = strip_non_letters_filter(word)



