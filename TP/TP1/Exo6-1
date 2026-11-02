def vers_binaire(n):
	if n == 0:
		return "0"
	resultat = ""
	quotient = n
	while quotient != 0:
		resultat = str(quotient%2) + resultat
		quotient = quotient//2
	return resultat

print("5 :", vers_binaire(5))
print("512 :", vers_binaire(512))
print("0 :", vers_binaire(0))

print("--DÉBUT TEST--")
print(all(vers_binaire(n) == bin(n)[2:] for n in range(10000)))
print("--FIN TEST--")
