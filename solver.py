# from sudoku_cv import predict_board
import time


def solve(bo):
    find = find_empty(bo)
    if not find:
        return True
    else:
        row, col = find

    set = [[1,2,3,4,5,6,7,8,9], 
            [2,3,4,5,6,7,8,9,1], 
            [3,4,5,6,7,8,9,1,2], 
            [4,5,6,7,8,9,1,2,3],
            [5,6,7,8,9,1,2,3,4],
            [6,7,8,9,1,2,3,4,5],
            [7,8,9,1,2,3,4,5,6],
            [8,9,1,2,3,4,5,6,7],
            [9,1,2,3,4,5,6,7,8]]
    
    solution_set = []
    for lst in set:
        for i in lst:
            if valid(bo, i, (row, col)):
                bo[row][col] = i

                if solve(bo):
                    solution_set.append(bo)
                    
                    return True

                bo[row][col] = 0
     
    return False


def valid(bo, num, pos):
    # Check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False

    # Check column
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False

    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x * 3, box_x*3 + 3):
            if bo[i][j] == num and (i,j) != pos:
                return False

    return True


def print_board(bo):
    for i in range(len(bo)):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - - - ")

        for j in range(len(bo[0])):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")

            if j == 8:
                print(bo[i][j])
            else:
                print(str(bo[i][j]) + " ", end="")


def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j) 

    return None

board = [[7,8,0,4,0,0,1,2,0],
        [6,0,0,0,7,5,0,0,9],
        [0,0,0,6,0,1,0,7,8],
        [0,0,7,0,4,0,2,6,0],
        [0,0,1,0,5,0,9,3,0],
        [9,0,4,0,6,0,0,0,5],
        [0,7,0,3,0,0,0,1,2],
        [1,2,0,0,0,7,4,0,0],
        [0,4,9,2,0,6,0,0,7]]

board1 = [[2, 9, 5, 7, 4, 3, 8, 6, 1],
        [4, 3, 1, 8, 6, 5, 9, 0, 0],
        [8, 7, 6, 1, 9, 2, 5, 4, 3],
        [3, 8, 7, 4, 5, 9, 2, 1, 6],
        [6, 1, 2, 3, 8, 7, 4, 9, 5],
        [5, 4, 9, 2, 1, 6, 7, 3, 8],
        [7, 6, 3, 5, 3, 4, 1, 8, 9],
        [9, 2, 8, 6, 7, 1, 3, 5, 4],
        [1, 5, 4, 9, 3, 8, 6, 0, 0]]

board2 = [[0,0,0,2,6,0,7,0,1],
        [6,8,0,0,7,0,0,9,0],
        [1,9,0,0,0,4,5,0,0],
        [8,2,0,1,0,0,0,4,0],
        [0,0,4,6,0,2,9,0,0],
        [0,5,0,0,0,3,0,2,8],
        [0,0,9,3,0,0,0,7,4],
        [0,4,0,0,5,0,0,3,6],
        [7,0,3,0,1,8,0,0,0]]

board3 = [[2,8,6,1,5,9,7,4,3],
        [3,5,7,6,4,8,2,1,9],
        [4,1,9,7,0,0,5,6,8],
        [8,2,1,9,6,5,4,3,7],
        [6,9,3,8,7,4,1,2,5],
        [7,4,5,3,0,0,8,9,6],
        [5,6,8,2,0,0,9,7,4],
        [1,3,4,5,9,7,6,8,2],
        [9,7,2,4,8,6,3,5,1]]

#board = predict_board('sudoku_original.jpeg')
if __name__ == '__main__':
    print_board(board)

    print("________________________\n")

    if solve(board):
        print_board(board)

    else:
        print('No solution')

start_time = time.time()
print("--- %s seconds ---" % (time.time() - start_time))


