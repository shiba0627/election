import tkinter as tk
from PIL import Image, ImageTk
import time
from config import YES, YES_WAIT, YES_SELECTED, NO, NO_SELECTED, NO_WAIT
from config import BUTTON_SIZE, HOVER_TIME, ARC_RADIUS, CANDIDATES_WHIDTH, CANDIDATES_HEIGHT
from config import CANDIDATES_1, CANDIDATES_1_SELECTED, CANDIDATES_1_WAIT_SELECTED, CANDIDATES_1_WAIT

# ボタンの親クラス
class BaseButton:
    def __init__(self, canvas, img_path, wait_path, wait_selected_path, selected_path, area, cmd, step):
        self.canvas = canvas
        width, height = int(area[2] - area[0]), int(area[3] - area[1])

        self.img               = ImageTk.PhotoImage(Image.open(img_path).resize((width, height)))
        self.img_wait          = ImageTk.PhotoImage(Image.open(wait_path).resize((width, height)))
        self.img_wait_selected = ImageTk.PhotoImage(Image.open(wait_selected_path).resize((width, height)))
        self.img_selected      = ImageTk.PhotoImage(Image.open(selected_path).resize((width, height)))

        # パラメータ設定
        self.my_step    = step
        self.my_cmd     = cmd
        self.area       = area
        self.stay_time  = HOVER_TIME
        self.enter_time = None
        self.arc_id     = None
        self.arc_radius = ARC_RADIUS

        self.image_id = self.canvas.create_image(area[0], area[1], image=self.img, anchor="nw")

    def draw_arc(self, x, y, percent):
        if self.arc_id:
            self.canvas.delete(self.arc_id)
        angle = percent * 3.6
        self.arc_id = self.canvas.create_arc(
            x - self.arc_radius, y - self.arc_radius, 
            x + self.arc_radius, y + self.arc_radius,
            start=90, extent=-angle, style='pieslice',
            outline='black', fill='blue'
        )

    def _handle_hover(self, cursor_x, cursor_y):
        x1, y1, x2, y2 = self.area
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:
            if self.enter_time is None:
                self.enter_time = time.time()
            elapsed = time.time() - self.enter_time
            percent = min(elapsed / self.stay_time * 100, 100)
            self.draw_arc(cursor_x + 40, cursor_y, percent)
            
            if elapsed >= self.stay_time:#一定時間滞留したら
                if self.arc_id:#アークがあるなら
                    self.canvas.delete(self.arc_id)#アークを消す
                    self.arc_id = None
                return self.my_cmd
        else:
            self.enter_time = None
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None
        return None

    def update(self, cursor_x, cursor_y, current_step, selected_candidate, last_decision):
        #サブクラスで実装するメソッド
        raise NotImplementedError

# 候補者ボタン用のクラス
class CandidateButton(BaseButton):
    def update(self, cursor_x, cursor_y, current_step, selected_candidate, last_decision):
        # 見た目の制御
        if current_step in [1, 2]:
            image_to_show = self.img_wait_selected if self.my_cmd == selected_candidate else self.img_wait
        else:
            image_to_show = self.img_selected if self.my_cmd == selected_candidate else self.img
        self.canvas.itemconfig(self.image_id, image=image_to_show)

        # 操作の制御
        if current_step not in [1, 2] or self.my_cmd == selected_candidate:
            return None
        return self._handle_hover(cursor_x, cursor_y)

# Yes/Noボタン用のクラス
class YesNoButton(BaseButton):
    def update(self, cursor_x, cursor_y, current_step, selected_candidate, last_decision):
        image_to_show = self.img # デフォルトは通常画像

        if current_step == 4:
            # 最終決定に至った 'y1' と 'y2' ボタンを選択済みで表示
            if self.my_cmd in ['y1', 'y2']:
                image_to_show = self.img_selected
            else:
                image_to_show = self.img
        # 通常のステップのロジック
        elif self.my_step == current_step:
            image_to_show = self.img_wait
        elif self.my_cmd == last_decision:
            image_to_show = self.img_selected
        
        self.canvas.itemconfig(self.image_id, image=image_to_show)
        # ステップ4では操作不可にする
        if self.my_step != current_step or current_step == 4:
            return None
            
        return self._handle_hover(cursor_x, cursor_y)

class GUIApp:
    def __init__(self):
        self.step = 1
        self.selected_candidate = None
        self.last_decision = None

        self.root = tk.Tk()
        self.root.state("zoomed")
        self.root.update_idletasks()
        self.width, self.height = self.root.winfo_width(), self.root.winfo_height()
        self.canvas = tk.Canvas(self.root, bg="white", width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)

        button_list = [
            (CANDIDATES_1, CANDIDATES_1_WAIT, CANDIDATES_1_WAIT_SELECTED, CANDIDATES_1_SELECTED, 0.06, 0.5, CANDIDATES_WHIDTH, CANDIDATES_HEIGHT, '1' , 1),
            (CANDIDATES_1, CANDIDATES_1_WAIT, CANDIDATES_1_WAIT_SELECTED, CANDIDATES_1_SELECTED, 0.17, 0.5, CANDIDATES_WHIDTH, CANDIDATES_HEIGHT, '2' , 1),
            (CANDIDATES_1, CANDIDATES_1_WAIT, CANDIDATES_1_WAIT_SELECTED, CANDIDATES_1_SELECTED, 0.28, 0.5, CANDIDATES_WHIDTH, CANDIDATES_HEIGHT, '3' , 1),
            (CANDIDATES_1, CANDIDATES_1_WAIT, CANDIDATES_1_WAIT_SELECTED, CANDIDATES_1_SELECTED, 0.39, 0.5, CANDIDATES_WHIDTH, CANDIDATES_HEIGHT, '4' , 1),
            (CANDIDATES_1, CANDIDATES_1_WAIT, CANDIDATES_1_WAIT_SELECTED, CANDIDATES_1_SELECTED, 0.50, 0.5, CANDIDATES_WHIDTH, CANDIDATES_HEIGHT, '5' , 1),
            (YES         , YES_WAIT         , YES_SELECTED              , YES_SELECTED         , 0.75, 3/8, BUTTON_SIZE      , BUTTON_SIZE      , 'y1', 2),
            (NO          , NO_WAIT          , NO_SELECTED               , NO_SELECTED          , 0.90, 3/8, BUTTON_SIZE      , BUTTON_SIZE      , 'n1', 2),
            (YES         , YES_WAIT         , YES_SELECTED              , YES_SELECTED         , 0.75, 6/8, BUTTON_SIZE      , BUTTON_SIZE      , 'y2', 3),
            (NO          , NO_WAIT          , NO_SELECTED               , NO_SELECTED          , 0.90, 6/8, BUTTON_SIZE      , BUTTON_SIZE      , 'n2', 3),
        ]
        
        self.buttons = []
        for img_path, wait_path, wait_sel_path, sel_path, cx_r, cy_r, w, h, cmd, step in button_list:
            center_x, center_y = cx_r * self.width, cy_r * self.height
            area = (center_x - w/2, center_y - h/2, center_x + w/2, center_y + h/2)
            
            if 'y' in cmd or 'n' in cmd:
                self.buttons.append(YesNoButton(self.canvas, img_path, wait_path, wait_sel_path, sel_path, area, cmd, step))
            else:
                self.buttons.append(CandidateButton(self.canvas, img_path, wait_path, wait_sel_path, sel_path, area, cmd, step))
        
        self.check_cursor()

    def check_cursor(self):
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()
        
        command = None
        # ステップ4ではボタン操作を無効にする
        if self.step != 4:
            for button in self.buttons:
                result = button.update(x, y, self.step, self.selected_candidate, self.last_decision)
                if result:
                    command = result
                    break
        # ステップ4に入ったら表示だけを更新し続ける
        else:
            for button in self.buttons:
                button.update(x, y, self.step, self.selected_candidate, self.last_decision)


        if command:
            if self.step == 1 and command.isdigit():
                self.selected_candidate = command
                self.step = 2
                print(f"候補者 {self.selected_candidate} を選択。ステップ2へ。")
            elif self.step == 2:
                if command.isdigit():
                    self.selected_candidate = command
                    self.last_decision = None
                    print(f"候補者を {self.selected_candidate} に変更。")
                elif command in ['y1', 'n1']:
                    self.last_decision = command
                    if command == 'y1':
                        self.step = 3
                        print("一回目の確認で「はい」。ステップ3へ。")
                    else: # n1
                        self.step = 1
                        self.selected_candidate = None
                        self.last_decision = None
                        print("一回目の確認で「いいえ」。ステップ1へ戻ある。")
            elif self.step == 3 and command in ['y2', 'n2']:
                self.last_decision = command
                if command == 'y2':
                    # ★★★ 修正点 ★★★
                    self.step = 4 # 完了ステップに移行
                    print(f"候補者 {self.selected_candidate}で確定。")
                    # 5秒後のリセットを削除
                else: # n2
                    self.step = 1
                    self.selected_candidate = None
                    self.last_decision = None
                    print("二回目の確認で「いいえ」。ステップ１へ。")

        self.root.after(20, self.check_cursor)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = GUIApp()
    app.run()