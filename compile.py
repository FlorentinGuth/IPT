'''
Compile un ast en une liste d'instructions assembleur.
Utilisation :
>>> from compile import *
>>> ast = ('AFFICHER', ('PLUS', ('ENTIER', '19'), ('ENTIER', '23')))
>>> asm = compile(ast)
(vous pouvez aller jeter un coup d'oeil du côté de parser.py pour obtenir l'AST)

Conventions :

On utilise le registre rsp pour la structure de pile.
rsp pointe toujours sur une case libre.
'''


def compile(ast):
    '''
    Cette fonction renvoie une chaîne de caractères qui est une suite
    d'instructions assembleur correspondant à l'AST donné en entrée.

    On décode la structure de l'AST en fonction du premier symbole, puis
    chaque type de noeud différent est traité à part.
    Si vous ajoutez une nouvelle construction à l'AST,
    par exemple ('MOINS', a, b) pour a - b, vous devez rajouter un cas
    à cette liste de conditions :
      ```
      elif ast[0] == 'MOINS':
          # Faire quelque chose avec ast[1] et ast[2]
          # Gardez à l'esprit que cela peut être des calculs arbitraires et pas
          # uniquement de simples entiers !
          # Il faut donc les compiler eux aussi en appelant `compile`.
          # N'oubliez pas de renvoyer le résultat !
      ```
    '''
    if ast[0] == 'AFFICHER':
        return compile(ast[1]) + depile('%rax') + 'print %rax\n'
    elif ast[0] == 'PLUS':
        return compile(ast[1]) + compile(ast[2]) + depile('%rax') \
            + depile('%rbx') + '%rax <- add %rbx\n' + empile('%rax')
    elif ast[0] == 'FOIS':
        return compile(ast[1]) + compile(ast[2]) + depile('%rax') \
            + depile('%rbx') + '%rax <- mul %rbx\n' + empile('%rax')
    elif ast[0] == 'ENTIER':
        return '%rax <- const {}\n'.format(ast[1]) + empile('%rax')


# Fonctions auxiliaires pour gérer la pile.

def empile(reg):
    return '''
(%rsp) <- store {reg}
 {reg} <- const 1
 %rsp  <- add {reg}
'''.format(reg=reg)

def depile(reg):
    return '''
 {reg} <- const 1
 %rsp  <- sub {reg}
 {reg} <- load (%rsp)
'''.format(reg=reg)


# Fausse fonction de compilation uniquement avec les registres, pour la démo.
def compile_faux(ast, reg=None):
    if ast[0] == 'AFFICHER':
        return compile_faux(ast[1], reg='%rax') + 'print %rax\n'
    elif ast[0] == 'PLUS':
        return compile_faux(ast[1], reg='%rax') + compile_faux(ast[2], reg='%rbx') \
            + ('%rax <- add %rbx\n' if reg == '%rax' else '%rbx <- add %rax\n')
    elif ast[0] == 'FOIS':
        return compile_faux(ast[1], reg='%rax') + compile_faux(ast[2], reg='%rbx') \
            + ('%rax <- mul %rbx\n' if reg == '%rax' else '%rbx <- mul %rax\n')
    elif ast[0] == 'ENTIER':
        return '{} <- const {}\n'.format(reg, ast[1])
