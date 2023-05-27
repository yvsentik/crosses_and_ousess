import random
import json
import copy


def getHash(field):
    """
    Создаёт хэш состояния игры
    :return: строка из массива с полем игры
    """
    state = []
    for row in field:
        for cell in row:
            state.append(cell)

    return str(state)


def getAvailablePositions(field):
    """
    Определение списка из возможных позиций
    :return: список ячеек, куда можно поставить крестик или нолик
    """
    positions = []
    for i in range(3):
        for j in range(3):
            if field[i][j] == 0:
                positions.append((i, j))
    return positions


class Model:
    def __init__(self, player1, player2):
        self.field = [[0] * 3 for _ in range(3)]  # Поле игры
        self.tic_player = player1  # Крестики
        self.tac_player = player2  # Нолики
        self.isEnd = False
        self.boardHash = ''
        self.playerSymbol = 1

    def checkWinner(self):
        """
        Функця определяет победителя в игре
        :return: 1 - победили крестики, -1 - нолики, 0 -ничья
        """
        # Смотрим по строкам
        for i in range(3):
            row_sum = sum(self.field[i])
            if row_sum == 3:
                self.isEnd = True
                return 1
            if row_sum == -3:
                self.isEnd = True
                return -1

        # Смотрим по столбцам
        for i in range(3):
            col_sum = sum([self.field[k][i] for k in range(3)])
            if col_sum == 3:
                self.isEnd = True
                return 1
            if col_sum == -3:
                self.isEnd = True
                return -1

        # Смотрим по диагоналям
        diag_sum1 = sum([self.field[i][i] for i in range(3)])
        diag_sum2 = sum([self.field[i][3 - i - 1] for i in range(3)])
        diag_sum = max(abs(diag_sum1), abs(diag_sum2))
        if diag_sum == 3:
            self.isEnd = True
            if diag_sum1 == 3 or diag_sum2 == 3:
                return 1
            else:
                return -1

        # Если ничья
        if len(getAvailablePositions(self.field)) == 0:
            self.isEnd = True
            return 0
        # Если ещё не конец игры
        self.isEnd = False

        return None

    def updateState(self, position):
        # Как работает??
        self.field[position[0]][position[1]] = self.playerSymbol
        self.playerSymbol = -1 if self.playerSymbol == 1 else 1

    def giveReward(self):
        """
        Раздать агентам награду после игры
        """
        result = self.checkWinner()
        if result == 1:
            self.tic_player.feedReward(1)
            self.tac_player.feedReward(0)
        elif result == -1:
            self.tic_player.feedReward(0)
            self.tac_player.feedReward(1)
        else:
            self.tic_player.feedReward(0.1)
            self.tac_player.feedReward(0.5)

    def reset(self):
        """
        Перезапустить игру
        """
        self.field = [[0] * 3 for _ in range(3)]
        self.boardHash = ''
        self.isEnd = False
        self.playerSymbol = 1

    def fit(self, rounds):
        for i in range(rounds):
            if i % 1000 == 0:
                print(f'Игра №{i}')
            while not self.isEnd:
                # Ход крестиков
                positions = getAvailablePositions(self.field)
                tic_cell = self.tic_player.chooseAction(positions, self.field, self.playerSymbol)
                # Обновляется состояние
                self.updateState(tic_cell)
                field_hash = getHash(self.field)
                self.tic_player.states.append(field_hash)

                # Определяем победил ли игрок
                win = self.checkWinner()
                if win is not None:
                    # self.showBoard()
                    # ended with tic_player either win or draw
                    self.giveReward()
                    self.tic_player.reset()
                    self.tac_player.reset()
                    self.reset()
                    break

                else:
                    # Ход ноликов
                    positions = getAvailablePositions(self.field)
                    tac_action = self.tac_player.chooseAction(positions, self.field, self.playerSymbol)
                    self.updateState(tac_action)
                    field_hash = getHash(self.field)
                    self.tac_player.states.append(field_hash)

                    # Победил ли игрок
                    win = self.checkWinner()
                    if win is not None:
                        self.giveReward()
                        self.tic_player.reset()
                        self.tac_player.reset()
                        self.reset()
                        break

    # play with human
    def play2(self):
        while not self.isEnd:
            # Player 1
            positions = getAvailablePositions(self.field)
            p1_action = self.tic_player.chooseAction(positions, self.field, self.playerSymbol)
            # take action and upate field state
            self.updateState(p1_action)
            self.showBoard()
            # check field status if it is end
            win = self.checkWinner()
            if win is not None:
                if win == 1:
                    print(f"{win} wins!!")
                else:
                    print("tie!")
                self.reset()
                break

            else:
                # Player 2
                positions = getAvailablePositions(self.field)
                p2_action = self.tac_player.chooseAction(positions)

                self.updateState(p2_action)
                self.showBoard()
                win = self.checkWinner()
                if win is not None:
                    if win == -1:
                        print(self.tac_player.name, "wins!")
                    else:
                        print("tie!")
                    self.reset()
                    break


class Player:
    def __init__(self, exp_rate=0.1, learning_rate=0.2):
        self.states = []  # Записываются все состояния поля
        self.lr = learning_rate  # Скорость обучения
        self.exp_rate = exp_rate  # Вероятоность случайного действия
        self.decay_gamma = 0.9  # Параметр в формуле обновления значений состояний
        self.states_value = {}  # Словарь {Состояние: значение}

    def chooseAction(self, positions, current_board, symbol):
        """
        Выбор действия
        :param positions: возможные клетки, куда можно поставить символ
        :param current_board: состояние поля
        :param symbol: какой символ нужно поставить
        :return:
        """
        # С заданной вероятностью действие случайное
        if random.random() <= self.exp_rate:
            action = random.choice(positions)
        else:
            action = [-1, -1]
            value_max = float('-inf')
            for p in positions:
                next_board = copy.deepcopy(current_board)
                next_board[p[0]][p[1]] = symbol
                next_boardHash = getHash(next_board)
                if self.states_value.get(next_boardHash) is None:
                    value = 0
                else:
                    value = self.states_value.get(next_boardHash)

                if value >= value_max:
                    value_max = value
                    action = p
        return action

    def feedReward(self, reward):
        """
        Обновить значения для всех состояний, которые были в игре, в зависимости от её исхода
        :param reward: награда после игры
        """
        for state in reversed(self.states):
            if self.states_value.get(state) is None:
                self.states_value[state] = 0
            self.states_value[state] += self.lr * (self.decay_gamma*reward - self.states_value[state])
            reward = self.states_value[state]

    def reset(self):
        self.states = []

    def savePolicy(self, name: str):
        with open(f'{name}.json', 'w') as file:
            json.dump(self.states_value, file)

    def loadPolicy(self, filename):
        with open(f'{filename}.json', 'r') as file:
            self.states_value = json.load(file)


if __name__ == "__main__":
    p1 = Player()
    p2 = Player()

    model = Model(p1, p2)
    print("training...")
    model.fit(100_000)
    p1.savePolicy('policy_p1')
