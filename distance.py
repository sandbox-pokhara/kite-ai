def get_chessboard_distance(coordinates_1, coordinates_2):
    x_1, y_1 = coordinates_1[:2]
    x_2, y_2 = coordinates_2[:2]
    return max(abs(y_2 - y_1), abs(x_2 - x_1))
