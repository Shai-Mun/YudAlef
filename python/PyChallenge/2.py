with open('2text.txt', 'r') as f:
    data = f.read()

new_msg = ""
for char in data:
    if char.isalpha():
        new_msg += char

print(new_msg)

