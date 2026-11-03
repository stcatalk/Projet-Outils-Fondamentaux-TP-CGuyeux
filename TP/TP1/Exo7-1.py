import math

def racines_naif(a, b, c):
	x1 = (-b-math.sqrt(b*b-4*a*c))/2*a
	x2 = (-b+math.sqrt(b*b-4*a*c))/2*a
	return (x1, x2)

x1, x2 = racines_naif(1, -10**8, 1)
print(x1, x2)
print(x1*x2)
