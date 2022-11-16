import os
from time import sleep
from kbhit import *

atexit.register(set_normal_term)
set_curses_term()

class Color:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RETURN = '\033[07m' #反転
    ACCENT = '\033[01m' #強調
    FLASH = '\033[05m' #点滅
    RED_FLASH = '\033[05;41m' #赤背景+点滅
    END = '\033[0m'

# {score: character}
alien_dic = {
    100: [Color.BLUE + '_', 'x', '_' + Color.END],
    150: [Color.GREEN + '<', 'O', '>' + Color.END],
    200: [Color.RED + 'o', '=', 'o' + Color.END],
    500: [Color.PURPLE + '<', 'o', ' ', 'o', '>' + Color.END]
}

# \033[nA #n行上に
# \033[nB #n行下に
# \033[nC #n行右に
# \033[nD #n行左に


canvas_width = 50
canvas_height = 20

class Alien:
    def __init__(self, x, y, score):
        self.x = x
        self.y = y
        self.radius = 1
        self.hitcircle = (self.x, self.y)
        self.xdir = 1
        self.ydir = 0
        self.edge = False
        self.moveloop = 0
        self.score = score
        self.character_list = alien_dic[score]
        self.character_length = len(self.character_list)

    def draw(self, win):
        row = win[self.y]
        row_before = row[:self.x-(self.character_length//2)]
        row_after = row[self.x+(1+self.character_length//2):]
        win[self.y] = row_before + self.character_list + row_after

    def move(self):
        self.x += self.xdir

    def shift_down(self):
        self.xdir *= -1
        self.y += self.radius

class Player:
    def __init__(self, x):
        self.x = x
        self.character = [Color.YELLOW + "/", "-", "^", "-", "\\" + Color.END]

    def move(self, key):
        if key == "left":
            self.x -= 1
        elif key == "right":
            self.x += 1
        return self
    
    def draw(self, win):
        row = win[-1]
        win[-1] = row[: self.x - 2] + self.character + row[self.x + 3: ]

class Cannon:
    def __init__(self, x):
        self.y = canvas_height - 2
        self.x = x
        self.r = 8

    def draw(self, win):
        row = win[self.y]
        win[self.y] = row[: self.x] + [Color.CYAN + ':' + Color.END] + row[self.x + 1: ]
    
    def move(self):
        if self.y > 0:
            self.y -= 1

    def collide(self, alien):
        if self.y == alien.y and abs(self.x - alien.x) <= (alien.character_length//2):
            return True
        return False 

# ターミナルをクリア
os.system('cls' if os.name in ('nt', 'dos') else 'clear')

# alienの初期配置
aliens = []
alien_scores = list(alien_dic.keys())[::-1]
for i, row in enumerate(range(1, 2*(len(alien_scores)), 2)):
    alien_score = alien_scores[i]

    if alien_score == 500:
        column_range = range(2, 30, 5)
    else:
        column_range = range(1, 30, 3)

    for column in column_range:
        aliens.append(Alien(column, row, alien_score))

player = Player(canvas_width//2)
cannons = []

while True:
    if kbhit():
        char = getch()
        if char == "q":
            break
        elif char == "a":
            player.move("left")
        elif char == "d":
            player.move("right")
        elif char == "w":
            cannons.append(Cannon(player.x))

    canvas = [[' ' for j in range(canvas_width)] for i in range(canvas_height)]

    # 衝突判定
    for cannon in cannons:
        for alien in aliens:
            if cannon.collide(alien):
                aliens.remove(alien)
                cannons.remove(cannon)
    
    # alienの描画&移動
    flag = False
    for alien in aliens:
        if ((alien.x + alien.character_length//2) >= canvas_width - 1 and alien.xdir == 1) or ((alien.x - alien.character_length//2) == 0 and alien.xdir == -1):
            flag = True
            break
    for alien in aliens:
        alien.draw(canvas)
        if flag:
            alien.shift_down()
        else:
            alien.move()

    # playerの描画
    player.draw(canvas)

    # cannonの描画&移動
    for cannon in cannons:
        cannon.draw(canvas)
        if cannon.y == 0:
            cannons.remove(cannon)
        else:
            cannon.move()

    # canvasの描画
    output = []
    for row in range(canvas_height):
        output.append(''.join(canvas[row]))
    print('\n'.join(output) + "\n" + f"\033[{canvas_height}A",end="")
    sleep(0.2)


# def drawWindow(ship,drops):
#     ship.draw()

#     for i in drops:
#         i.draw()

#     for b in flowers:
#         b.draw()
#         b.move()  

#     pygame.display.update()

# drops = []
# flowers = []
# shootloop = 0
# for i in range(6):
#     x = i*80 + 80
#     flowers.append(Flower(win,x))
# ship = Ship(win)
# run = True
# while run:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             run = False   

#     keys = pygame.key.get_pressed()

#     if shootloop > 0:
#         shootloop += 1
#     if shootloop > 20:
#         shootloop = 0

#     if keys[pygame.K_SPACE] and shootloop == 0:
#         if len(drops) <= 10:
#             drops.append(Drop(win,ship.x))

#         shootloop = 1

#     for drop in drops:
#         if drop.y > 0:
#             drop.y -= 1
#         else:
#             drops.pop(drops.index(drop))    

#         for flower in flowers:
#             if drop.collide(drop,flower):
#                 flower.grow(flower)
#                 drops.pop(drops.index(drop))

#     for flower in flowers:
#         if flower.x > 600 or flower.x < 0:
#             flower.edge = True

#         if flower.edge:
#             flower.shiftDown()

    # ship.move(keys)
    # win.fill((51,51,51))