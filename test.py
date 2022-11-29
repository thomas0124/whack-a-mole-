import tkinter
import random
import wave
import numpy as np
from PIL import Image, ImageTk

MOLE_PATH = "icon.png"  # モグラの画像のファイルパス
NUM_H_HOLE = 4  # 横方向の穴の数
NUM_V_HOLE = 3  # 縦方向の穴の数
WIDTH_HOLE = 100  # 穴の幅（長軸の長さ）
HEIGHT_HOLE = 50  # 穴の高さ（短軸の長さ）
WIDTH_SPACE = 20  # 穴と穴のスペースの幅
HEIGHT_SPACE = 80  # 穴と穴のスペースの高さ
POINT_DRAW_TIME = 500  # 加算or減算されたポイントが表示される時間
MOLE_UPDATE_INTERVAL = 100  # モグラの状態や位置を更新する時間間隔
FIGURE_UPDATE_INTERVAL = 100  # モグラの画像を更新する時間間隔
MOLE_CHOICE_INTERVAL = 1000  # 穴から出すモグラを決める時間間隔

class Mole:
    def __init__(self, x, y, width, height, speed, figure):
        '''コンストラクタ'''

        self.x = x  # 中央下の位置（横方向）
        self.y = y  # 中央下の位置（縦方向）
        self.width = width  # 画像の幅
        self.height = height  # 画像の高さ

        self.figure = figure  # 描画画像の図形ID

        self.hole_y = y  # モグラが穴に潜る高さ
        self.top_y = self.hole_y - HEIGHT_HOLE / 3  # 穴から出る高さ
        self.speed = speed  # 移動スピード

        self.point = int(speed * 10)  # 叩いた時にゲットできるポイント

        self.is_up = False  # 上方向に移動中かどうかを管理するフラグ
        self.is_draw = True  # 描画するかどうかを管理するフラグ
        self.is_hitted = False  # 既に叩かれているかどうかを管理するフラグ
        self.is_appearing = False  # 穴から出ているかどうかを管理するフラグ

    def appear(self):
        '''モグラを穴から出す'''

        # 穴から出ているフラグをON
        self.is_appearing = True

        # 上方向に移動を開始
        self.is_up = True

    def update(self):
        '''定期的な状態更新を行う'''

        if self.is_up:
            # 上方向への移動中

            # 上方向に移動
            self.y = max(self.top_y, self.y - self.speed)
            if self.y == self.top_y:
                # 上方向の上限まで移動したので下方向への移動を開始
                self.is_up = False
        else:
            # 下方向への移動中

            # 下方向に移動
            self.y = min(self.hole_y, self.y + self.speed)
            if self.y == self.hole_y:
                # モグラがまた穴に潜ってしまった場合

                # モグラの状態をリセットする
                self.is_appearing = False
                self.is_hitted = False
                self.is_draw = True

        if self.is_hitted:
            # 叩かれたフラグが立っている場合

            # 描画実行フラグのON/OFFを切り替える
            self.is_draw = not self.is_draw

    def hit(self):
        '''叩かれた時の処理を実行'''

        # 下方向への移動を開始
        self.is_up = False

        # 叩かれたフラグをセット
        self.is_hitted = True

    def isHit(self, mouse_x, mouse_y):
        '''叩かれたかどうかを判断する'''

        if not self.is_appearing:
            # 穴から出ていない
            return False

        if self.is_hitted:
            # すでに叩かれている
            return False

        # モグラの画像が表示されている領域の座標を計算
        x1 = self.x - self.width / 2
        y1 = self.y - self.height
        x2 = self.x + self.width / 2
        y2 = self.y

        # (mouse_x,mouse_y)が上記領域内であるかどうかを判定
        if x1 <= mouse_x and x2 >= mouse_x:
            if y1 <= mouse_y and y2 >= mouse_y:

                # 領域内をクリックされたので叩かれた
                return True

        # 叩かれなかった
        return False


class WhackaMole:
    def __init__(self, master):
        '''コンストラクタ'''

        # 親ウィジェット
        self.master = master

        # 幅と高さを穴のサイズ・数、スペースのサイズから計算
        self.width = NUM_H_HOLE * (WIDTH_HOLE + WIDTH_SPACE) + WIDTH_SPACE
        self.height = NUM_V_HOLE * (HEIGHT_HOLE + HEIGHT_SPACE) + HEIGHT_SPACE

        self.createWidgets()
        self.drawBackground()
        self.drawHoles()
        self.createMoles()
        self.updateFigures()
        self.choiceMole()
        self.updateMoles()

    def createWidgets(self):
        '''ウィジェットの作成と配置を行う'''

        # キャンバスの作成と配置
        self.canvas = tkinter.Canvas(
            self.master,
            width=self.width,
            height=self.height,
            highlightthickness=0
        )
        self.canvas.pack()

        # ラベルの作成と配置
        self.label = tkinter.Label(
            self.master,
            font=("", 40),
            text="0"
        )
        self.label.pack()

    def drawBackground(self):
        '''背景を描画する'''

        # キャンバス全面に緑色の長方形を描画
        self.bg = self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill="green"
        )

    def drawHoles(self):
        '''穴を描画する'''

        # 空の管理リストを作成
        self.hole_coords = []

        for v in range(NUM_V_HOLE):
            for h in range(NUM_H_HOLE):

                # 穴の中心座標を計算
                x = h * (WIDTH_HOLE + WIDTH_SPACE) + WIDTH_SPACE + WIDTH_HOLE / 2
                y = v * (HEIGHT_HOLE + HEIGHT_SPACE) + HEIGHT_SPACE + HEIGHT_HOLE / 2

                # 穴の左上と右下座標を計算
                x1 = x - WIDTH_HOLE / 2
                y1 = y - HEIGHT_HOLE / 2
                x2 = x + WIDTH_HOLE / 2
                y2 = y + HEIGHT_HOLE / 2

                # 穴を楕円として描画
                self.canvas.create_oval(
                    x1, y1, x2, y2,
                    fill="black"
                )

                # 管理リストに追加
                self.hole_coords.append((x, y))

    def createMoles(self):
        '''モグラを作成して表示する'''

        # モグラの画像を読み込む
        image = Image.open(MOLE_PATH)

        # 不要な画像の外側の透明画素を除去
        cropped_image = image.crop(image.getbbox())

        # 穴の幅に合わせて画像を拡大縮小
        ratio = (WIDTH_HOLE - 20) / cropped_image.width
        resize_size = (
            round(ratio * cropped_image.width),
            round(ratio * cropped_image.height)
        )
        resized_image = cropped_image.resize(resize_size)

        # tkinter用の画像オブジェクトに変換
        self.mole_image = ImageTk.PhotoImage(resized_image)

        self.moles = []

        for coord in self.hole_coords:

            # 穴の座標を取得
            x, y = coord

            # 穴の中心にモグラの画像の下が接するように画像を描画
            figure = self.canvas.create_image(
                x, y,
                anchor=tkinter.S,
                image=self.mole_image
            )

            # 描画した画像を背景画像の下側に隠す
            self.canvas.lower(figure, "all")

            # モグラオブジェクトを作成
            width = self.mole_image.width()
            height = self.mole_image.height()
            mole = Mole(x, y, width, height, 1, figure)

            # モグラオブジェクトを管理リストに追加
            self.moles.append(mole)

            # 描画画像がクリックされた時にonClickが実行されるように設定
            self.canvas.tag_bind(figure, "<ButtonPress>", self.onClick)

    def updateFigures(self):
        '''モグラの画像を更新する'''

        for mole in self.moles:

            if mole.is_appearing and mole.is_draw:
                # 出現中&描画フラグONの画像の場合

                # モグラの画像を最前面に移動
                self.canvas.lift(mole.figure, "all")

                # モグラの位置を更新
                self.canvas.coords(mole.figure, mole.x, mole.y)
            else:
                # モグラの画像を最背面に移動
                self.canvas.lower(mole.figure, "all")

        # FIGURE_UPDATE_INTERVAL後に再度モグラの状態を更新
        self.master.after(FIGURE_UPDATE_INTERVAL, self.updateFigures)

    def choiceMole(self):
        '''選んだモグラを穴から出させる'''

        # 穴に隠れているモグラだけのリストを作成
        hide_moles = []
        for mole in self.moles:
            if not mole.is_appearing:
                hide_moles.append(mole)

        if len(hide_moles) != 0:
            # 穴に隠れているモグラがいる場合

            # ランダムにモグラを１つ選んで穴から出させる
            mole = random.choice(hide_moles)
            mole.appear()

        # MOLE_CHOICE_INTERVAL後に再度別のモグラを穴から出させる
        self.master.after(MOLE_CHOICE_INTERVAL, self.choiceMole)

    def updateMoles(self):
        '''モグラの状態や位置を更新する'''

        for mole in self.moles:

            # 更新前のモグラの状態を退避
            is_hitted = mole.is_hitted
            before_appearing = mole.is_appearing

            # モグラの状態や位置を更新する
            mole.update()

            # 更新後にモグラが隠れたかどうかのフラグを取得
            after_appearing = mole.is_appearing

            if not is_hitted and before_appearing and not after_appearing:
                # moleが叩かれていない＆上記のupdateメソッドによりmoleが穴に潜り込んだ場合

                # ポイントの加算と加算ポイントの描画
                self.pointUp(-mole.point)
                self.drawPoint(-mole.point, mole.x, mole.y)

        # MOLE_UPDATE_INTERVAL後に再度モグラの状態を更新
        self.master.after(MOLE_UPDATE_INTERVAL, self.updateMoles)

    def onClick(self, event):
        '''クリックされた時の処理を実行する'''

        for mole in self.moles:

            # moleの画像がクリックされたかどうかを判断
            if mole.isHit(event.x, event.y):
                # クリックされた場合

                # moleを叩く
                mole.hit()

                # ポイントの加算と加算ポイントの描画
                self.pointUp(mole.point)
                self.drawPoint(mole.point, event.x, event.y)

    def pointUp(self, point):
        '''ポイントを加算する'''

        # ラベルに表示されているポイントを取得
        now_point = int(self.label.cget("text"))

        # 取得したポイントに加算して表示文字列に設定
        now_point += point
        self.label.config(text=str(now_point))

    def drawPoint(self, point, x, y):
        '''加算されたポイントを表示'''

        if point >= 0:
            sign = "+"
            color = "yellow"
        else:
            sign = "-"
            color = "red"

        point_figure = self.canvas.create_text(
            x, y,
            text=sign + str(abs(point)),
            fill=color,
            font=("", 40)
        )

        # DRAW_TIME_POINT後に描画した文字列を削除
        self.master.after(
            POINT_DRAW_TIME, lambda: self.canvas.delete(point_figure))


app = tkinter.Tk()
game = WhackaMole(app)
app.mainloop()