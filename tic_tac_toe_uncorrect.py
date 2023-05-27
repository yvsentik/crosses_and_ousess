from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from fit_agents import *

import sys
import random


class GameButton(QPushButton):
    def __init__(self, x, y, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y


class Game(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tic-Tac toe")
        self.setGeometry(100, 100,
                         300, 450)
        self.enabledCorners = [[0, 0], [0, 2], [2, 0], [2, 2]]
        self.label = QLabel(self)
        self.field_buttons = []
        self.field = [[0]*3 for _ in range(3)]
        self.turn = 0
        self.player = Player(exp_rate=0)
        self.player.loadPolicy("policy_p1")

        self.build_field()
        self.show()

    def build_field(self):
        self.field_buttons = []

        for i in range(3):
            row = []
            for j in range(3):
                row.append((GameButton(j, i, self)))
            self.field_buttons.append(row)

        x = 90
        y = 90

        self.label.setGeometry(20, 300, 260, 60)
        self.label.setStyleSheet("QLabel"
                                 "{"
                                 "background : white;"
                                 "}")

        for i in range(3):
            for j in range(3):
                self.field_buttons[i][j].setGeometry(x * i + 20,
                                                     y * j + 20,
                                                     80, 80)

                self.field_buttons[i][j].setFont(QFont(QFont('Times', 17)))
                self.field_buttons[i][j].clicked.connect(self.action_called)

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Times', 15))

        reset_game = QPushButton("Reset", self)
        reset_game.setGeometry(50, 380, 200, 50)
        reset_game.clicked.connect(self.reset)

    def reset(self):
        for row in self.field_buttons:
            for button in row:
                button.setEnabled(True)
                button.setText("")
        self.field = [[0] * 3 for _ in range(3)]
        self.turn = 0

    def correctMatrix(self):
        for i in range(3):
            for j in range(3):
                if self.field[i][j] == 2:
                    self.field[i][j] = -1
        return self.field

    def action_called(self):
        button = self.sender()
        x = button.x
        y = button.y
        if self.turn % 2 + 1 == 2:
            self.field[x][y] = -1
        else:
            self.field[x][y] = 1

        button.setEnabled(False)
        self.turn += 1

        if self.turn % 2:
            button.setText("❌")
            positions = getAvailablePositions(self.field)
            x, y = self.player.chooseAction(positions, self.field, -1)
            print(x, y)
            self.field_buttons[x][y].click()
        else:
            button.setText("⭕")


if __name__ == '__main__':
    App = QApplication(sys.argv)
    game = Game()
    sys.exit(App.exec())
