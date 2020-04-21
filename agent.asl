


+car(Color) <-
    .print("The car is",Color);
    a_function(3, X);
    .print("return value =", X).


+car(Color, Size)
 <- .print("The car is",Color, Size).


+cell_empty(R, D) : D == n <-
    bdi_move(R, D, X);
    .print("return value =", X).