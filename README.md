Sokoban in python
# Summary
The creation of a Sokoban game program, which includes an automatic solver
to assist the player and an editor for the game's level set. The program should
support different skins and several sets of levels.

During development, the program was split into two logical parts. One is the
menu system, which with a little modification could be a package in itself. The other
unit is the game program itself, where the understanding and development of the
sokoban solvers took longer. The level editor makes it easy to create new tracks for
the game.

While developing the menu system, I got to know more about the event handlers
that can be implemented by the pygame package and the drawing options in the
same package. This resulted in a package that can even be used on its own, and in
the process of developing it I became more aware of the difficulties of developing a
basic user interface and, in turn, the customisability that self-development offers.
During the development of the game, I learned about how Sokoban solvers work
and the difficulties of solving Sokoban problems. Although artificial intelligence
solutions are gaining ground in this field, I found that there are still problems that
can be solved with well thought-out algorithms like this one.

As I have already mentioned, the menu system for the program could be used
as a stand-alone user interface package. Therefore this part of the program could
be implemented in other programs.

Since the program supports external looks, by creating them with a custom level
you can create a unique game for yourself with a little graphical knowledge. The
looks also support animated characters and the display of isometric walls.
