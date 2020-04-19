!start.

+!start <-
    +car(blue).

+car(Color)
 <- .print("The car is",Color).

+cell_empty(cheese) <- .print(cheese).

+cell_empty(request_id, direction) <-
    +car(orange);
    bdi_move(request_id, direction).