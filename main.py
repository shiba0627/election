import tkinter as tk
from PIL import Image, ImageTk
import time
from config import YES, YES_WAIT, YES_CLICKED
from config import NO, NO_CLICKED, NO_WAIT
from config import BUTTON_SIZE, HOVER_TIME, ARC_RADIUS
from config import CANDIDATES_WHIDTH, CANDIDATES_HEIGHT
from config import CANDIDATES_1, CANDIDATES_1_CLICKED, CANDIDATES_1_WAIT

class makeButton:
    def __init__(self, canvas, img_path, dark_path, lock_path, attention_path, area, cmd, step):
        self.canvas = canvas

        #self.root = tk.Tk()
        #self.canvas = tk.Canvas(self.root, width=500, height=500)
        
        width = int(area[2] - area[0])
        height = int(area[3]-area[1])
        self.img           = ImageTk.PhotoImage(Image.open(img_path).resize((width, height)))
        self.img_dark      = ImageTk.PhotoImage(Image.open(dark_path).resize((width, height)))
        self.img_lock      = ImageTk.PhotoImage(Image.open(lock_path).resize((width, height)))
        self.img_attention = ImageTk.PhotoImage(Image.open(attention_path).resize((width, height)))
        
        self.area = area
        self.stay_time = HOVER_TIME#滞留時間
        self.enter_time = None#領域内にカーソルが入った時刻
        self.clicked = False#クリック状態か
        self.locked = False#ロック状態か
        self.arc_id = None#アークのキャンパスID
        self.arc_radius = ARC_RADIUS#半径
        self.cmd = cmd#コマンド(半角一文字)
        self.step = 1#現在の段階

        self.image_id = self.canvas.create_image(area[0], area[1], image = self.img, anchor="nw")#描画
    
    def reset(self):
        self.enter_time = None
        self.clicked = False
        self.locked = False
        self.canvas.itemconfig(self.image_id, image=self.img)
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
            outline = 'black', fill = 'black'
        )
        self.canvas.itemconfig(self.image_id, image = self.img_attention)

        
    
    def update(self, cursor_x, cursor_y):
        x1, y1, x2, y2 = self.area
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:
            if not self.clicked:#クリック状態でないなら(滞留中なら)
                if self.enter_time is None:
                    self.enter_time = time.time()
                elapsed = time.time() - self.enter_time#滞留時間
                percent = min(elapsed / self.stay_time * 100, 100)
                self.draw_arc(cursor_x + 40, cursor_y, percent)

                if elapsed >= self.stay_time:
                    print(f'{self.cmd}')
                    self.canvas.itemconfig(self.image_id, image = self.img_dark)
                    self.clicked = True
                    if self.arc_id:
                        self.canvas.delete(self.arc_id)
                        self.arc_id = None
        else:
            self.reset()

class GUIApp():
    def __init__(self):
        self.root = tk.Tk()
        self.root.state("zoomed")
        self.root.update_idletasks()#ウィンドウ準備完了を待つ
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)#canvas = window

        #ボタンの設定(通常, dark, ロック, 滞留中, 中心X, 中心Y, 横長さ, 縦長さ, コマンド, 段階)
        button_list = [
            (CANDIDATES_1, CANDIDATES_1_CLICKED, CANDIDATES_1,CANDIDATES_1_WAIT,  6/100,5/10,CANDIDATES_WHIDTH, CANDIDATES_HEIGHT,'1',1),
            (CANDIDATES_1, CANDIDATES_1_CLICKED, CANDIDATES_1,CANDIDATES_1_WAIT, 17/100,5/10,CANDIDATES_WHIDTH, CANDIDATES_HEIGHT,'2',1),
            (CANDIDATES_1, CANDIDATES_1_CLICKED, CANDIDATES_1,CANDIDATES_1_WAIT, 28/100,5/10,CANDIDATES_WHIDTH, CANDIDATES_HEIGHT,'3',1),
            (CANDIDATES_1, CANDIDATES_1_CLICKED, CANDIDATES_1,CANDIDATES_1_WAIT, 39/100,5/10,CANDIDATES_WHIDTH, CANDIDATES_HEIGHT,'4',1),
            (CANDIDATES_1, CANDIDATES_1_CLICKED, CANDIDATES_1,CANDIDATES_1_WAIT, 50/100,5/10,CANDIDATES_WHIDTH, CANDIDATES_HEIGHT,'5',1),
            (CANDIDATES_1, CANDIDATES_1_CLICKED, CANDIDATES_1,CANDIDATES_1_WAIT, 61/100,5/10,CANDIDATES_WHIDTH, CANDIDATES_HEIGHT,'6',1),
            (YES, YES_CLICKED, YES, YES_WAIT, 75/100, 3/8, BUTTON_SIZE, BUTTON_SIZE,'a',2),
            (NO , NO_CLICKED ,  NO,  NO_WAIT, 90/100, 3/8, BUTTON_SIZE, BUTTON_SIZE,'b',2),
            (YES, YES_CLICKED, YES, YES_WAIT, 75/100, 6/8, BUTTON_SIZE, BUTTON_SIZE,'c',3),
            (NO , NO_CLICKED ,  NO,  NO_WAIT, 90/100, 6/8, BUTTON_SIZE, BUTTON_SIZE,'d',3),
        ]
        
        self.buttons = []
        for img_path, clicked_path, lock_path, attention_path, center_x_ratio, center_y_ratio, w,h,char,step in button_list:
            center_x = center_x_ratio * self.width
            center_y = center_y_ratio * self.height
            area = self.calc_area(center_x, center_y, w, h)
            self.buttons.append(makeButton(self.canvas, img_path, clicked_path, lock_path, attention_path, area, char, step))
        
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
        for button in self.buttons:
            button.update(x,y)
        self.root.after(20, self.check_cursor)
    
    def run(self):
        self.root.mainloop()
    
def main():
    app = GUIApp()
    app.run()
if __name__ == '__main__':
    main()
