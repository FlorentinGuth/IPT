"""
Ce fichier transforme une chaîne de caractères en arbre de syntaxe abstraite (AST).
Utilisation :
>>> from parser import *
>>> ast = parse('AFFICHER((3 + 2) * 6 + 12)')
>>> print_ast(ast)

Ce fichier est en réalité composée de deux parties :
- le lexer, qui transforme par exemple la chaîne de caractères ['2', ' ', '+', '7', '\n']
  en liste de tokens [('ENTIER', '2'), ('PLUS', '+'), ('ENTIER', '7')] : c'est déjà beaucoup plus maniable !
- le parser, qui transforme cette liste de tokens en arbre de syntaxe abstraite :
  par exemple, [2, +, 3, *, 4] devient :
      +
     / \
    2   *
       / \
      3   4
  (et non :
      *
     / \
    +   4
   / \
  2   3
  car l'ordre est important : le premier vaut 14 alors que le second vaut 20 !)
"""

# Lexing : transformation du fichier en liste de tokens

tokens = [
    'AFFICHER',
    'ENTIER',
    'PLUS', 'FOIS',
    'PAREN_G', 'PAREN_D',
]

# Chaque token dispose d'une regex (regular expression, ou expression régulière)
# qui définit à quoi il peut ressembler.
# Par exemple, un PLUS est un '+' tout simplement, mais un ENTIER est une
# séquence de un ou plusieurs chiffres.

t_AFFICHER = r'AFFICHER'
t_PAREN_G = r'\('
t_PAREN_D = r'\)'
t_PLUS = r'\+'
t_FOIS = r'\*'
t_ENTIER = r'\d+'

# On ignore les espaces et les tabulations
t_ignore = ' \t'

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

# On introduit des règles récursives qui permettent de transformer petit à petit
# une séquence de tokens en AST.
# Par exemple, dans 'AFFICHER(1 + 2)', on utilise la règle
# 'instruction : AFFICHER PAREN_G expression PAREN_D',
# il reste ensuite à faire correspondre '1 + 2' avec expression :
# on utilise la règle 'expression : expression PLUS expression',
# puis deux fois la règle 'expression : ENTIER' sur 1 et 2.

# Les fonctions p_expression_truc(p) prennent en entrée p, qui est plus ou moins
# une liste de tokens / asts, qui se conforme à l'un des cas décrit dans la docstring.
# Ces règles peuvent être utilisées dès que 'expression' apparaît dans la dosctring d'une règle.
# Elles doivent mettre dans p[0] l'AST correspondant à la séquence de tokens
# décrite dans la docstring, sachant que p[1] contient l'AST correspondant
# au premier token / la première règle de la séquence, p[2] la deuxième, etc...


# Associativité et priorités
# 'left' signifie que 1 + 2 + 3 devient (1 + 2) + 3, alors que 'right' donne 1 + (2 + 3).
# Pour le plus et le fois, ça ne change rien, mais (1 - 2) - 3
# (ce qui est ce que l'on attend quand on n'écrit pas de parenthèses)
# est différent de 1 - (2 - 3).
# Plus un opérateur apparaît en dessous, plus il est prioritaire : ainsi 1 + 2 * 3
# devient automatiquement 1 + (2 * 3).
# Si 2 opérateurs ou plus sont sur la même ligne, alors ils ont la même priorité
# et sont donc effectués de gauche à droite (ou de droite à gauche avec 'right') :
# 1 - 2 + 3 devient (1 - 2) + 3 et non 1 - (2 + 3).
precedence = (
    ('left', 'PLUS'),
    ('left', 'FOIS'),
)

def p_expression_entier(p):
    '''expression : ENTIER'''
    p[0] = ("ENTIER", p[1])

def p_expression_operation(p):
    '''expression : expression PLUS expression
                  | expression FOIS expression'''
    ops = {
        '+': "PLUS",
        '*': "FOIS",
    }
    p[0] = (ops[p[2]], p[1], p[3])

def p_expression_parentheses(p):
    '''expression : PAREN_G expression PAREN_D'''
    # Pas besoin de représenter les parenthèses dans l'AST !
    # En effet, elles ne servent qu'à manifester les priorités dans le code source,
    # mais on n'en n'a plus besoin dans l'AST, justement car la structure d'arbre
    # nous dit qu'il faut commencer par faire les opérations intérieures.
    p[0] = p[2]

def p_instruction_afficher(p):
    '''instruction : AFFICHER PAREN_G expression PAREN_D'''
    p[0] = ('AFFICHER', p[3])

def p_error(p):
    raise RuntimeError("Erreur de syntaxe à la ligne {} : {}".format(p.lineno, p.value))


# Construction du parser
import ply.yacc as yacc
# Si vous changez le parser et avez des erreurs, remplacez ces False par des True !
yacc.yacc(start='instruction', debug=False, write_tables=False)


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
