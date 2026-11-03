import math

def racines(a, b, c):
	delta = b*b - 4*a*c
	if delta < 0:
		raise ValueError
	x1 = (-b+math.sqrt(delta))/2*a
	x2 = c/(a*x1)
	return (x1, x2)

x1, x2 = racines(1, -10**8, 1)
print(x1, x2)
print(x1*x2)

for x in (x2, x1):
	residu = x * x - 1e8 * x + 1
	print(f"residu : {residu:.1e}, soit {residu / max(x * x, 1.0):.1e} en relatif")
