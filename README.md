# Janggi Game - Portfolio Project

This is a portfolio project done for a computer science class. This program creates a class
named JanggiGame for playing an abstract board game called Janggi. For the specific rules,
the overall "Rules" section on [the Wikipedia page](https://en.wikipedia.org/wiki/Janggi) explains
them well. The following rules are _not_ implemented: rules regarding perpetual check, 
position repetition, any kind of draw or the miscellaneous rules. 

The game handles checkmate, all piece-specific rules, check, and not allowing pieces to make moves
if doing so would put the player's general in check. The game ends if one player's general is
put into checkmate. Janggi allows you to pass a turn and thus there is no stalemate (a scenario when no legal moves can 
be made). 

The competing players are Blue and Red with Blue as the starting player. No special mechanism is 
implemented for figuring out who can start the game.

Locations on the board are specified using "algebraic notation", with columns labeled a-i and rows 
labeled 1-10, with row 1 being the Red side and row 10 the Blue side. The initial board setup 
has the Elephant transposed with the Horse, on the right side, as seen on the image from Wikipedia.

A method called `make_move` when called will move the pieces. This method takes two parameters - 
strings that represent the square to move from and the square to move to. For example, 
`make_move('b3', 'b10')`.  
* If the square being moved from does not contain a piece belonging to the player whose turn it is, 
or 
* if the indicated move is not legal, or 
* if the game has already been won, then it should just return False.  
* Otherwise it should make the indicated move, remove any captured piece, update the game state if 
necessary, update whose turn it is, and return True.

If the `make_move` method is passed the same string for the square moved from and to, it should be 
processed as the player passing their turn, and return True.