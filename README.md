# Informatique Pour Tous
## Comment créer un langage de programmation ? - Florentin Guth

### Installation

Vous aurez besoin de :
 - cloner ce repository (dépôt) : cliquez sur télécharger en haut à droite,
 - python 3,
 - le paquet `ply` (`pip3 install ply`).
 
Pour ces 3 étapes, vous pouvez vous référer au `README.md` de [Lucas](https://github.com/lcswillems/python-MNIST-classifier).


### Utilisation

Ouvrez une console python depuis ce répertoire. Sur Windows, shift + clique droit dans le navigateur, choississez "Ouvrir une invite de commande" dans le menu déroulant, puis tapez `python`. Sous Linux, tapez `python` dans un terminal.
Pour compiler un programme, écrivez :
```python
>>> from main import test
>>> test('AFFICHER((3 + 2) * 6 + 12)')
```
Cela va générer afficher le programme, l'arbre de syntaxe abstraite (AST, pour Abstract Syntax Tree en anglais), les instructions assembleur générées par le compilateur, et finalement le résultat de l'exécution.

Si votre programme est situé dans un fichier, vous pouvez le lire de la manière suivante :
```python
>>> with open('chemin/de/mon/fichier.code') as f:
>>>     code = ''.join(f.readlines())
>>> test(code)
```

### Liste des fichiers

Voici les fichiers que j'ai utilisé pour la démonstration dans l'exposé :
- `parser.py` contient le code qui lit le fichier source `.code` et le convertit en arbre de syntaxe abstraite (AST).
C'est ce fichier qui définit ce qu'il est possible d'écrire dans un programme `.code`, et comment l'AST est représenté.
- `compile.py` prend en entrée un AST et renvoie le (un) programme assembleur correspondant.
C'est là que les choses intéressantes se passent ! Il définit les opérations qui manipulent la pile par exemple.
- `interprete_asm.py` prend en entrée une liste d'instructions assembleur. Il permet de vérifier qu'il n'y a pas eu d'erreur lors de la compilation ! 
Il définit les opérations assembleur autorisées et leur sens.
- `main.py` contient les fonctions de test utilisées pendant l'exposé.
- `exemples/p*.code` : exemples de difficulté croissante, que vous pouvez essayer de compiler (cf. plus bas).
- `solutions/*.py` : code de la solution, qui marche sur tous les exemples (sauf le dernier, il ne faut pas rêver non plus !). A n'aller voir que si vous avez vraiment essayé !

### Pour aller plus loin

Je n'ai pas décrit le fonctionnement du lexer/parser, mais je vous encourage à aller lire `parser.py` et essayer de comprendre comment cela marche grâce aux commentaires !
J'ai utilisé le paquet [ply](https://github.com/dabeaz/ply) pour me simplifier la vie, vous pouvez allez voir sa [documentation](http://www.dabeaz.com/ply/ply.html) (en anglais), ou vous partir de l'exemple qui est donné dans leur `README` qui présente bien les principes de base. C'est un paquet qui permet de faire du lexing (regrouper les caractères en tokens comme des nombres ou des noms de variable) et du parsing (regrouper les tokens en groupes comme des expressions, et les organiser en un arbre).

Vous pouvez tenter d'optimiser l'assembleur produit en détectant les cas où on effectue un empilement suivi d'un dépilement (ce qui ne sert strictement à rien à part perdre du temps) pour éviter ce cas de figure.

Pour les plus courageux, vous pouvez essayer de compiler les programmes en exemple (le premier marche déjà, c'est faux pour le reste !). J'ai expliqué très rapidement comment faire pour certains d'entre eux dans la conclusion de l'exposé. Je vous conseille d'utiliser les `parser.py` et `interprete_asm.py` de la solution (ce dernier contient des opérations supplémentaires qui peuvent être utiles), mais de vous occuper vous-même de `compile.py`. Ces exercices deviennent assez vite corsés, plutôt que d'aller voir la solution, cherchez sur internet ou dans les ressources (cf. plus bas) pour des indices, et implémentez l'idée vous-même !
En-dehors des ajouts que j'ai fait dans la solution, essayez de ne pas modifier `interprete_asm.py` ! Je sais que c'est tentant, mais l'exercice est de faire des miracles avec le très peu d'instructions que je vous ai laissées ;)

Un exemple de fonctionnalité relativement simple à ajouter au langage est la soustraction ou la division.
Vous devrez modifier `parser.py` pour permettre à l'utilisateur de les utiliser, puis les compiler correctement dans `compile.py`.
Et si vous ne voulez pas passer du temps sur le parser, vous pouvez toujours écrire l'AST à la main pour de petits programmes ! Par exemple, pour `p1.code`, cela donne :
```python
ast_p1 = ("AFFICHER",
          ("PLUS",
           ("FOIS",
            ("PLUS",
             ("ENTIER", "3"),
             ("ENTIER", "2")
            ),
            ("ENTIER", "6")
           ),
           ("ENTIER", "12")
          )
         )
```

Exercice bonus : rajouter des tableaux. Premièrement, vous pouvez vous limiter au cas où leur taille est connue à l'avance (c'est-à-dire, c'est un `("ENTIER", "12")`), puis traiter le cas (plus difficile ! pourquoi ?) où elle n'est pas encore connue (par exemple, `("VARIABLE", "n")`).


### Ressources et liens

- Lien de la page de l'exposé (vidéo et slides) : http://seminairespourtous.ens.fr/ipt/1819/exposes/23/comment-creer-un-langage-de-programmation
- Lien de la conférence de David Naccache sur les systèmes de calcul avec des plantes carnivores : https://www.dailymotion.com/video/xbwqej
- L'excellent cours de Jean-Christophe Filliâtre sur la compilation, que j'ai eu le plaisir d'avoir en L3 et qui est la raison que cet exposé existe : https://www.lri.fr/~filliatr/ens/compil/2016-2017/
- Le "livre du dragon" *Compilateurs : principes, techniques et outils* : je ne l'ai pas lu donc que je ne peux pas le recommander personnellement, mais c'est une référence !
- Un tutoriel pour apprendre à programmer en python d'OpenClassrooms (mais il en existe plein d'autres sur internet) : https://openclassrooms.com/fr/courses/235344-apprenez-a-programmer-en-python

### Contact
 
Si vous avez des questions, vous pouvez bien entendu me les poser !
Vous pouvez créer une *issue* (pour signaler un problème) sur ce repository, ou me contacter par e-mail à `prenom.nom@ens.fr` (mon nom est en haut de ce `README`).
