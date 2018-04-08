'''
Compile un programme et l'exécute.
Utilisation :
>>> from main import *
>>> test('AFFICHER((3 + 2) * 6 + 12)')
'''

import parser, compile, interprete_asm

def test(prog, cpl=compile.compile):
    print('Programme :')
    print(prog)
    print('')

    ast = parser.parse(prog)
    print('Arbre :')
    parser.print_ast(ast)
    print('')

    asm = cpl(ast)
    print('Assembleur :')
    interprete_asm.print_asm(asm)
    print('')

    print('Exécution :')
    interprete_asm.interprete(asm)

def test1():
    test('AFFICHER((3 + 2) * 6 + 12)', compile.compile_faux)

def test2():
    test('AFFICHER(6 * (4 + 3))', compile.compile_faux)

def test3():
    test('AFFICHER(6 * (4 + 3))', compile.compile)

def test4():
    test('AFFICHER((3 + 2) * 6 + 12)', compile.compile)
