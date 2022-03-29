#coding=utf-8
class Board(object):
    """
    棋盘
    """
    def __init__(self, width=8, height=8, n_in_row=5):
        self.width = width
        self.height = height
        self.states = {} # 棋盘状态
        self.n_in_rows = n_in_row # 几子连成一线算胜利
    def init_board(self):
        if self.width < self.n_in_rows or self.height < self.n_in_rows:
            raise Exception('board width and height can not less than %d' % self.n_in_rows)
        self.availables = list(range(self.width*self.height)) # 棋盘上所有合法位置
        for m in self.availables:
            self.states[m] = -1 # -1表示空
    def move_to_location(self, move): # 一维变二维
        h = move // self.width
        w = move % self.width
        return [h, w]
    def location_to_move(self, location):
        if(len(location)!=2):
            return -1
        h = location[0]
        w = location[1]
        move = h*self.width+w
        if(move not in range(self.width*self.height)):
            return -1
        return move
    def update(self, player, move): # player在move处落子
        self.states[move] = player  # 更新棋盘
        self.availables.remove(move)  # 位置移除
