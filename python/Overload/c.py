class Square:
    def __init__(self, w):
        self.width = w
        self.height = w

    def area(self):
        return self.width * self.height

    def peri(self):
        return self.width*4

    def __add__(self, other):
        return self.peri() + other.peri()

    def __mul__(self, other):
        return self.area() + other.area()

    def __truediv__(self, other):
        return self.area() / other.area()

    def __sub__(self, other):
        return f'{type(self)}'

    def __getitem__(self, key):
        if key == 0:
            return self.width
        if key == 1:
            return self.height

    def __eq__(self, other):
        if self.width == other.width and self.height == other.height:
            return True
        return False


class Rect:
    def __init__(self, w, h):
        self.width = w
        self.height = h

    def area(self):
        return self.width * self.height

    def peri(self):
        return self.width*2 + self.height*2


sq = Square(10)
rect = Rect(4, 10)
print("Square perimeter: " + str(sq.peri()))
print("Rectangle perimeter: " + str(rect.peri()))
print("Square area: " + str(sq.area()))
print("Rectangle area: " + str(rect.area()))

print("Add overload (perimeter addition): ")
print(sq + rect)

print("Mul overload (area addition): ")
print(sq * rect)

print("Div overload (area ratio): ")
print(sq / rect)

print("Indexing overload (get width (0) or height (1)): ")
print(sq[1])


print("Equal overload (check if rect is identical to square): ")
print(sq == rect)



