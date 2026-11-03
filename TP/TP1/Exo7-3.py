import fractions

somme = fractions.Fraction(0,1)
for i in range(1000):
	somme += fractions.Fraction(1,10)

print(somme)
print(fractions.Fraction(1,10) + fractions.Fraction(2,10) == fractions.Fraction(3,10))
