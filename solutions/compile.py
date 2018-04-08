"""
Compile un ast en une liste d'instructions assembleur.
Utilisation (dans une console python) :
>>> ast = ("BLOC", [...])
>>> compile_prog(ast)
ou avec le parser :
>>> compile('exemple/p1.code')

Conventions :

Il y a un saut de ligne ('\n') après chaque instruction.

On utilise le registre rsp pour la structure de pile. rsp pointe toujours sur une case libre.
La pile est toujours représentée en grandissant vers le bas ! (c'est historique, et comme beaucoup de choses
en informatique, il est trop tard pour changer !)

Après un appel de fonction, rax contient la valeur de retour.
rbp est utilisé pour accéder aux arguments dans le code d'une fonction.
(voir compile_fonction() pour le détail)
"""

import parser


# Variables : si globales, allouées tout en bas de la pile au début du programme ;
# si locales, allouées lors de l'appel de la fonction.
# L'adresse d'une variable peut être de deux formes différentes :
# - "absolue",  12 : variable globale stockée à l'adresse 12
# - "relative", -3 : variable locale stockée à l'adresse 'valeur de rbp' - 3

variables = {}  # variables["x"] contient l'addresse en mémoire de x
dans_une_fonction = False
adresse_globale_libre = 0
adresse_locale_libre = 0

def nouvelle_variable(nom):
    """Retourne une adresse libre pour la nouvelle variable"""
    global adresse_globale_libre, adresse_locale_libre

    if dans_une_fonction:
        # Variable locale
        adresse = adresse_locale_libre
        adresse_locale_libre += 1
        variables[nom] = "relative", adresse
    else :
        # Variable globale
        adresse = adresse_globale_libre
        adresse_globale_libre += 1
        variables[nom] = "absolue", adresse

    return variables[nom]

def adresse_variable(nom):
    # Crée une nouvelle variable si besoin
    if nom in variables:
        return variables[nom]
    return nouvelle_variable(nom)


# Fonctions : leur code sera entre l'allocation des variables et le point d'entrée du programme.
# On ne peut pas placer les fonctions tout en haut, on ne commence pas par les exécuter !
# On ne peut pas non plus les placer tout en bas simplement, car on ne connaît pas encore leur adresse :
# quelle est la taille du code que l'on n'a pas encore compilé ?
# On les met donc presque tout en haut, on ajoutera à la fin au tout début du programme 3 instructions qui permettent
# de tout mettre en place et sauter bien plus bas, là où le 'vrai programme' commence.
# Le code ressemble donc à :
# setup 1 (alloue variables globales)
# setup 2 (alloue variables globales)
# saute fonctions --|
# ... fonction 1    |
# ...               |
# ... fonction n    |
# vrai programme <---
# vrai programme
# (appel de fonction 3)
# ...

fonctions = {}  # fonctions["f"] contient l'adresse du code de f
code_fonctions = ""  # contient le code de toutes les fonctions dans l'ordre
adresse_fonction_libre = 3  # instructions 0 et 1 pour allouer les variables, 2 pour sauter au point d'entrée

def nouvelle_fonction(nom, code):
    global adresse_fonction_libre, code_fonctions

    adresse = adresse_fonction_libre
    fonctions[nom] = adresse

    adresse_fonction_libre += code.count('\n') # La prochaine fonction sera située après celle-ci
    code_fonctions += code


# Fonctions auxiliaires pour gérer la pile.
# Attention : elles modifient le registre rcx ! Evitez de l'utiliser quand vous devez manipuler la pile !

def empile(reg):
    return "(rsp) <- store {}\n".format(reg) + "rcx <- const 1\n" + "rsp <- add rcx\n"

def depile(reg):
    return "rcx <- const 1\n" + "rsp <- sub rcx\n" + "{} <- load (rsp)\n".format(reg)



def compile_ast(ast):
    """
    Décode la structure de l'AST en fonction du premier symbole.
    Chaque type de noeud différent est ensuite compilé dans sa propre fonction.
    Si vous ajoutez une nouvelle construction à l'AST, par exemple ("DIVISER", a, b) pour a / b, vous avez deux choses à faire :
    - rajouter un cas à cette longue liste conditions:
      ```
      elif type == "DIVISION":
          return compile_division(ast[1], ast[2]) # compile_division(a, b)
      ```
    - rajouter la fonction `compile_division(a, b)` :
      gardez à l'esprit que ici `a` et `b` peuvent être n'importe quelle expression et pas seulement des entiers !
      Il faut les compiler en appelant `compile_ast` (cela devrait être la seule fonction que vous appelez dans `compile_division`)
    """
    type = ast[0]
    if type == "AFFICHER":
        return compile_afficher(ast[1])
    elif type == "PLUS":
        return compile_plus(ast[1], ast[2])
    elif type == "MOINS":
        return compile_moins(ast[1], ast[2])
    elif type == "FOIS":
        return compile_fois(ast[1], ast[2])
    elif type == "ENTIER":
        return compile_entier(ast[1])
    elif type == "BLOC":
        return compile_bloc(ast[1])
    elif type == "AFFECTATION":
        return compile_affectation(ast[1], ast[2])
    elif type == "VARIABLE":
        return compile_variable(ast[1])
    elif type == "CONDITION":
        return compile_condition(ast[1], ast[2])
    elif type == "EGALE":
        return compile_egale(ast[1], ast[2])
    elif type == "FONCTION":
        return compile_fonction(ast[1], ast[2], ast[3])
    elif type == "RENVOYER":
        return compile_renvoyer(ast[1])
    elif type == "APPEL":
        return compile_appel(ast[1], ast[2])


def compile_afficher(ast):
    return compile_ast(ast) + depile("rax") + "print rax\n"

def compile_plus(ast1, ast2):
    return compile_ast(ast1) + compile_ast(ast2) + depile("rax") + depile("rbx") + "rax <- add rbx\n" + empile("rax")

def compile_moins(ast1, ast2):
    # Attention à l'ordre ici ! a - b est différent de b - a !
    # ast1 est compilé est empilé en premier, donc il est dépilé en dernier !
    # Avec la pile qui grandit vers le bas, cela donne (rsp est représenté par une étoile *) :
    #
    # 0: rien*  ->  ast1   ->  ast1  ->  ast1             ->  ast1* (dans rbx)
    # 1: rien       rien*      ast2      ast2* (dans rax)     ast2  (dans rax)
    # 2: rien       rien       rien*                          rien
    return compile_ast(ast1) + compile_ast(ast2) + depile("rax") + depile("rbx") + "rbx <- sub rax\n" + empile("rbx")

def compile_fois(ast1, ast2):
    return compile_ast(ast1) + compile_ast(ast2) + depile("rax") + depile("rbx") + "rax <- mul rbx\n" + empile("rax")

def compile_entier(n):
    return "rax <- const {}\n".format(n) + empile("rax")

def compile_bloc(asts):
    prog = ""
    for ast in asts:
        prog += compile_ast(ast)
    return prog

def compile_affectation(var, ast):
    type, adr = adresse_variable(var)

    val_dans_rax = compile_ast(ast) + depile("rax")

    adr_dans_rbx = "rbx <- const {}\n".format(adr)
    if type == "relative":
        # L'adresse est par rapport à rbp, il faut donc l'ajouter pour obtenir la vraie adresse.
        adr_dans_rbx += "rbx <- add rbp\n"

    return val_dans_rax + adr_dans_rbx + "(rbx) <- store rax\n"

def compile_variable(var):
    # Ici var doit déjà être définie. Sinon, cela va planter !
    type, adr = variables[var]

    adr_dans_rbx = "rbx <- const {}\n".format(adr)
    if type == "relative":
        adr_dans_rbx += "rbx <- add rbp\n"

    return adr_dans_rbx + "rax <- load (rbx)\n" + empile("rax")

def compile_condition(si, alors):
    code_si = compile_ast(si)
    code_alors = compile_ast(alors)
    # Si la condition est fausse (elle est évaluée en quelque chose différent de 0 -- je suis d'accord que j'ai pris
    # le parti d'une convention étrange, mais dans le cas particulier du test d'égalité cela simplifie les choses),
    # alors on saute le code du ALORS en modifiant le registre rip.
    # Attention : même après avoir modifié rip, il est toujours incrémenté entre chaque instruction !
    return code_si + depile("rax") + "rbx <- const {}\n".format(code_alors.count('\n')) + "rax <- addinz rbx\n" + code_alors

def compile_egale(ast1, ast2):
    # a = b si et seulement si a - b = 0
    # La convention choisie pour la condition du SI nous simplifie la vie !
    return compile_ast(ast1) + compile_ast(ast2) + depile("rax") + depile("rbx") + "rax <- sub rbx\n" + empile("rax")

def compile_fonction(nom, args, code):
    global dans_une_fonction, adresse_locale_libre, variables
    """
    Etat de la pile (le plus ancien en bas, le plus récent en haut), n'importe quand dans le corps de la fonction :
    
    ###
    trucs appartenant à l'appelant
    ###
    argument 1
    .
    .
    argument n
    adresse de retour
    ancien rbp
    variable locale 1  <--- rbp
    .
    .
    variable locale p
    ###
    résultats intermédiaires
    ###
    
    Cet espace libre va bientôt être rempli par des résultats intermédiaires, et rsp va être modifié,
    ce qui explique pourquoi on a besoin de le sauvegarder maintenant pour pouvoir retrouver les arguments.
    """

    # Avant toute chose, on sauvegarde l'ancien rbp, puisqu'on s'apprête à le modifier.
    empile_rbp = empile("rbp")

    # Ensuite on sauvegarde rsp dans rbp.
    sauvegarde_rsp = "rbp <- copy rsp\n"

    # Avant de compiler le corps de la fonction, on rajoute les arguments dans l'environnement,
    # et on enregistre qu'on est dans une fonction (car alors les nouvelles variables sont locales à la fonction).
    dans_une_fonction = True
    variables_copie = variables.copy()
    adr_arg = -2 - len(args) # le premier argument est tout en bas !
    for arg in args:
        variables[arg] = "relative", adr_arg
        adr_arg += 1
    # La prochaine adresse locale libre pour une nouvelle variable est donc à rbp pile
    adresse_locale_libre = 0
    # On se souvient du nombre de variables pour savoir combien il y en a de nouvelles (locales).
    num_variables = len(variables)
    # Enfin, on rajoute la fonction en cours dans l'environnement en cas de récursivité
    fonctions[nom] = adresse_fonction_libre

    corps = compile_ast(code)

    # Lorsque quelqu'un devra exécuter la fonction, il devra allouer de l'espace sur sa pile pour les variables locales.
    # Combien y en a-t-il ? Ce sont les variables qui n'étaient pas là avant de compiler le corps de la fonction !
    alloue_locales = "rax <- const {}\n".format(len(variables) - num_variables) + "rsp <- add rax\n"

    # On restaure l'environnement.
    dans_une_fonction = False
    variables = variables_copie

    code_final = empile_rbp + sauvegarde_rsp + alloue_locales + corps
    # On ne rajoute rien après, on fait confiance à l'utilisateur pour avoir écrit un RENVOYER à la fin !

    nouvelle_fonction(nom, code_final)

    # Pas de code à exécuter pour la déclaration ! Il sera rajouté en haut du code à la fin.
    return ""

def compile_renvoyer(ast):
    # On copie la valeur de retour dans rax
    retour_rax = compile_ast(ast) + depile("rax")

    # On enlève tout ce qui peut traîner sur la pile (variables locales éventuelles).
    restaure_pile = "rsp <- copy rbp\n"

    # Ensuite on restaure le rbp de l'appelant
    restaure_rbp = depile("rbp")

    # Il ne reste plus qu'à depiler l'adresse de retour dans rip !
    retour = depile("rip")

    return retour_rax + restaure_pile + restaure_rbp + retour

def compile_appel(nom, args):
    empile_args = ""
    for arg in args:
        empile_args += compile_ast(arg)

    # Ici on fait un petit calcul avec rip pour connaître la bonne adresse de retour :
    # en effet, on sauvegarde rip avant de sauter dans la fonction, mais on quand on le
    # restaure depuis la fonction appelée on ne veut pas exécuter une deuxième fois le saut
    # vers la fonction appelée !

    # Cependant, une amélioration est possible : si vous réfléchissez bien, on n'a pas besoin de lire
    # la valeur de rip car on peut la connaître statiquement (c'est-à-dire, au moment de la compilation,
    # par opposition à dynamiquement, qui signifie au moment de l'exécution). En effet, on sait que rip
    # commence à 0 : il suffit donc de connaître la taille du code qui est placé avant ! On peut donc
    # simplifier cette addition en:

    # ligne 45: load rax <- 48   (bonne adresse calculée au moment de la compilation, attention au rip += 1 qui sera exécuté !)
    # ligne 46: empile rax  (attention cela prend 3 lignes et non une seule !)
    # ligne 46: empile rax
    # ligne 47: empile rax
    # ligne 48: saut vers la fonction, qui va dépiler 48 et faire rip <- 48 ; après incrémentation, on se retrouve bien ligne 49 !
    # ligne 49: ici la fonction a été exécutée

    # A vous de jouer !

    empile_adresse_de_retour = (
        "rax <- copy rip\n" # rax pointe sur cette instruction
      + "rbx <- const 7\n"  # Constante magique qui représente le nombre d'instructions à sauter
      + "rax <- add rbx\n"  # rax pointe sur l'instruction de l'appel : OK !
      + empile("rax")       # 3 instructions
    )

    adr = fonctions[nom]
    appel = "rax <- const {}\n".format(adr - 1) + "rip <- copy rax\n"

    # On n'oublie pas de dépiler les arguments !
    depile_args = "rbx <- const {}\n".format(len(args)) + "rsp <- sub rbx\n"

    # Ni d'empiler la valeur de retour !
    empile_retour = empile("rax")

    return empile_args + empile_adresse_de_retour + appel + depile_args + empile_retour


def compile(ast):
    """
    Cette fonction se charge de compiler le programme entier : c'est-à-dire, elle rajoute le code
    qui alloue la place pour les variables, ainsi que le code de déclaration des fonctions.
    """
    code = compile_ast(ast)

    alloue_variables = "rax <- const {}\n".format(len(variables)) + "rsp <- add rax\n"
    saut = "rip <- const {}\n".format(adresse_fonction_libre - 1) # - 1 car rip est incrémenté à la fin du 'const' !

    return alloue_variables + saut + code_fonctions + code
