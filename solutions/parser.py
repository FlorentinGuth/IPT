r"""
Ce fichier transforme une chaîne de caractères en arbre de syntaxe abstraite (AST).
Il est en réalité composée de deux parties :
- le lexer, qui transforme par exemple la chaîne de caractères ['a', ' ', '+', 'b', '\n']
  en liste de tokens [("IDENT", "a"), ("PLUS", '+'), ("IDENT", b)] : c'est déjà beaucoup plus maniable !
- le parser, qui transforme cette liste de tokens en arbre de syntaxe abstraite : par exemple,
  [2, +, 3, *, 4] devient    +     (et non    *   , car l'ordre est important : le premier vaut 14 alors que le second vaut 20 !)
                            / \              / \
                           2   *            +   4
                              / \          / \
                             3   4        2   3

Utilisation:
>>> import parser
>>> ast = parser.parse(chaine)
"""

# Lexing : transformation du fichier en liste de tokens

# Mot-clés réservés (ils ne peuvent pas être utilisés comme nom de variable ou de fonction)
reserves = ['AFFICHER', 'SI', 'ALORS', 'FIN', 'FONCTION', 'RENVOYER']
tokens = [
    'PAREN_G', 'PAREN_D',
    'PLUS', 'MOINS', 'FOIS',
    'ENTIER', 'IDENT',
    'EGALE',
    'VIRGULE',
] + reserves

# Chaque token dispose d'une regex (regular expression, ou expression régulière) qui définit à quoi il peut ressembler.
# Par exemple, un PLUS est un '+' tout simplement, mais un ENTIER est une séquence de un ou plusieurs chiffres.

t_PAREN_G = r'\('
t_PAREN_D = r'\)'
t_PLUS = r'\+'
t_MOINS = r'-'
t_FOIS = r'\*'
t_ENTIER = r'\d+'
def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Un identifieur peut-être en fait un mot-clé : dans ce cas, on le remplace par le bon token
    t.type = t.value if t.value in reserves else "IDENT"
    return t
t_EGALE = r'='
t_VIRGULE = r','

t_ignore = ' \t' # On ignore les espaces et les tabulations

# Ceci sert uniquement à indiquer les numéros de lignes lors des erreurs.
def t_newline(t):
    r'\n'
    t.lexer.lineno += 1

def t_error(t):
    raise RuntimeError("Caractère invalide à la ligne {}: {}".format(t.lexer.lineno, t.value[0]))

# Construction du lexer
import ply.lex as lex
lex.lex()


# Parsing : transformation de la liste de tokens en AST

# On introduit des règles récursives qui permettent de transformer petit à petit une séquence de tokens en AST.
# Par exemple, dans 'AFFICHER(1 + 2)', on utilise la règle 'instruction : AFFICHER PAREN_G expression PAREN_D',
# il reste ensuite à faire correspondre '1 + 2' avec expression : on utilise la règle 'expression : expression PLUS expression',
# puis deux fois la règle 'expression : ENTIER' sur 1 et 2.

# Les fonctions p_expression_truc(p) prennent en entrée p, plus ou moins une liste de tokens / asts, qui se conforme
# à l'un des cas décrit dans la docstring. Ces règles peuvent être utilisées dès que 'expression' apparaît dans la
# dosctring d'une règle.
# Elles doivent mettre dans p[0] l'AST correspondant à la séquence de tokens décrite dans la docstring, sachant que
# p[1] contient l'AST correspondant au premier token / la première règle de la séquence, p[2] la deuxième, etc...


# Associativité et priorités
# 'left' signifie que 1 + 2 + 3 devient (1 + 2) + 3, alors que 'right' donne 1 + (2 + 3)
# Pour le plus et le fois, ça ne change rien, mais (1 - 2) - 3 (ce qui est ce que l'on attend quand on n'écrit pas
# de parenthèses) est différent de 1 - (2 - 3)
# Plus un opérateur apparaît en dessous, plus il est prioritaire : ainsi 1 + 2 * 3 devient automatiquement 1 + (2 * 3)
# Si 2 opérateurs ou plus sont sur la même ligne, alors ils ont la même priorité et sont donc effectués de gauche à
# droite (ou sans doute de droite à gauche avec 'right') : 1 - 2 + 3 est (1 - 2) + 3 et non 1 - (2 + 3).
precedence = (
    ('left', 'PLUS', 'MOINS'),
    ('left', 'FOIS'),
)

def p_expression_entier(p):
    '''expression : ENTIER'''
    p[0] = ("ENTIER", p[1])

def p_expression_operation(p):
    '''expression : expression PLUS expression
                  | expression MOINS expression
                  | expression FOIS expression'''
    ops = {
        '+': "PLUS",
        '-': "MOINS",
        '*': "FOIS",
    }
    p[0] = (ops[p[2]], p[1], p[3])

def p_expression_parentheses(p):
    '''expression : PAREN_G expression PAREN_D'''
    # Pas besoin de représenter les parenthèses dans l'AST !
    # En effet, elles ne servent qu'à manifester les priorités dans le code source, mais on n'en n'a plus besoin dans l'AST,
    # justement car la structure d'arbre nous dit qu'il faut commencer par faire les opérations intérieures.
    p[0] = p[2]

def p_instruction_afficher(p):
    '''instruction : AFFICHER PAREN_G expression PAREN_D'''
    p[0] = ('AFFICHER', p[3])

def p_instruction_affectation(p):
    '''instruction : IDENT EGALE expression'''
    p[0] = ("AFFECTATION", p[1], p[3])

# Ne reconnaît rien : utile pour les fonctions sans arguments.
def p_vide(p):
    '''vide : '''
    pass

def p_bloc(p):
    '''bloc : vide
            | bloc instruction'''
    if len(p) == 2:
        p[0] = ("BLOC", [])
    else:
        p[0] = ("BLOC", p[1][1] + [p[2]])

def p_expression_variable(p):
    '''expression : IDENT'''
    p[0] = ("VARIABLE", p[1])

def p_expression_condition(p):
    '''instruction : SI test ALORS bloc FIN'''
    p[0] = ("CONDITION", p[2], p[4])

def p_test(p):
    '''test : expression EGALE expression'''
    p[0] = ("EGALE", p[1], p[3])

def p_instruction_fonction(p):
    '''instruction : FONCTION IDENT PAREN_G parametres PAREN_D bloc FIN'''
    p[0] = ("FONCTION", p[2], p[4], p[6])

def p_parametres(p):
    '''parametres : vide
                  | IDENT
                  | parametres VIRGULE IDENT'''
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_instruction_renvoyer(p):
    '''instruction : RENVOYER expression'''
    p[0] = ("RENVOYER", p[2])

def p_expression_appel(p):
    '''expression : IDENT PAREN_G arguments PAREN_D'''
    p[0] = ("APPEL", p[1], p[3])

def p_arguments(p):
    '''arguments : vide
                 | expression
                 | arguments VIRGULE expression'''
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_error(p):
    raise RuntimeError("Erreur de syntaxe à la ligne {} : {}".format(p.lineno, p.value))


# Construction du parser
import ply.yacc as yacc
yacc.yacc(start='bloc', debug=False, write_tables=False) # Si vous changez le parser et avez des erreurs, remplacez ces False par True !


def parse(s):
    return yacc.parse(s, tracking=True)

# Affiche joliment un arbre de syntaxe abstraite.
def print_ast(ast):
    print(print_ast_aux(ast, 0).rstrip(',\n'))

def print_ast_aux(ast, indent):
    ind = ''.join(['  '] * indent)
    if type(ast) == str:
        return ind + "'" + ast + "'" + ",\n"
    if type(ast) == tuple:
        p = '(', ')'
    elif type(ast) == list:
        p = '[', ']'
    s = ""
    first = True
    for a in ast:
        t = print_ast_aux(a, indent+1)
        if first:
            first = False
            t = ind + p[0] + t.lstrip(' ')
        s += t
    return s.rstrip(',\n') + p[1] + ',\n'
