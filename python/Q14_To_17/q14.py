from datetime import datetime

print(datetime.now())

def h(s, SIZE = 8):
    print("len=", len(s))
    for p in [s[i*SIZE : min((i+1)*SIZE, len(s))] for i in range(len(s) // SIZE + 1)]:
        print(b" ".join([b"%02X" % int(p[i]) if i < len(p) else b"  " for i in range(SIZE)]) + \
              b"  " + b"".join([chr(p[i]).encode()
              if p[i] > 31 and p[i] < 128 else b"." for i in range(len(p))]))

s = [0, 255, 10]
h(s)

#הפעולה מקבלת מערף של מספרים וממירה אותם לבתים, ואז מדפיסה את הבתים למסך, בצורה הקסדצימלית.