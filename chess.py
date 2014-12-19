#A chess program

def setup_board():
    '''Returns a list of lists. Every list in the upper
    level represents a row on the board. The lists are padded
    with null values at the beginning so that they begin at 1.

    To access a square at coordinates x, y the value is board[y][x].

    White's piece are capitalized and black's are lowercase.
    '''
    board = [''] #Initial empty value so rows and columns begin at one

    for y in range(8):
        board.append([''])
        for x in range(8):
            board[y+1].append(' ')

    home_row = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    for i, piece in enumerate(home_row): 
        x = i + 1
        board[1][x] = piece
        board[2][x] = 'P'
        board[7][x] = 'p'
        board[8][x] = piece.lower()

    return board

def move_parser(move):
    '''
    Valid moves - [piece][origin_data][x]target
    Target is essential and x doesn't matter at all unless
    I use it to check for mate in later versions or make its
    inclusion strict for captures

    Attempts to return valid target, piece and origin_data

    Doesn't parse moves strictly. For instance, the move
    'Nx[anything]e5' would parse like Nxe5 because after parsing
    target, anything after the x is discarded. 
    Any data placed between piece and origin_data also gets
    discarded as irrelevant
    '''
    notation = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}
    numbers = ['1', '2', '3', '4', '5', '6', '7', '8']
    pieces = ['R', 'N', 'B', 'Q', 'K'] #Pawns aren't used in move notation
    
    piece = None
    origin_data = None
    target = None

    #Get the target from last letter and number and strip it
    if len(move) >= 2 and move[-2] in notation and move[-1] in numbers:
        target = str(notation[move[-2]]) + str(move[-1])
        move = move[:-2]

    #Strip possible trailing x
    move_origin = move.split('x')[0]

    #Now only piece possibly followed by [origin_data]
    if len(move_origin) >= 1:
        if move_origin[-1] in notation or move_origin[-1] in numbers:
            piece = 'P'
            origin_data = move_origin[-1]
        if move_origin[0] in pieces:
            piece = move_origin[0]
    else:
        piece = 'P'

    return target, piece, origin_data

def find_endpoint(target, piece, xdir, ydir, board):
    '''Searches from target in the direction provided by
    xdir and ydir and returns the endpoint coordinates if
    the line ends on the right piece
    '''
    numbers = [1, 2, 3, 4, 5, 6, 7, 8]
    x = int(target[0]) + xdir
    y = int(target[1]) + ydir
    line_endpoint = None
    while x in numbers and y in numbers:
        if board[y][x] == piece:
            line_endpoint = str(x) + str(y)
            break
        if board[y][x] != ' ':
            break
        x += xdir
        y += ydir
    return line_endpoint

def get_possible_origins(target, piece, board, turn):
    '''This function determines where the piece moving could have come from
    and returns all possible origins as a list of 'xy' coordinates

    Pawns, knights and kings search by predestined distances from their
    location while bishops, rooks and queens search in lines
    '''
    numbers = [1, 2, 3, 4, 5, 6, 7, 8]
    possible_origins = []

    tar_x = int(target[0])
    tar_y = int(target[1])

    #To avoid taking own pieces
    target_square = board[tar_y][tar_x]
    if turn%2:
        if target_square != ' ' and target_square == target_square.upper():
            return possible_origins
    else:
        piece = piece.lower() #To check for black's lowercase pieces
        if target_square != ' ' and target_square == target_square.lower():
            return possible_origins

    if piece == 'P' or piece == 'p':
        #Two captures, a move forward and a leap forward
        moves = []

        if turn%2:
            pawn_dir = -1 #Pawn direction
        else:
            pawn_dir = 1

        if board[tar_y][tar_x] == ' ':
            if tar_y + turn%2 == 5 and board[tar_y + pawn_dir][tar_x] == ' ':
                #Leap forward if origin is home row and no piece in the middle
                moves.append([0, 2 * pawn_dir])
            elif board[tar_y + pawn_dir][tar_x] == piece:
                #Spot might be occupied, so check if that piece is a pawn
                moves.append([0, pawn_dir])
        else:
            #Target is occupied, so attempt capture
            moves.append([-1, pawn_dir])
            moves.append([1, pawn_dir])

        for move in moves:
            x = tar_x + move[0]
            y = tar_y + move[1]
            if x in numbers and y in numbers and board[y][x] == piece:
                possible_origins.append(str(x) + str(y))

    if piece == 'B' or piece == 'b' or piece == 'Q' or piece == 'q':
        moves = [[-1, 1], [1, 1], [1, -1], [-1, -1]]
        for move in moves:
            endpoint = find_endpoint(target, piece, move[0], move[1], board)
            if endpoint is not None:
                possible_origins.append(endpoint)

    if piece == 'R' or piece == 'r' or piece == 'Q' or piece == 'q':
        moves = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        for move in moves:
            endpoint = find_endpoint(target, piece, move[0], move[1], board)
            if endpoint is not None:
                possible_origins.append(endpoint)

    if piece == 'K' or piece == 'k':
        moves = [ [-1, 0], [-1, 1], [-1, -1], [0, 1], 
                  [0, -1], [1, 0],  [1, 1],  [1, -1], 
                ]
        for move in moves:
            x = tar_x + move[0]
            y = tar_y + move[1]
            if x in numbers and y in numbers:
                if board[y][x] == piece:
                    possible_origins.append(str(x) + str(y))
                    print(str(x)+str(y))

    if piece == 'N' or piece == 'n':
        moves = [ [-2, 1], [-2, -1], [-1, 2], [-1, -2], 
                  [1, 2], [1, -2], [2, 1], [2, -1],
                ]
        for move in moves:
            x = tar_x + move[0]
            y = tar_y + move[1]
            if x in numbers and y in numbers and board[y][x] == piece:
                possible_origins.append(str(x) + str(y))

    return possible_origins

def get_single_origin(possible_origins, origin_data):
    '''Gets a list of 'xy' coordinates of possible origins. Must
    use origin_data to narrow it down to one or else return None
    '''
    notation = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}
    numbers = ['1', '2', '3', '4', '5', '6', '7', '8']
    origin = None

    parsed_origins = []

    if origin_data and len(possible_origins) > 1:
        for possible_origin in possible_origins:
            #Search through all possible pieces that could make the move
            #and attempt to narrow it down to a single value with origin_data
            ori_x = possible_origin[0]
            ori_y = possible_origin[1]
            if origin_data in notation and int(ori_x) == notation[origin_data]:
                parsed_origins.append(possible_origin)
            elif origin_data in numbers and ori_y == origin_data:
                parsed_origins.append(possible_origin)
        
    if len(possible_origins) == 1:
        origin = possible_origins[0]
    elif len(parsed_origins) == 1:
        origin = parsed_origins[0]
    else:
        print(len(possible_origins), 'pieces can make that move')

    return origin

def update_board(origin, target, board):
    '''Takes two squares origin and target as strings of coordinates
    in 'xy' format. Moves the piece at the origin to the target
    and makes the origin equal to ' '
    '''
    ori_x = int(origin[0])
    ori_y = int(origin[1])
    tar_x = int(target[0])
    tar_y = int(target[1])

    piece = board[ori_y][ori_x]
    captured_piece = board[tar_y][tar_x]
    empty = ' '

    board[ori_y][ori_x] = empty
    board[tar_y][tar_x] = piece

    if captured_piece == 'K' or captured_piece == 'k':
        check_mate = True
    else:
        check_mate = False

    return board, check_mate

def print_board(board, turn):
    '''Rotates the board according to turn so that the 
    proper player is at the bottom with the pieces in the right order
    '''
    if turn%2: #White's turn
        horizontal_board_order = range(1, 9)
        vertical_board_order = range(8, 0, -1)
    else: #Black's turn
        horizontal_board_order = range(8, 0, -1)
        vertical_board_order = range(1, 9)

    light_square = ' '
    dark_square = '='
    top_border = '_'
    bottom_border = '-'
    side_border = '|'
    empty = ' '

    print(top_border * 17) #Top of the board. 17 is the width with borders
    for y in vertical_board_order:
        line = side_border
        for x in horizontal_board_order:
            square = board[y][x]
            if square != empty:
                line = line + square + side_border
            else:
                if (x+y)%2:
                    line = line + dark_square + side_border
                else:
                    line = line + light_square + side_border
        print(line)
        print(bottom_border * 17)
    
def run_game():
    board = setup_board()
    turn = 1
    check_mate = False

    print_board(board, turn)

    move = input('Please enter a move for White: ') 

    while move != 'q' and move != 'quit':
        target, piece, origin_data = move_parser(move)

        if target is not None and piece is not None:
            possible_origins = get_possible_origins(target, piece, board, turn)
            origin = get_single_origin(possible_origins, origin_data)

            if origin is not None:
                board, check_mate = update_board(origin, target, board)
                turn += 1
        else:
            print('Move could not be parsed. Check your notation')

        print_board(board, turn)
        
        if check_mate:
            print('Checkmate!')
            break
        else:
            if turn%2:
                playersturn = 'White'
            else:
                playersturn = 'Black'
            move = input('Please enter a move for ' + playersturn + ': ')

run_game()
