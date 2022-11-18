import argparse
import os
from time import sleep
from kbhit import *
import random
import wiringpi as wp

wp.wiringPiSetupSys()

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
    RETURN = '\033[07m'  # 反転
    ACCENT = '\033[01m'  # 強調
    FLASH = '\033[05m'  # 点滅
    RED_FLASH = '\033[05;41m'  # 赤背景+点滅
    END = '\033[0m'


# {score: character}
alien_dic = {
    100: [Color.BLUE + '_', 'x', '_' + Color.END],
    150: [Color.GREEN + '<', 'O', '>' + Color.END],
    200: [Color.RED + 'o', '=', 'o' + Color.END],
    500: [Color.PURPLE + '<', 'o', ' ', 'o', '>' + Color.END]
}

canvas_width = 50
canvas_height = 15


class Alien:
    def __init__(self, x: int, y: int, score: int):
        self.x = x
        self.y = y
        self.xdir = 1
        self.radius = 1
        self.score = score
        self.character_list = alien_dic[score]
        self.character_length = len(self.character_list)

    def draw(self, win):
        row = win[self.y]
        row_before = row[:self.x - (self.character_length // 2)]
        row_after = row[self.x + (1 + self.character_length // 2):]
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
        win[-1] = row[: self.x - 2] + self.character + row[self.x + 3:]


class Cannon:
    def __init__(self, x, y, ydir):
        self.y = y
        self.ydir = ydir
        self.x = x

    def draw(self, win):
        row = win[self.y]
        if self.ydir == -1:
            win[self.y] = row[: self.x] + ['!'] + row[self.x + 1:]
        else:
            win[self.y] = row[: self.x] + \
                [Color.CYAN + ':' + Color.END] + row[self.x + 1:]

    def move(self):
        if self.y > 0 and self.y < canvas_height - 1:
            self.y += self.ydir

    def collide_alien(self, alien):
        if self.y == alien.y and abs(
                self.x -
                alien.x) <= (
                alien.character_length //
                2):
            return True
        return False

    def collide_player(self, player):
        if self.y == canvas_height - 1 and abs(self.x - player.x) <= 2:
            return True
        return False


def fire(alien, canvas, prob):
    if alien.y + 2 < canvas_height and canvas[alien.y + 2][alien.x] == ' ':
        if random.random() <= prob:
            return True
    return False


# ゲームオーバー画面
game_over_title = """
  ___    _    __  __  ___
 / __|  /_\\  |  \\/  || __|
| (_ | / _ \\ | |\\/| || _|
 \\___|/_/ \\_\\|_|  |_||___|

  ___  __   __ ___  ___
 / _ \\ \\ \\ / /| __|| _ \\
| (_) | \\ V / | _| |   /
 \\___/   \\_/  |___||_|_\\
"""

# ゲームクリア画面
game_clear_title = """
  ___    _    __  __  ___
 / __|  /_\\  |  \\/  || __|
| (_ | / _ \\ | |\\/| || _|
 \\___|/_/ \\_\\|_|  |_||___|

  ___  _     ___    _    ___
 / __|| |   | __|  /_\\  | _ \\
| (__ | |__ | _|  / _ \\ |   /
 \\___||____||___|/_/ \\_\\|_|_\\
"""


def main(args):
    # ターミナルをクリア
    os.system('cls' if os.name in ('nt', 'dos') else 'clear') 

    pin_led = [5, 6, 13]
    pin_sw = [19, 26, 21]

    for pin in pin_led:
        wp.pinMode(pin, wp.GPIO.OUTPUT)

    for pin in pin_sw:
        wp.pinMode(pin, wp.GPIO.OUTPUT)

    # スタート画面
    canvas = [[' ' for j in range(canvas_width)] for i in range(canvas_height)]
    left_up = (2, 4)
    # トップ画面
    title = """
 ___
/ __| _ __  __ _  __  ___
\\__ \\| '_ \\/ _` |/ _|/ -_)
|___/| .__/\\__,_|\\__|\\___|
     |_|
 ___                      _
|_ _| _ _  __ __ __ _  __| | ___  _ _  ___
 | | | ' \\ \\ V // _` |/ _` |/ -_)| '_|(_-<
|___||_||_| \\_/ \\__,_|\\__,_|\\___||_|  /__/
"""
    for i, row in enumerate(title.split('\n')):
        for j, char in enumerate(row):
            if char:
                canvas[left_up[0] + i][left_up[1] + j] = char
    output = []
    for row in range(canvas_height):
        output.append(''.join(canvas[row]))
    flash_flag = True
    while True:
        state = [wp.digitalRead(pin) for pin in pin_sw]
        if any(state):
            break

        flash_message = " " * 50
        if flash_flag:
            flash_message = " " * 18 + "press to start" + " " * 18
        flash_flag = not flash_flag

        print(
            '\n'.join(output) +
            "\n" +
            f"{flash_message}\n" +
            f"\033[{canvas_height+1}A",
            end="")
        sleep(0.5)

    # alienの初期配置
    aliens = []
    alien_scores = list(alien_dic.keys())[::-1]
    for i, row in enumerate(range(1, 2 * (len(alien_scores)), 2)):
        alien_score = alien_scores[i]

        if alien_score == 500:
            column_range = range(2, 30, 5)
        else:
            column_range = range(1, 30, 3)

        for column in column_range:
            aliens.append(Alien(column, row, alien_score))

    player = Player(canvas_width // 2)
    cannons = []
    time_left = 3

                
    for pin in pin_led:
        wp.digitalWrite(pin, 1)

    diff_prob_dict = {"easy": 0.01, "medium": 0.03, "hard": 0.1}
    prob = diff_prob_dict[args.diff]
    score = 0
    game_over = False
    
    last_state = [False]*3

    while True:
        new_state = [wp.digitalRead(pin) for pin in pin_sw]
        if (new_state[1] == False) and (last_state[1] == True):
            cannons.append(Cannon(player.x, canvas_height - 2, -1))
        elif (new_state[0] == False) and (last_state[0] == True):
            player.move("left")
        elif (new_state[2] == False) and (last_state[2] == True):
            player.move("right")

        canvas = [[' ' for j in range(canvas_width)]
                  for i in range(canvas_height)]

        # 終了判定
        if len(aliens) == 0:
            break
        for alien in aliens:
            if alien.y == canvas_height - 1:
                game_over = True

        # 衝突判定
        for cannon in cannons:
            for alien in aliens:
                if cannon.ydir == -1 and cannon.collide_alien(alien):
                    score += alien.score
                    aliens.remove(alien)
                    cannons.remove(cannon)
            if cannon.ydir == 1 and cannon.collide_player(player):
                time_left -= 1
                
                for i, pin in enumerate(pin_led):
                    if i < time_left:
                        wp.digitalWrite(pin, 1)
                    else:
                        wp.digitalWrite(pin, 0)
                
                if time_left <= 0:
                    game_over = True

        if game_over:
            break

        # alienの描画&移動
        flag = False
        for alien in aliens:
            if ((alien.x +
                 alien.character_length //
                 2) >= canvas_width -
                1 and alien.xdir == 1) or ((alien.x -
                                            alien.character_length //
                                            2) == 0 and alien.xdir == -
                                           1):
                flag = True
                break
        for alien in aliens:
            alien.draw(canvas)

        for alien in aliens:
            if fire(alien, canvas, prob):
                cannons.append(Cannon(alien.x, alien.y + 1, 1))

            if flag:
                alien.shift_down()
            else:
                alien.move()

        # playerの描画
        player.draw(canvas)

        # cannonの描画&移動
        for cannon in cannons:
            cannon.draw(canvas)
            if cannon.y == 0 or cannon.y == canvas_height - 1:
                cannons.remove(cannon)
            else:
                cannon.move()

        # canvasの描画
        output = []
        for row in range(canvas_height):
            output.append(''.join(canvas[row]))
        print(
            '\n'.join(output) +
            "\n" +
            f"SCORE : {score}\n" +
            f"\033[{canvas_height+1}A",
            end="")

        last_state = new_state
        sleep(0.2)


    canvas = [[' ' for j in range(canvas_width)] for i in range(canvas_height)]

    if game_over:
        left_up = (2, 11)
        title = game_over_title
    else:
        left_up = (2, 10)
        title = game_clear_title

    for i, row in enumerate(title.split('\n')):
        for j, char in enumerate(row):
            if char:
                canvas[left_up[0] + i][left_up[1] + j] = char
    output = []
    for row in range(canvas_height):
        output.append(''.join(canvas[row]))
    flash_flag = True
    while True:
        state = [wp.digitalRead(pin) for pin in pin_sw]
        if any(state):
            break

        flash_message = " " * 50
        if flash_flag:
            flash_message = " " * 18 + "press to end" + " " * 18
        flash_flag = not flash_flag

        print(
            '\n'.join(output) +
            "\n" +
            f"{flash_message}\n" +
            f"\033[{canvas_height+1}A",
            end="")
        sleep(0.5)
    
    os.system('cls' if os.name in ('nt', 'dos') else 'clear')
    for pin in pin_led:
        wp.digitalWrite(pin, wp.GPIO.LOW)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--diff',
        default="easy",
        help="the game difficulty (easy | medium | hard)",
        type=str)

    args = parser.parse_args()
    main(args)
