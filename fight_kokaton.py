import os
import random
import sys
import time
import math
import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
NUM_OF_BOMBS = 5
NUM_OF_BEAMS = 5


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとん，または，爆弾SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        img0 = pg.transform.rotozoom(pg.image.load(
            f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
        self.imgs = {  # 0度から反時計回りに定義
            (+5, 0): img,  # 右
            (+5, -5): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -5): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-5, 0): img0,  # 左
            (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +5): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+5, +5): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        # img1 = pg.transform.rotozoom(pg.image.load(
        #     f"{MAIN_DIR}/fig/beam.png"), 0, 2.0)
        # img2 = pg.transform.flip(img1, True, False)
        # self.dires = {  # 0度から反時計回りに定義
        #     (+5, 0): img2,  # 右
        #     (+5, -5): pg.transform.rotozoom(img2, 45, 1.0),  # 右上
        #     (0, -5): pg.transform.rotozoom(img2, 90, 1.0),  # 上
        #     (-5, -5): pg.transform.rotozoom(img1, -45, 1.0),  # 左上
        #     (-5, 0): img1,  # 左
        #     (-5, +5): pg.transform.rotozoom(img1, 45, 1.0),  # 左下
        #     (0, +5): pg.transform.rotozoom(img2, -90, 1.0),  # 下
        #     (+5, +5): pg.transform.rotozoom(img2, -45, 1.0),  # 右下
        # }
        # self.img = pg.transform.flip(  # 左右反転
        #     pg.transform.rotozoom(  # 2倍に拡大
        #         pg.image.load(f"{MAIN_DIR}/fig/{num}.png"),
        #         0,
        #         2.0),
        #     True,
        #     False
        # )
        self.img = self.imgs[(+5, 0)]  # 右向き
        self.rct = self.img.get_rect()
        self.rct.center = xy
        self.dire = (+5, 0)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(
            pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)

        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])

        if not (sum_mv[0] == 0 and sum_mv[1] == 0):  # 何もキーが押されていなくなかったら
            self.img = self.imgs[tuple(sum_mv)]
            self.dire = tuple(sum_mv)

        screen.blit(self.img, self.rct)


class Bomb:
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
              (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    """
    爆弾に関するクラス
    """

    def __init__(self):
        """
        引数に基づき爆弾円Surfaceを生成する
        """
        rad = random.randint(10, 100)
        self.img = pg.Surface((2*rad, 2*rad))
        color = random.choice(Bomb.colors)

        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Beam:

    def __init__(self, bird):
        # 角度を計算
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        # 映像を回転
        self.img = pg.transform.rotozoom(pg.image.load(
            f"{MAIN_DIR}/fig/beam.png"), angle, 1.0)
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery  # こうかとんの中心の座標取得
        self.rct.centerx = bird.rct.centerx + bird.rct.width/2

        self.rct = self.img.get_rect()
        # ビームの座標
        self.rct.centerx = bird.rct.centerx + bird.rct.width * self.vx // 5
        self.rct.centery = bird.rct.centery + bird.rct.height * self.vy // 5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class ScoreBoard:
    """
    機能３：撃ち落とした爆弾の数を表示するスコアクラス
    """

    def __init__(self, all_bomb: int):
        self.all_bomb = all_bomb  # Total number of bombs in the game
        self.killed_bombs = 0  # Count of bombs that have been shot down
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)  # フォントオブジェクトを作成する
        self.text_color = (0, 0, 255)

    def count_score(self, active_bomb: int):
        """
        撃ち落とした爆弾の数を計算する
        """
        self.killed_bombs = self.all_bomb - active_bomb
        return self.killed_bombs

    def display_score(self, screen: pg.Surface):
        """
        スコアを表示する
        """
        # 色を定義する
        black = (0, 0, 0)
        white = (255, 255, 255)
        font = pg.font.Font('freesansbold.ttf', 32)  # フォントオブジェクトを作成する
        text = self.font.render(
            f"score:{self.killed_bombs}", True, self.text_color)
        textRect = text.get_rect()
        textRect.center = (70, 50)
        screen.blit(text, textRect)


class BombEffect:
    """
    機能１：爆弾撃ち落とした時の爆発エフェクトクラス
    """

    def __init__(self, bomb: Bomb, duration=3000):
        self.bomb = bomb
        self.img = pg.image.load(f"{MAIN_DIR}/fig/explosion.gif")
        self.rct = self.img.get_rect()
        self.rct.centery = bomb.rct.centery
        self.rct.centerx = bomb.rct.centerx
        self.duration = duration
        self.start_time = pg.time.get_ticks()

    def boom_effect(self, screen):
        current_time = pg.time.get_ticks()
        if current_time - self.start_time < self.duration:
            screen.blit(self.img, self.rct)
            return True
        else:
            return False


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    bombs = [Bomb() for _ in range(NUM_OF_BOMBS)]  # Bombインスタンス
    bomb_counter = ScoreBoard(NUM_OF_BOMBS)
    beams = []  # ビームに空きリスト
    bomb_effects = []  # 爆発に空きリスト

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))

        screen.blit(bg_img, [0, 0])
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return

        for i, bomb in enumerate(bombs):
            for j, beam in enumerate(beams):
                if beam.rct.colliderect(bomb.rct):
                    bombs[i] = None
                    beams[j] = None
                    bird.change_img(6, screen)
                    bomb_effect = BombEffect(bomb)
                    bomb_effects.append(bomb_effect)
            # Noneでない爆弾だけをリスト化
            bombs = [bomb for bomb in bombs if bomb is not None]
            # Noneでないビームだけをリスト化
            beams = [beam for beam in beams if beam is not None]
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        for bomb in bombs:
            bomb.update(screen)
        for beam in beams:
            beam.update(screen)
        bomb_counter.count_score(len(bombs))
        bomb_counter.display_score(screen)

        bomb_effects = [
            effect for effect in bomb_effects if effect.boom_effect(screen)]
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
