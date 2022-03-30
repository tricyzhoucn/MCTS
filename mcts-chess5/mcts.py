#coding=utf-8
import copy
import time
from math import log, sqrt
from random import choice


class MCTS(object):
    """
    mcts 蒙特卡洛搜索
    """
    def __init__(self, board, play_turn, n_in_row=5, time=5, max_actions=1000):
        self.board = board
        self.play_turn = play_turn # 出手顺序
        self.calculation_time = float(time) # 最大计算时间
        self.max_actions = max_actions # 模拟对局次数
        self.n_in_row = n_in_row # 判胜规则

        self.player = play_turn[0] # 模拟对局说明到ai的轮次所以ai先出手
        self.confident = 1.96 # ucb中的常数
        self.plays = {} # 记录着法模拟次数 (player,move)
        self.wins = {} # 记录着法获胜次数
        self.max_depth = 1
    def get_action(self): # return move
        if len(self.board.availables) == 1:
            return self.board.availables[0] # 棋盘只剩最后一个落子位置
        # 每次计算下一步时都要清空plays和wins表，因为经过AI和玩家的2步棋之后，整个棋盘的局面发生了变化，
        # 原来的记录已经不适用了——原先普通的一步现在可能是致胜的一步，如果不清空，会影响现在的结果，导致这一步可能没那么“致胜”了
        self.plays = {}
        self.wins = {}
        simulations = 0 # 模拟次数
        begin = time.time()
        while time.time() - begin < self.calculation_time:
            board_copy = copy.deepcopy(self.board) # 模拟会修改board 所以需要深拷贝
            play_turn_copy = copy.deepcopy(self.play_turn) # 每次模拟都必须按照固定顺序 深拷贝防止顺序被修改
            self.run_simulation(board_copy, play_turn_copy) # 进行MCTS模拟
            simulations += 1
        print("total simulations=", simulations)

        move = self.select_one_move() # 选择最佳着法 此时棋局已经被模拟填充好了所有下一步着法的次数和概率了
        location = self.board.move_to_location(move) # 移动到最终选择的位置
        print("Maximum depth searched:", self.max_depth) # 记录深度
        print("AI move: %d, %d\n" % (location[0], location[1]))
        return move
    def run_simulation(self, board, play_turn):
        """
        MCTS main process
        """
        plays = self.plays
        wins = self.wins
        availables = board.availables
        player = self.get_player(play_turn) # 获取当前出手的玩家
        visited_states = set() # 记录当前路径上的全部着法 这里不是从一开始记录 而是从当下棋局开始记录
        winner = -1 # 赢家给默认值
        expand = True # 是否扩展
        # Simulation
        for t in range(1, self.max_actions+1):
            # Selection
            # 如果所有着法都有统计信息，则获取ucb最大的着法
            if all(plays.get((player, move)) for move in availables):
                log_total = log(sum(plays[(player, move)] for move in availables))
                value, move = max(((wins[(player, move)]/plays[(player, move)]) + sqrt(self.confident*log_total/plays[(player, move)]), move) for move in availables)
            else:
                # 随机选择
                move = choice(availables)
            board.update(player, move)

            # Expand
            # 每次模拟最多扩展一次，每次扩展只增加一个着法， 这里才会真正影响后面的棋局
            if expand and (player, move) not in plays:
                expand = False # 扩展关闭
                plays[(player, move)] = 0 # 扩展一个未占领的位置
                wins[(player, move)] = 0 # 扩展一个未占领的位置
                if t > self.max_depth:
                    self.max_depth = t # 也可以认为记录棋盘上棋子数
            visited_states.add((player, move)) # 当前路径增加
            is_full = not len(availables) # 是否走满棋局
            win, winner = self.has_a_winner(board) # 棋局是否有一个胜者
            if is_full or win: # 游戏结束
                break
            player = self.get_player(play_turn) # 没有结束 更换次序 继续往下走

        # Back-propagation
        for player, move in visited_states: # 针对当前路径的走法
            if(player, move) not in plays: # 还没模拟过的地方 下面就是当前和之前模拟过的位置
                continue
            plays[(player, move)] += 1 # 扩展的那一步模拟次数加1
            if player == winner:
                wins[(player, move)] += 1 # 扩展那一步如果最终赢了则ai的扩展那一步胜利次数加1
    def get_player(self, players):
        p = players.pop(0)
        players.append(p)
        return p
    def select_one_move(self):
        percent_wins, move = max(
            (self.wins.get((self.player, move), 0) /
            self.plays.get((self.player, move), 1), move) for move in self.board.availables # 选择胜率最高的着法
        )
        return move
    def has_a_winner(self, board):
        """
                检查是否有玩家获胜
                """
        moved = list(set(range(board.width * board.height)) - set(board.availables))
        if (len(moved) < self.n_in_row + 2):
            return False, -1

        width = board.width
        height = board.height
        states = board.states
        n = self.n_in_row
        for m in moved:
            h = m // width
            w = m % width
            player = states[m]

            if (w in range(width - n + 1) and
                    len(set(states[i] for i in range(m, m + n))) == 1):  # 横向连成一线
                return True, player

            if (h in range(height - n + 1) and
                    len(set(states[i] for i in range(m, m + n * width, width))) == 1):  # 竖向连成一线
                return True, player

            if (w in range(width - n + 1) and h in range(height - n + 1) and
                    len(set(states[i] for i in range(m, m + n * (width + 1), width + 1))) == 1):  # 右斜向上连成一线
                return True, player

            if (w in range(n - 1, width) and h in range(height - n + 1) and
                    len(set(states[i] for i in range(m, m + n * (width - 1), width - 1))) == 1):  # 左斜向下连成一线
                return True, player

        return False, -1
    def __str__(self):
        return "AI"