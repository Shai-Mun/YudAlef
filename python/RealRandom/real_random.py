import math
import random
import numpy as np
import matplotlib.pyplot as plt

length = 1000000
nums = [random.random() for i in range(length)]
cnt = 0
for n in nums:
    if 0.5 <= n <= 0.7:
        cnt += 1

print(cnt/length)

a = np.random.random(10**6)
b = np.random.random(10**6)
ratios = np.floor(a/b)
cnt = 0
for r in ratios:
    if int(r) % 2 == 0:
        cnt += 1
my_ratio = cnt/length
print(my_ratio)

a = np.random.random(10**6)
b = np.random.random(10**6)
ratios = []
for n1, n2 in zip(a, b):
    r = 0
    if n1 > n2:
        r = n1 / n2
    else:
        r = n2 / n1
    ratios.append(math.floor(r))
cnt = 0
for r in ratios:
    if int(r) % 2 == 0:
        cnt += 1
my_ratio = cnt/length
print(my_ratio)

a = [ random.randint(1,10**100) for _ in range(100)]
cnt = 0
for n in a:
    if "7" in str(n):
        cnt += 1
print(len(a)/cnt)

# plt.hist(my_ratio, range= (0,10), bins=20, rwidth =0.9 )
# plt.show()

