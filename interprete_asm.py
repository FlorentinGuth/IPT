"""
Interprète un fichier assembleur.
Utilisation :
>>> from interprete_asm import *
>>> interprete('%rax <- const   42 \n print %rax')

Opérations autorisées :
 reg1  <- const     n    # stocke une constante dans le registre reg1
 reg1  <- add    reg2    # ajoute le contenu de reg2 au contenu de reg1
 reg1  <- sub    reg2    # soustrait le contenu de reg2 au contenu de reg1
 reg1  <- mul    reg2    # multiplie le contenu de reg1 par le contenu de reg2
          print  reg1    # affiche le contenu de reg1
 reg1  <- load  (reg2)   # reg1 reçoit ce qui es stocké en mémoire à l'adresse reg2
(reg1) <- store  reg2    # le contenu de reg2 est stocké en mémoire à l'adresse reg1

En théorie, on n'utilise que des entiers non signés (positifs) entre 0 et 255 (8 bits = 1 octet).
Cependant, je ne fais aucun tests et ne gère pas les débordements :
vous êtes libre de modifier le code si vous en avez besoin !
Essayez cependant de n'ajouter des opération que si vous êtes VRAIMENT
sûr que c'est impossible sans : cela fait partie de l'exercice !

Registres autorisés :
rax
rbx
rsp
rip   # Spécial : contient le numéro de ligne de la prochaine instruction,
      # incrémenté à la fin de CHAQUE instruction (même les sauts).

La mémoire est de taille 256 : si votre pile déborde, c'est probablement que
vous gérez mal une récursion quelque part ;)
"""

def interprete(instructions):
    lignes = list(filter(None, instructions.split('\n')))

    # Registres :
    registres = {
        "rax": 0,
        "rbx": 0,
        "rsp": 0,
        "rip": 0,
    }

    # Mémoire :
    memoire = [0] * 256

    # Boucle principale (on s'arrête si on sort du programme)
    while registres["rip"] < len(lignes):
        ligne = lignes[registres["rip"]]
        operandes = ligne.split()

        if len(operandes) == 2: # print est un cas à part
            operandes = ['', ''] + operandes

        # dest <- op source
        # On enlève aussi les parenthèses et le % qui ne sont pas nécessaires
        dest = operandes[0].lstrip('(%').rstrip(')')
        op = operandes[2]
        source = operandes[3].lstrip('(%').rstrip(')')

        # Décommentez ces lignes si vous voulez débugger votre programme :
        # elles sont très utiles !
        # Croyez-moi, ce n'est pas aussi simple avec du vrai assembleur qui
        # s'exécute directement sur le processeur ;)
        # print("rip", registres["rip"], "sur", operandes)
        # print(registres)
        # print(memoire)

        # Exécution de l'instruction courante
        if op == "const":
            registres[dest] = int(source)
        elif op == "add":
            registres[dest] += registres[source]
        elif op == "sub":
            registres[dest] -= registres[source]
        elif op == "mul":
            registres[dest] *= registres[source]
        elif op == "print":
            print(registres[source])
        elif op == "load":
            registres[dest] =  memoire[registres[source]]
        elif op == "store":
            memoire[registres[dest]] =  registres[source]

        registres["rip"] += 1


# Affiche joliment des instructions assembleur.
def print_asm(asm):
    lignes = list(filter(None, asm.split('\n')))
    for ligne in lignes:
        print(print_instr(ligne))

def print_instr(instr):
    operandes = instr.split()

    if len(operandes) == 2: # print est un cas à part
        operandes = ['', ''] + operandes

    dest = operandes[0]
    op = operandes[2]
    source = operandes[3]

    return print_operande(dest) + (' ' + operandes[1] + ' ').ljust(4) + op.ljust(6) + print_operande(source)

def print_operande(o):
    if len(o) > 0 and o[0] != '(':
        o = ' {} '.format(o)
    return o.rjust(6)
