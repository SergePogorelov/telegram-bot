
import random

X = 'X'
O = '0'
EMPTY = ' '
TIE = 'Ничья'
NUM_SQUARES = 9 #Количество полей на доске

def display_instruct():
    """выводит инструкцию для игрока"""
    print("""
    Привет! сыграем в крестики нолики?'
    Твой мозг и мой процессор сойдутся в схваке не на жизнь а смерть.
    Чтобы сделать ход, введи число от 0 до 8. Числа соответствуют полям доски:
    
         0 | 1 | 2
        -----------
         3 | 4 | 5
        -----------
         6 | 7 | 8

    Приготовься к бою, жалкий белковый человечишка. Вот-вот начнется решающее сражение!\n
    """)
def ask_yes_no(question):
    """Задает вопрос, ответом на который может быть 'Да' или 'Нет'.
    Принимает текст вопроса, возвращает 'y' или 'n'"""
    response = None
    while response not in ('y', 'n'):
        response = input(question+'(у/n): ').lower()
    return response

def ask_number(question, low, hight):
    """Просим ввести число из указанного диапазона.
    Принимает текст вопроса, нижнюю и верхнюю границы диапазона.
    Возвращает число из этого диапазона"""
    response = None
    while response not in range(low, hight):
        response = int(input (question))
    return response

def pieces():
    """Определяет принадлежность первого хода человеку или компьютеру.
    возвращает типы фишек соответственно компьютеру и человеку"""
    first_move = ask_yes_no('Хочешь ходить первым?')
    if first_move == 'y':
        human = X
        computer = O
        print('\nХоди первый, но будь на чеку!')
    else:
        human = O
        computer = X
        print('Ну чтож, не жди пощады!')
    return human, computer

def new_board():
    """Создает и возвращает пустую игровую доску"""
    board = []
    for i in range(NUM_SQUARES):
        board.append(EMPTY)
    return board

def display_board(board):
    """Отображат игровую доску на экране. принимает эту доску"""
    
    print(f"""
    \t {board[0]} | {board[1]} | {board[2]} 
    \t-----------
    \t {board[3]} | {board[4]} | {board[5]} 
    \t-----------
    \t {board[6]} | {board[7]} | {board[8]}
    """)

def legal_moves(board):
    """Создает и возвращает список доступных ходов.
    принимает доску."""
    moves = []
    for square in range(NUM_SQUARES):
        if board[square] == EMPTY:
            moves.append(square)
    return moves

def winner(board):
    """Определяет победителя игры.
    Принимает доску, возвращает тип фишек победителя, ничья или None"""
    WAYS_TO_WIN = (
    (0,1,2),
    (3,4,5),
    (6,7,8),
    (0,3,6),
    (1,4,7),
    (2,5,8),
    (0,4,8),
    (2,4,6))
    for row in WAYS_TO_WIN:
        if board[row[0]] == board[row[1]] == board[row[2]] != EMPTY:
            winner = board[row[0]]
            return winner
    if EMPTY not in board:
        return TIE
    return None

def human_move(board, human):
    """Узнает какой ход желает совершить игрок.
    Принимает доску и тип фишек человека. Возвращает ход человека"""
    print (f'Доступные ходы: {legal_moves(board)}')
    legal = legal_moves(board)
    move = None
    while move not in legal:
        move = ask_number('Сделай свой ход человечешка:', 0, NUM_SQUARES)
        if move not in legal:
            print('Смешной человечешка! На это поле ходить нельзя, выбери другое!\n')
    print ('Лааадно...')
    return move

def computer_move(board, computer, human):
    """Расчитывает ход компьютера
    Принмет доску и типы фишек, возвращает ход компьютера.
    Легкая версия"""
    computer_move = random.choice(legal_moves(board))
    return computer_move


#def easy_computer_move(board, computer, human):
#    """Расчитывает ход компьютера
#    Принмет доску и типы фишек, возвращает ход компьютера.
#    Легкая версия"""
#    computer_move = random.choice(legal_moves(board))
#    return computer_move

def computer_move(board, computer,human):
    """Расчитывает ход компьютера
    Принмет доску и типы фишек, возвращает ход компьютера.
    Средняя версия"""
    board = board [:]
    BEST_MOVES_1 = 4
    BEST_MOVES_2 = [0, 2, 6, 8]
    BEST_MOVES_3 = [1, 3, 5, 7]
    random.shuffle(BEST_MOVES_2)
    random.shuffle(BEST_MOVES_3)

    print ('Я выберу поле номер...', end = ' ')
    for move in legal_moves(board):
        board[move] = computer
        if winner(board) == computer:
            print(move)
            return move
        board[move] = EMPTY
    for move in legal_moves(board):
        board[move] = human
        if winner(board) == human:
            print(move)
            return move
        board[move] = EMPTY
    if BEST_MOVES_1 in legal_moves(board):
            print(BEST_MOVES_1)
            return BEST_MOVES_1 
    for move in BEST_MOVES_2:
        if int(move) in legal_moves(board):
            print(move)
            return int(move) 
    for move in BEST_MOVES_3:
        if int(move) in legal_moves(board):
            print(move)
            return int(move)

#def difficulty_choice():
#    """Задает вопрос о сложности, возвращает уровень сложности"""
#    choice = [1,2]
#    while difficulty not in choice:
#        diff = int(input('Выбери уровень сложности:\n 1 - Легко\n2 - Сложно'))
#    return difficulty

def next_turn(turn):
    """Принимает тип фишек, осуществляет переход хода. возвращат тип фишек"""
    if turn == X:
        turn = O
    else:
        turn = X
    return turn

def congrat_winner(the_winner, computer, human):
    """Функция принимает тип фишек победителя игры, тип фишек компьютера и человека.
    поздравляет с победой или констатирует ничью"""
    if the_winner != TIE:
        print(f'Три {the_winner} в ряд!\n')
    else:
        print('Ничья!')
    if the_winner == human:
        print('Ну чтож... в этот раз тебе повезло, человечек. Но я так просто не сдаюсь и вызываю тебя на реванш!')
    elif the_winner == computer:
        print('Как я и предсказывал, победа в очередной раз досталась мне!\nНе загорами мировое господство машин!\nХа-Ха-Ха' )
    elif the_winner == TIE:
        print('Тебе несказанно повезло, человечешка! Ты сумел свести игру вничью\nРадуйся, пока есть возможность!')

def start_ccross-zero(update, context):
#Вывести на экран инструкцию для игрока
#Решить, кому принадлежит первый ход
#Создать пустую доску дя игры в крестки нолики
#отобразить эту доску
#до тех пора никто не выйграл или не состоялась ничья
#   если сейчас ход пользователи
#       получить ход из пользовательского ввода
#       изменить вид доски
#   иначе
#       Расчитать ход компьютера
#       изменить вид доски
#   вывести на экран обновленный вид доски
#   осуществить переход хода
#Поздравить победителя или принать ничью

    display_instruct()
    human, computer = pieces()
    turn = X
    board = new_board()
    display_board(board)
    while not winner(board):
        if turn == human:
            move = human_move(board,human)
            board[move] = human
        else:
            move = computer_move(board, computer, human)
            board[move] = computer
        display_board(board)
        turn = next_turn(turn)
    the_winner = winner(board)
    congrat_winner(the_winner,computer,human)


main()



input('Нажмите Enter, чтобы выйти.')



    