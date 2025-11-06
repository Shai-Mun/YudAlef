import math

num = 0
while num <= 5:
    if math.ceil(round(num,1)) == round(num,1):
        print(round(num))
    else:
        print(round(num, 1))
    num += 0.1