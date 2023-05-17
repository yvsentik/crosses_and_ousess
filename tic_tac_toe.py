from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys


class Game(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tic-Tac toe")
        self.setGeometry(100, 100,
                         300, 450)

        self.field = []
        self.turn = 0

        self.build_field()
        self.show()

    def build_field(self):
        self.field = []

        for i in range(3):
            row = []
            for j in range(3):
                row.append((QPushButton(self)))
            self.field.append(row)

        x = 90
        y = 90

        self.label = QLabel(self)
        self.label.setGeometry(20, 300, 260, 60)
        self.label.setStyleSheet("QLabel"
                                 "{"
                                 "border : 1px solid black;"
                                 "background : white;"
                                 "}")

        for i in range(3):
            for j in range(3):
                self.field[i][j].setGeometry(x * i + 20,
                                             y * j + 20,
                                             80, 80)

                self.field[i][j].setFont(QFont(QFont('Times', 17)))
                self.field[i][j].clicked.connect(self.action_called)

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Times', 15))

        reset_game = QPushButton("Reset", self)
        reset_game.setGeometry(50, 380, 200, 50)
        reset_game.clicked.connect(self.reset)

    def reset(self):
        for row in self.field:
            for button in row:
                button.setEnabled(True)
                button.setText("")

        self.turn = 0

    def action_called(self):
        button = self.sender()
        button.setEnabled(False)

        if self.turn % 2 == 0:
            button.setText("X")
        else:
            button.setText("О")

        self.turn += 1


if __name__ == '__main__':
    App = QApplication(sys.argv)
    game = Game()
    sys.exit(App.exec())
