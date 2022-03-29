#coding=utf-8
from random import choice, shuffle

from mcts import MCTS
from human import Human
class Game(object):
    """
    game server
    """
    def __init__(self, board, **kwargs):
        self.board = board
        self.player = [1, 2] # player1 and player2
        self.n_in_row = int(kwargs.get("n_in_row", 5))
        self.time = float(kwargs.get('time', 5))
        self.max_actions = int(kwargs.get('max_actions', 1000))
    def init_player(self):
        # 多个选手随机选俩
        plist = list(range(len(self.player)))
        index1 = choice(plist)
        plist.remove(index1)
        index2 = choice(plist)
        return self.player[index1], self.player[index2]
    def graphic(self, board, human, ai):
        """
        绘制棋盘状态
        """
        width = board.width
        height = board.height
        print("Human Player", human.player, "with X".rjust(3))
        print("AI    Player", human.player, "with O".rjust(3))
        print()
        for x in range(width):
            print("{0:8}".format(x), end="")
        print("\r\n")
        for i in range(height-1, -1, -1):
            print("{0:4d}".format(i), end="")
            for j in range(width):
                loc = i*width+j
                if board.states[loc] == human.player:
                    print("X".center(8), end="")
                elif board.states[loc] == ai.player:
                    print("O".center(8), end="")
                else:
                    print("_".center(8), end="")
            print("\r\n\r\n")
    def game_end(self, ai):
        win, winner = ai.has_a_winner(self.board)
        if win:
            return True, winner
        elif not len(self.board.availables):
            print("Game end. Tie") # 和局
            return True, -1
        return False, -1
    def start(self):
        p1, p2 = self.init_player()
        self.board.init_board()
        ai = MCTS(self.board, [p1, p2], self.n_in_row, self.time, self.max_actions)
        human = Human(self.board, p2) # 人是p2
        players = {}
        players[p1] = ai
        players[p2] = human
        turn = [p1, p2]
        shuffle(turn)
        while True:
            p = turn.pop(0) # 轮
            turn.append(p)  # 流
            player_in_turn = players[p]
            move = player_in_turn.get_action() # 获得行动方式（核心）
            self.board.update(p, move) # 当前轮次的移动
            self.graphic(self.board, human, ai) # 展示当前结果
            end, winner = self.game_end(ai) # 游戏结果判定
            if end:
                if winner!=-1:
                    print("Game end. Winner is", players[winner])
                break