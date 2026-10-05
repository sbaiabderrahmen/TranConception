produit = "pomme"
prix = 79.3
stock = 25 
print (f"total ; {prix * stock} pour le produit {produit .upper()} avec un stock de {stock} unitées")
prix_ttc = [12.99,15.49, 9.99 , 20.00]
prix_ht =  []
for p in prix_ttc:
    prix_ht.append(round(p/1.2,2))
    print (prix_ht)
prix_ht_1 = [round (p/1.2,2) for p in prix_ttc]
print (prix_ht_1)

prix_sup = [p for p in prix_ttc if p >= 15]
print ( prix_sup)


def calcul (prix, tva):
    return round (prix * (1*tva),2)
print(calcul(100,0.2))
def calcul_tva(prix,tva=0.19):
    return round(prix * tva , 2)
print(calcul_tva(100))
print(calcul_tva(100,0.12))
def facturer(client,*lignes):
    total=0
    for ligne in lignes:
        total += ligne
        return f"client : {client} - total : {total}"
    print (facturer("Alice", 100,200,50))

class Livre :
    def _init_(self,a,b,c):
        self.titre=a
        self.auteur=b
        self.prix=c
    def afficher (self):
        return f"{self.titre} par { self.auteur}" - prix : {self.prix}
def _str_(self):
  return f"{self.titre} par {self.auteur} - prix : {self.prix}"

L1= Livre("1984","george orwell" ,15.99 )
print (L1)

class eBook(livre):
    