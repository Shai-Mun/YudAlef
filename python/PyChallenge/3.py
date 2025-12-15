import re

with open('3text.txt', 'r') as f:
    data = f.read()

print("".join(re.findall('[a-z][A-Z][A-Z][A-Z]([a-z])[A-Z][A-Z][A-Z][a-z]', data)))