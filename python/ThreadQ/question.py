import threading
import time

def printL(id, letter):
    print(letter, end="")
    time.sleep(100)

name = input("Enter your name\n")
i = 1
for char in name:
    t = threading.Thread(target=printL, args=(i, char))
    t.start()
    i += 1