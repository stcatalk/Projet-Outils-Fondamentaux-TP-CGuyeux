import math
import random
import matplotlib.pyplot as plt


# ============================================================
#  STRONGHOLD FINDER - MINECRAFT
# ============================================================
#
# Le programme estime la position d'un stronghold à partir
# de plusieurs lancers d'Œil de l'Ender.
#
# Pour chaque lancer, on connaît :
#   - X : position du joueur
#   - Z : position du joueur
#   - yaw : orientation Minecraft au moment du lancer
#
# Minecraft :
#   yaw = 0°   -> direction +Z
#   yaw = 90°  -> direction -X
#   yaw = 180° -> direction -Z
#   yaw = 270° -> direction +X
#
# Le programme transforme chaque lancer en une droite,
# puis cherche le point qui correspond le mieux à toutes
# les droites.
# ============================================================


# ------------------------------------------------------------
# CONSTANTES
# ------------------------------------------------------------

EPSILON = 1e-10


# ------------------------------------------------------------
# CONVERSION YAW -> VECTEUR DE DIRECTION
# ------------------------------------------------------------

def direction_depuis_yaw(yaw):
    """
    Convertit un yaw Minecraft en vecteur de direction.

    Dans Minecraft :
        X = -sin(yaw)
        Z =  cos(yaw)

    Retourne :
        dx, dz
    """

    angle = math.radians(yaw)

    dx = -math.sin(angle)
    dz = math.cos(angle)

    return dx, dz


# ------------------------------------------------------------
# CREATION D'UNE TRAJECTOIRE
# ------------------------------------------------------------

def creer_trajectoire(x, z, yaw):
    """
    Crée une trajectoire à partir d'une position et d'un yaw.

    Une trajectoire est représentée par :

        P(t) = P0 + t * d

    avec :
        P0 = position du joueur
        d  = vecteur de direction
    """

    dx, dz = direction_depuis_yaw(yaw)

    return {
        "x": x,
        "z": z,
        "yaw": yaw,
        "dx": dx,
        "dz": dz
    }


# ------------------------------------------------------------
# INTERSECTION DE DEUX TRAJECTOIRES
# ------------------------------------------------------------

def intersection_deux_trajectoires(ligne1, ligne2):
    """
    Calcule l'intersection de deux droites.

    Retourne :
        (x, z)
    ou :
        None si les droites sont parallèles.
    """

    x1 = ligne1["x"]
    z1 = ligne1["z"]
    dx1 = ligne1["dx"]
    dz1 = ligne1["dz"]

    x2 = ligne2["x"]
    z2 = ligne2["z"]
    dx2 = ligne2["dx"]
    dz2 = ligne2["dz"]

    determinant = dx1 * dz2 - dz1 * dx2

    # Les droites sont parallèles
    if abs(determinant) < EPSILON:
        return None

    difference_x = x2 - x1
    difference_z = z2 - z1

    t = (
        difference_x * dz2
        - difference_z * dx2
    ) / determinant

    x = x1 + t * dx1
    z = z1 + t * dz1

    return x, z


# ------------------------------------------------------------
# DISTANCE D'UN POINT A UNE TRAJECTOIRE
# ------------------------------------------------------------

def distance_point_trajectoire(x, z, trajectoire):
    """
    Calcule la distance entre un point et une trajectoire.

    On utilise le produit vectoriel en 2 dimensions.
    """

    x0 = trajectoire["x"]
    z0 = trajectoire["z"]

    dx = trajectoire["dx"]
    dz = trajectoire["dz"]

    vx = x - x0
    vz = z - z0

    distance = abs(vx * dz - vz * dx)

    return distance


# ------------------------------------------------------------
# ANGLE ENTRE DEUX TRAJECTOIRES
# ------------------------------------------------------------

def angle_entre_trajectoires(ligne1, ligne2):
    """
    Calcule l'angle aigu entre deux trajectoires.
    """

    dx1 = ligne1["dx"]
    dz1 = ligne1["dz"]

    dx2 = ligne2["dx"]
    dz2 = ligne2["dz"]

    produit_scalaire = dx1 * dx2 + dz1 * dz2

    norme1 = math.sqrt(dx1 ** 2 + dz1 ** 2)
    norme2 = math.sqrt(dx2 ** 2 + dz2 ** 2)

    cos_angle = produit_scalaire / (norme1 * norme2)

    # Évite les problèmes numériques avec acos
    cos_angle = max(-1, min(1, abs(cos_angle)))

    angle = math.degrees(math.acos(cos_angle))

    return angle


# ------------------------------------------------------------
# ESTIMATION PAR MOINDRES CARRES
# ------------------------------------------------------------

def estimation_moindres_carres(lancers):
    """
    Estime la position du stronghold avec plusieurs lancers.

    Chaque trajectoire est une droite :

        a*x + b*z = c

    On cherche le point (x, z) qui minimise la somme
    des carrés des distances aux différentes droites.

    Cette méthode est particulièrement intéressante lorsque
    les observations comportent des erreurs.
    """

    somme_a2 = 0
    somme_ab = 0
    somme_b2 = 0

    somme_ac = 0
    somme_bc = 0

    for lancer in lancers:

        x0 = lancer["x"]
        z0 = lancer["z"]

        dx = lancer["dx"]
        dz = lancer["dz"]

        # Vecteur normal à la trajectoire
        a = -dz
        b = dx

        # Equation :
        # a*x + b*z = c

        c = a * x0 + b * z0

        somme_a2 += a * a
        somme_ab += a * b
        somme_b2 += b * b

        somme_ac += a * c
        somme_bc += b * c

    determinant = (
        somme_a2 * somme_b2
        - somme_ab ** 2
    )

    if abs(determinant) < EPSILON:
        return None

    x = (
        somme_ac * somme_b2
        - somme_bc * somme_ab
    ) / determinant

    z = (
        somme_a2 * somme_bc
        - somme_ab * somme_ac
    ) / determinant

    return x, z


# ------------------------------------------------------------
# CALCUL DES ERREURS
# ------------------------------------------------------------

def calculer_erreurs(position, lancers):
    """
    Calcule l'erreur entre la position estimée et chaque lancer.
    """

    x, z = position

    erreurs = []

    for lancer in lancers:
        erreur = distance_point_trajectoire(
            x,
            z,
            lancer
        )

        erreurs.append(erreur)

    return erreurs


# ------------------------------------------------------------
# QUALITE DE L'ESTIMATION
# ------------------------------------------------------------

def evaluer_estimation(position, lancers):
    """
    Donne plusieurs statistiques sur l'estimation.
    """

    erreurs = calculer_erreurs(position, lancers)

    erreur_moyenne = sum(erreurs) / len(erreurs)

    erreur_max = max(erreurs)

    erreur_rms = math.sqrt(
        sum(e ** 2 for e in erreurs)
        / len(erreurs)
    )

    return erreur_moyenne, erreur_max, erreur_rms


# ------------------------------------------------------------
# AFFICHAGE DES RESULTATS
# ------------------------------------------------------------

def afficher_resultats(position, lancers):
    """
    Affiche les résultats de l'estimation.
    """

    print()
    print("=" * 60)
    print("RESULTAT")
    print("=" * 60)

    if position is None:
        print("Impossible de déterminer le stronghold.")
        print()
        print(
            "Les trajectoires sont probablement trop proches "
            "du parallélisme."
        )
        return

    x, z = position

    print()
    print(f"Position estimée du stronghold :")
    print(f"    X = {x:.2f}")
    print(f"    Z = {z:.2f}")

    print()
    print("Coordonnées Minecraft arrondies :")
    print(f"    X = {round(x)}")
    print(f"    Z = {round(z)}")

    erreur_moyenne, erreur_max, erreur_rms = (
        evaluer_estimation(position, lancers)
    )

    print()
    print("Précision de l'estimation :")
    print(f"    Erreur moyenne : {erreur_moyenne:.2f} blocs")
    print(f"    Erreur maximale : {erreur_max:.2f} blocs")
    print(f"    Erreur RMS : {erreur_rms:.2f} blocs")

    print()
    print("Erreur de chaque lancer :")

    for i, erreur in enumerate(
        calculer_erreurs(position, lancers),
        start=1
    ):
        print(
            f"    Lancer {i} : {erreur:.2f} blocs"
        )


# ------------------------------------------------------------
# VERIFICATION DES TRAJECTOIRES
# ------------------------------------------------------------

def analyser_geometrie(lancers):
    """
    Analyse les angles entre les trajectoires.

    Deux trajectoires presque parallèles donnent généralement
    une estimation beaucoup moins stable.
    """

    print()
    print("=" * 60)
    print("ANALYSE GEOMETRIQUE")
    print("=" * 60)

    meilleur_angle = 0

    for i in range(len(lancers)):
        for j in range(i + 1, len(lancers)):

            angle = angle_entre_trajectoires(
                lancers[i],
                lancers[j]
            )

            print(
                f"Trajectoires {i + 1} / {j + 1} : "
                f"{angle:.2f}°"
            )

            meilleur_angle = max(
                meilleur_angle,
                angle
            )

    if meilleur_angle < 10:
        print()
        print(
            "ATTENTION : les trajectoires sont presque "
            "parallèles."
        )

    elif meilleur_angle < 30:
        print()
        print(
            "Les trajectoires sont relativement proches "
            "du parallélisme."
        )

    else:
        print()
        print(
            "La géométrie des lancers est favorable."
        )


# ------------------------------------------------------------
# AFFICHAGE GRAPHIQUE
# ------------------------------------------------------------

def afficher_graphique(lancers, position):
    """
    Affiche les trajectoires et la position estimée.
    """

    if position is None:
        return

    x_estime, z_estime = position

    plt.figure(figsize=(10, 8))

    # Taille de la zone graphique
    points_x = [lancer["x"] for lancer in lancers]
    points_z = [lancer["z"] for lancer in lancers]

    tous_x = points_x + [x_estime]
    tous_z = points_z + [z_estime]

    largeur = max(
        max(tous_x) - min(tous_x),
        max(tous_z) - min(tous_z),
        100
    )

    centre_x = (max(tous_x) + min(tous_x)) / 2
    centre_z = (max(tous_z) + min(tous_z)) / 2

    marge = largeur * 0.7

    xmin = centre_x - marge
    xmax = centre_x + marge

    zmin = centre_z - marge
    zmax = centre_z + marge

    longueur = largeur * 2

    # Dessin des trajectoires
    for i, lancer in enumerate(lancers):

        x0 = lancer["x"]
        z0 = lancer["z"]

        dx = lancer["dx"]
        dz = lancer["dz"]

        # On trace une longue portion de la droite
        x1 = x0 - dx * longueur
        z1 = z0 - dz * longueur

        x2 = x0 + dx * longueur
        z2 = z0 + dz * longueur

        plt.plot(
            [x1, x2],
            [z1, z2],
            label=f"Lancer {i + 1}"
        )

        plt.scatter(
            x0,
            z0,
            s=50
        )

        plt.text(
            x0,
            z0,
            f"  Joueur {i + 1}"
        )

    # Position estimée
    plt.scatter(
        x_estime,
        z_estime,
        marker="*",
        s=300,
        label="Stronghold estimé"
    )

    plt.text(
        x_estime,
        z_estime,
        f"  Stronghold\n  ({x_estime:.1f}, {z_estime:.1f})"
    )

    plt.xlim(xmin, xmax)
    plt.ylim(zmin, zmax)

    plt.xlabel("X")
    plt.ylabel("Z")

    plt.title(
        "Estimation de la position du Stronghold"
    )

    plt.grid(True)
    plt.legend()

    # Même échelle sur X et Z
    plt.axis("equal")

    plt.show()


# ------------------------------------------------------------
# SIMULATION D'ERREUR
# ------------------------------------------------------------

def simuler_erreur(lancers, position_reelle, erreur_angle):
    """
    Simule une erreur sur les angles.

    Cette fonction permet d'étudier l'influence d'une erreur
    de mesure sur la position estimée.
    """

    nouveaux_lancers = []

    for lancer in lancers:

        angle_erreur = random.uniform(
            -erreur_angle,
            erreur_angle
        )

        nouveau_yaw = (
            lancer["yaw"] + angle_erreur
        )

        nouveau_lancer = creer_trajectoire(
            lancer["x"],
            lancer["z"],
            nouveau_yaw
        )

        nouveaux_lancers.append(
            nouveau_lancer
        )

    nouvelle_position = (
        estimation_moindres_carres(
            nouveaux_lancers
        )
    )

    if nouvelle_position is None:
        return None

    x1, z1 = nouvelle_position
    x2, z2 = position_reelle

    erreur = math.sqrt(
        (x1 - x2) ** 2
        + (z1 - z2) ** 2
    )

    return erreur


# ------------------------------------------------------------
# ETUDE DE PRECISION
# ------------------------------------------------------------

def etude_precision(lancers, position_reelle):
    """
    Effectue une expérience numérique.

    On ajoute différentes erreurs aux angles et on mesure
    l'erreur finale sur la position du stronghold.
    """

    print()
    print("=" * 60)
    print("ETUDE DE PRECISION")
    print("=" * 60)

    erreurs_angles = [
        0.1,
        0.5,
        1.0,
        2.0,
        5.0
    ]

    nombre_essais = 100

    for erreur_angle in erreurs_angles:

        erreurs = []

        for _ in range(nombre_essais):

            erreur = simuler_erreur(
                lancers,
                position_reelle,
                erreur_angle
            )

            if erreur is not None:
                erreurs.append(erreur)

        if erreurs:

            moyenne = (
                sum(erreurs)
                / len(erreurs)
            )

            maximum = max(erreurs)

            print()
            print(
                f"Erreur angulaire ±{erreur_angle}° :"
            )

            print(
                f"    Erreur moyenne : "
                f"{moyenne:.2f} blocs"
            )

            print(
                f"    Pire erreur : "
                f"{maximum:.2f} blocs"
            )


# ------------------------------------------------------------
# SAISIE D'UN LANCER
# ------------------------------------------------------------

def demander_lancer(numero):
    """
    Demande les informations d'un lancer à l'utilisateur.
    """

    print()
    print(f"--- LANCER {numero} ---")

    while True:
        try:
            x = float(
                input("Position X du joueur : ")
            )

            z = float(
                input("Position Z du joueur : ")
            )

            yaw = float(
                input("Yaw Minecraft (en degrés) : ")
            )

            break

        except ValueError:
            print(
                "Erreur : entre une valeur numérique."
            )

    return creer_trajectoire(
        x,
        z,
        yaw
    )


# ------------------------------------------------------------
# PROGRAMME PRINCIPAL
# ------------------------------------------------------------

def main():

    print()
    print("=" * 60)
    print("       MINECRAFT - STRONGHOLD FINDER")
    print("=" * 60)

    print()
    print(
        "Ce programme estime la position d'un stronghold"
    )
    print(
        "à partir de plusieurs lancers d'Œil de l'Ender."
    )

    print()
    print("Convention du yaw Minecraft :")
    print("    0°   -> +Z")
    print("    90°  -> -X")
    print("    180° -> -Z")
    print("    270° -> +X")

    print()

    # --------------------------------------------------------
    # Nombre de lancers
    # --------------------------------------------------------

    while True:

        try:
            nombre = int(
                input("Nombre de lancers (minimum 2) : ")
            )

            if nombre >= 2:
                break

            print(
                "Il faut au moins deux lancers."
            )

        except ValueError:
            print(
                "Entre un nombre entier."
            )

    # --------------------------------------------------------
    # Saisie des lancers
    # --------------------------------------------------------

    lancers = []

    for i in range(nombre):

        lancer = demander_lancer(i + 1)

        lancers.append(lancer)

    # --------------------------------------------------------
    # Affichage des données
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("DONNEES")
    print("=" * 60)

    for i, lancer in enumerate(
        lancers,
        start=1
    ):

        print(
            f"Lancer {i} : "
            f"X={lancer['x']:.2f}, "
            f"Z={lancer['z']:.2f}, "
            f"yaw={lancer['yaw']:.2f}°"
        )

    # --------------------------------------------------------
    # Cas de deux lancers
    # --------------------------------------------------------

    if len(lancers) == 2:

        print()
        print("=" * 60)
        print("INTERSECTION DES DEUX TRAJECTOIRES")
        print("=" * 60)

        position_intersection = (
            intersection_deux_trajectoires(
                lancers[0],
                lancers[1]
            )
        )

        if position_intersection is None:

            print(
                "Les deux trajectoires sont parallèles."
            )

        else:

            x, z = position_intersection

            print(
                f"X = {x:.2f}"
            )

            print(
                f"Z = {z:.2f}"
            )

    # --------------------------------------------------------
    # Estimation générale
    # --------------------------------------------------------

    position_estimee = (
        estimation_moindres_carres(
            lancers
        )
    )

    afficher_resultats(
        position_estimee,
        lancers
    )

    # --------------------------------------------------------
    # Analyse géométrique
    # --------------------------------------------------------

    analyser_geometrie(
        lancers
    )

    # --------------------------------------------------------
    # Graphique
    # --------------------------------------------------------

    print()
    choix = input(
        "Afficher le graphique ? (o/n) : "
    ).lower()

    if choix == "o":

        afficher_graphique(
            lancers,
            position_estimee
        )

    # --------------------------------------------------------
    # Simulation
    # --------------------------------------------------------

    print()

    choix = input(
        "Faire une étude de précision ? (o/n) : "
    ).lower()

    if choix == "o":

        if position_estimee is not None:

            print()
            print(
                "Pour la simulation, on considère"
            )

            print(
                "la position calculée comme position réelle."
            )

            etude_precision(
                lancers,
                position_estimee
            )

        else:

            print(
                "Impossible de réaliser la simulation."
            )

    print()
    print("=" * 60)
    print("FIN DU PROGRAMME")
    print("=" * 60)


# ------------------------------------------------------------
# LANCEMENT
# ------------------------------------------------------------

if __name__ == "__main__":
    main()
