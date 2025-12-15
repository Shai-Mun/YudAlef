# msg = "g fmnc wms bgblr rpylqjyrc gr zw fylb. rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyr'q ufw rfgq rcvr gq qm jmle. sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj."

msg = "http://www.pythonchallenge.com/pc/def/map.html"
new_msg = ""
for char in msg:
    if char.isalpha():
        new_char = chr(ord(char) + 2)
        if new_char > 'z':
            new_char = chr(ord(new_char) - 26)
        new_msg += new_char
    else:
        new_msg += char

print(new_msg)
