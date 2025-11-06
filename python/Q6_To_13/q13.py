import math

def circle_area(radius):
    return math.pi*radius**2

def triangle_area(ray1, ray2, angle):
    return round(0.5*ray1*ray2*math.sin(math.radians(angle)),1)

def angle(l1, l2):
    m = l1[0] - l2[0]
    b = l2[1] - l1[1]

    x = b/m
    y = l1[0]*x + l1[1]

    y_diff = abs(b)
    s = (y_diff*x)/2
    l1_ray = math.sqrt(x**2 + (l1[1]-y)**2)
    l2_ray = math.sqrt(x**2+ (l2[1]-y)**2)

    return round( math.degrees(math.asin((2 * s) / (l1_ray * l2_ray))),1 )


assert str(circle_area(10))== "314.1592653589793"
assert str(triangle_area(4, 8, 30)) == "8.0"
assert str(angle((2, 4), (-3, 16))) == "45.0"
