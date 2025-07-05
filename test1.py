import tkinter as tk
from PIL import Image, ImageTk
import time
from config import YES, YES_WAIT, YES_SELECTED
from config import NO, NO_SELECTED, NO_WAIT
from config import BUTTON_SIZE, HOVER_TIME, ARC_RADIUS
from config import CANDIDATES_WHIDTH, CANDIDATES_HEIGHT
from config import CANDIDATES_1, CANDIDATES_1_SELECTED, CANDIDATES_1_WAIT_SELECTED, CANDIDATES_1_WAIT

class makeButton:
    def __init__(self, canvas, img_path, wait_path, wait_selected_path, selected_path, area, cmd, step):
        self.canvas = canvas

        #self.root = tk.Tk()
        #self.canvas = tk.Canvas(self.root, width=500, height=500)
        
        width  = int(area[2] - area[0])
        height = int(area[3] - area[1])
        self.img               = ImageTk.PhotoImage(Image.open(img_path).resize((width, height)))
        self.img_wait          = ImageTk.PhotoImage(Image.open(wait_path).resize((width, height)))
        self.img_wait_selected = ImageTk.PhotoImage(Image.open(wait_selected_path).resize((width, height)))
        self.img_selected      = ImageTk.PhotoImage(Image.open(selected_path).resize((width, height)))

        self.img_default = self.img_wait#reset()を実行したときの見た目
        self.my_step    = step#自分はステップいくつか
        self.my_cmd     = cmd#自分のコマンドは何か
        self.clicked    = None#クリックされているか
        self.area       = area
        self.stay_time  = HOVER_TIME#滞留時間
        self.enter_time = None#領域内にカーソルが入った時刻
        self.arc_id     = None#アークのキャンパスID
        self.arc_radius = ARC_RADIUS#半径
        self.cmd        = cmd#コマンド(半角一文字)

        self.image_id = self.canvas.create_image(area[0], area[1], image = self.img_default, anchor="nw")#初期描画

    def reset(self):
        self.enter_time = None
        self.clicked    = False
        self.canvas.itemconfig(self.image_id, image=self.img_default)
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None
    
    def draw_arc(self, x, y, percent):
        if self.arc_id:
            self.canvas.delete(self.arc_id)
        angle = percent * 3.6
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius,
            x + self.arc_radius, y + self.arc_radius,
            start = 90, extent=-angle, style = 'pieslice',
            outline = 'black', fill = 'blue'
        )

    def update(self, cursor_x, cursor_y, step, select):
        if step == 3:#二回目の確認の段階、選択不可
            if self.my_cmd != select:#自分が選択されていないとき
                self.img_default = self.img
            elif self.my_cmd == select:#自分が選択されているとき
                self.img_default = self.img_selected
            if self.enter_time or self.arc_id:#アークを消す
                self.enter_time = None
                if self.arc_id:
                    self.canvas.delete(self.arc_id)
                    self.arc_id = None
            self.reset()
            return select, 3
        x1, y1, x2, y2 = self.area
        if self.my_cmd == select:
            self.img_default=self.img_wait_selected
        else:
            self.img_default = self.img_wait
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:#カーソルが領域内部なら
            #アークの描画
            if self.my_cmd != select:
                if self.enter_time is None:
                    self.enter_time = time.time()
                elapsed = time.time() - self.enter_time#滞留時間
                percent = min(elapsed / self.stay_time * 100, 100)
                self.draw_arc(cursor_x + 40, cursor_y, percent)

                if elapsed >= self.stay_time:#一定時間滞留したら
                    #print(f'{self.cmd}')
                        #self.canvas.itemconfig(self.image_id, image = self.img_wait_selected)
                        #self.img_default = self.img_wait_selected
                        #self.clicked = True
                    if self.arc_id:
                        self.canvas.delete(self.arc_id)
                        self.arc_id = None
                    self.enter_time = None    
                    self.img_default = self.img_wait_selected
                    self.canvas.itemconfig(self.image_id, image = self.img_wait_selected)

                    return self.cmd, 2#選んだら次は確認１回目
            else:
                if self.arc_id:
                    self.canvas.delete(self.arc_id)
                    self.arc_id = None
        else:#カーソルが領域外なら
            self.enter_time = None
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None
            self.reset()
        return select, 2

#はいボタン、いいえボタンは候補者ボタンと動作が少し異なるため、継承しちょっと変える
class makeYesNoButton(makeButton):
    def __init__(self, canvas, img_path, wait_path, wait_selected_path, selected_path, area, cmd, step):
        super().__init__(canvas, img_path, wait_path, wait_selected_path, selected_path, area, cmd, step)
        self.clicked = None

    def reset(self):
        self.enter_time = None
        self.canvas.itemconfig(self.image_id, image=self.img_default)
        if self.arc_id:
            self.canvas.delete(self.arc_id)
            self.arc_id = None

    def update(self, cursor_x, cursor_y, step, select):
        #ステップ管理
        x1, y1, x2, y2 = self.area
        if self.my_step != step:
            if self.my_cmd != select:
                self.img_default = self.img
            elif self.my_cmd == select:
                self.img_default = self.img_selected
            if self.enter_time or self.arc_id:
                self.enter_time = None
                if self.arc_id:
                    self.canvas.delete(self.arc_id)
                    self.arc_id = None
            self.reset()
            return select, step
        #カーソル管理
        x1, y1, x2, y2 = self.area
        if self.my_cmd == select:
            self.img_default=self.img_wait_selected
        else:
            self.img_default = self.img_wait
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:#カーソルが領域内部なら
            #アークの描画
            if not self.clicked:
                if self.enter_time is None:
                    self.enter_time = time.time()
                elapsed = time.time() - self.enter_time#滞留時間
                percent = min(elapsed / self.stay_time * 100, 100)
                self.draw_arc(cursor_x + 40, cursor_y, percent)

                if elapsed >= self.stay_time:#一定時間滞留したら
                    #print(f'{self.cmd}')
                        #self.canvas.itemconfig(self.image_id, image = self.img_wait_selected)
                        #self.img_default = self.img_wait_selected
                    if self.arc_id:
                        self.canvas.delete(self.arc_id)
                        self.arc_id = None
                    self.enter_time = None    
                    self.clicked = True
                    self.img_default = self.img_selected
                    self.canvas.itemconfig(self.image_id, image = self.img_default)

                    return select, 3
            else:
                if self.arc_id:
                    self.canvas.delete(self.arc_id)
                    self.arc_id = None
                self.reset()
        else:#カーソルが領域外なら
            self.enter_time = None
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None
            self.reset()
        return select, 2

class GUIApp():
    def __init__(self):
        self.step = 1#現在のステップ
        self.select = None#選ばれた候補者 初期値はNone(誰も選ばれていない)

        self.root = tk.Tk()
        self.root.state("zoomed")
        self.root.update_idletasks()#ウィンドウ準備完了を待つ
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)#canvas = window

        #ボタンの設定(通常, 待機, 待機選択, 選択, 中心X割合, 中心Y割合, 横長さ, 縦長さ, コマンド, step)
        button_list = [
            (CANDIDATES_1, CANDIDATES_1_WAIT, CANDIDATES_1_WAIT_SELECTED,CANDIDATES_1_SELECTED,  6/100,5/10,CANDIDATES_WHIDTH, CANDIDATES_HEIGHT,'1',1),
            (CANDIDATES_1, CANDIDATES_1_WAIT, CANDIDATES_1_WAIT_SELECTED,CANDIDATES_1_SELECTED, 17/100,5/10,CANDIDATES_WHIDTH, CANDIDATES_HEIGHT,'2',1),
            (CANDIDATES_1, CANDIDATES_1_WAIT, CANDIDATES_1_WAIT_SELECTED,CANDIDATES_1_SELECTED, 28/100,5/10,CANDIDATES_WHIDTH, CANDIDATES_HEIGHT,'3',1),
            (CANDIDATES_1, CANDIDATES_1_WAIT, CANDIDATES_1_WAIT_SELECTED,CANDIDATES_1_SELECTED, 39/100,5/10,CANDIDATES_WHIDTH, CANDIDATES_HEIGHT,'4',1),
            (CANDIDATES_1, CANDIDATES_1_WAIT, CANDIDATES_1_WAIT_SELECTED,CANDIDATES_1_SELECTED, 50/100,5/10,CANDIDATES_WHIDTH, CANDIDATES_HEIGHT,'5',1),
            (YES, YES_WAIT, YES_SELECTED, YES_SELECTED, 75/100, 3/8, BUTTON_SIZE, BUTTON_SIZE,'y1',2),
            (NO , NO_WAIT ,  NO_SELECTED,  NO_SELECTED, 90/100, 3/8, BUTTON_SIZE, BUTTON_SIZE,'n1',2),
            (YES, YES_WAIT, YES_SELECTED, YES_SELECTED, 75/100, 6/8, BUTTON_SIZE, BUTTON_SIZE,'y2',3),
            (NO , NO_WAIT ,  NO_SELECTED,  NO_SELECTED, 90/100, 6/8, BUTTON_SIZE, BUTTON_SIZE,'n2',3),
        ]
        
        self.buttons = []
        for img_path, wait_path, wait_selected_path, selected_path, center_x_ratio, center_y_ratio, w, h, cmd, step in button_list:
            center_x = center_x_ratio * self.width
            center_y = center_y_ratio * self.height
            area = self.calc_area(center_x, center_y, w, h)
            if cmd == 'y1' or cmd == 'n1' or cmd == 'y2' or cmd == 'n2' :
                self.buttons.append(makeYesNoButton(self.canvas, img_path, wait_path, wait_selected_path, selected_path, area, cmd, step))
            else:
                self.buttons.append(makeButton(self.canvas, img_path, wait_path, wait_selected_path, selected_path,  area, cmd, step))
        
        self.check_cursor()

    def calc_area(self, center_x, center_y, width, height):
        half_width = width // 2
        half_height = height // 2
        return (center_x - half_width, center_y - half_height, center_x + half_width, center_y + half_height)

    def check_cursor(self):
        """
        カーソル位置を定期的に取得
        """
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()
        current_selection = self.select#self.selectは途中で変わる可能性あり.代入しておく
        for button in self.buttons:
                result, next_step = button.update(x,y,self.step,self.select)
                if next_step == 1:
                    self.step = 1
                elif next_step == 2:
                    self.step = 2
                elif next_step == 3:
                    self.step = 3
                elif next_step == 4:
                    print('finish!!')
        self.root.after(20, self.check_cursor)
    
    def run(self):
        self.root.mainloop()
    
def main():
    app = GUIApp()
    app.run()
if __name__ == '__main__':
    main()
