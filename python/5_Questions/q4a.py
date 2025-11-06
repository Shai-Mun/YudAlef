num = range(1, 100)
numbers = list(filter(lambda x: x % 7 == 0 or "7" in str(x), num))
print(numbers)