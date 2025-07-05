'''
Geminiに、以下のプロンプトを使って書き直してもらったコード。

「このプログラムを、簡潔に、より短く、より可読性高く書き直して。」
'''

import tkinter as tk
from PIL import Image, ImageTk
import time
from config import YES, YES_WAIT, YES_SELECTED, NO, NO_SELECTED, NO_WAIT
from config import BUTTON_SIZE, HOVER_TIME, ARC_RADIUS, CANDIDATES_WHIDTH, CANDIDATES_HEIGHT
from config import CANDIDATES_1, CANDIDATES_1_SELECTED, CANDIDATES_1_WAIT_SELECTED, CANDIDATES_1_WAIT

# --- Button Classes (ほぼ変更なし、updateメソッドのロジックを改善) ---

class BaseButton:
    """ボタンの共通機能を担当する親クラス"""
    def __init__(self, canvas, img_path, wait_path, wait_selected_path, selected_path, area, cmd, step):
        self.canvas = canvas
        width, height = int(area[2] - area[0]), int(area[3] - area[1])

        # 画像の読み込みとリサイズ
        self.img = ImageTk.PhotoImage(Image.open(img_path).resize((width, height)))
        self.img_wait = ImageTk.PhotoImage(Image.open(wait_path).resize((width, height)))
        self.img_wait_selected = ImageTk.PhotoImage(Image.open(wait_selected_path).resize((width, height)))
        self.img_selected = ImageTk.PhotoImage(Image.open(selected_path).resize((width, height)))

        # パラメータ設定
        self.my_step = step
        self.my_cmd = cmd
        self.area = area
        self.stay_time = HOVER_TIME
        self.enter_time = None
        self.arc_id = None
        self.arc_radius = ARC_RADIUS

        self.image_id = self.canvas.create_image(area[0], area[1], image=self.img, anchor="nw")

    def draw_arc(self, x, y, percent):
        """カーソル位置にホバー時間を表す円弧を描画する"""
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
        """カーソルのホバーを処理し、一定時間経過したらコマンドを返す"""
        x1, y1, x2, y2 = self.area
        if x1 <= cursor_x <= x2 and y1 <= cursor_y <= y2:
            if self.enter_time is None:
                self.enter_time = time.time()
            
            elapsed = time.time() - self.enter_time
            percent = min(elapsed / self.stay_time * 100, 100)
            self.draw_arc(cursor_x + 40, cursor_y, percent)

            if elapsed >= self.stay_time:
                if self.arc_id:
                    self.canvas.delete(self.arc_id)
                    self.arc_id = None
                return self.my_cmd
        else:
            self.enter_time = None
            if self.arc_id:
                self.canvas.delete(self.arc_id)
                self.arc_id = None
        return None

    def update(self, cursor_x, cursor_y, current_step, selected_candidate, last_decision):
        """ボタンの状態を更新する（サブクラスで実装）"""
        raise NotImplementedError

class CandidateButton(BaseButton):
    """候補者ボタン用のクラス"""
    def update(self, cursor_x, cursor_y, current_step, selected_candidate, last_decision):
        # --- 見た目の制御（ロジックを単純化） ---
        is_selected = self.my_cmd == selected_candidate
        is_waiting_step = current_step in [1, 2]
        
        if is_selected and is_waiting_step:
            image_to_show = self.img_wait_selected
        elif is_selected and not is_waiting_step:
            image_to_show = self.img_selected
        elif not is_selected and is_waiting_step:
            image_to_show = self.img_wait
        else:
            image_to_show = self.img
        self.canvas.itemconfig(self.image_id, image=image_to_show)

        # --- 操作の制御（ロジックを可読性高く変更） ---
        can_interact = (current_step == 1) or \
                       (current_step == 2 and not is_selected)
        
        if can_interact:
            return self._handle_hover(cursor_x, cursor_y)
        return None


class YesNoButton(BaseButton):
    """Yes/Noボタン用のクラス"""
    def update(self, cursor_x, cursor_y, current_step, selected_candidate, last_decision):
        # --- 見た目の制御（ロジックを単純化） ---
        image_to_show = self.img  # デフォルト
        if current_step == 4 and self.my_cmd in ['y1', 'y2']:
            image_to_show = self.img_selected # 最終決定
        elif self.my_cmd == last_decision:
            image_to_show = self.img_selected # 選択済み
        elif self.my_step == current_step:
            image_to_show = self.img_wait     # 選択可能

        self.canvas.itemconfig(self.image_id, image=image_to_show)

        # --- 操作の制御 ---
        if self.my_step == current_step and current_step != 4:
            return self._handle_hover(cursor_x, cursor_y)
        return None

# --- Main Application Class (ロジックを大幅にリファクタリング) ---

class GUIApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.state("zoomed")
        self.root.update_idletasks()
        self.width, self.height = self.root.winfo_width(), self.root.winfo_height()
        self.canvas = tk.Canvas(self.root, bg="white", width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)

        self._reset_to_start()
        
        # ステートマシンハンドラの定義
        self.state_handlers = {
            1: self._handle_step_1,
            2: self._handle_step_2,
            3: self._handle_step_3,
        }

        self.buttons = self._create_buttons()
        self.check_cursor()

    def _reset_to_start(self):
        """アプリケーションの状態を初期ステップにリセットする"""
        self.step = 1
        self.selected_candidate = None
        self.last_decision = None
        print("--- ステップ1: 候補者を選択してください ---")

    def _create_buttons(self):
        """ボタンの設定データからインスタンスを生成する"""
        # ボタン設定を辞書のリストで定義（可読性向上）
        button_configs = []
        # 候補者ボタン (ループで生成)
        for i in range(5):
            button_configs.append({
                'type': CandidateButton, 'img': CANDIDATES_1, 'wait': CANDIDATES_1_WAIT,
                'wait_sel': CANDIDATES_1_WAIT_SELECTED, 'sel': CANDIDATES_1_SELECTED,
                'cx_r': 0.06 + i * 0.11, 'cy_r': 0.5, 'w': CANDIDATES_WHIDTH, 'h': CANDIDATES_HEIGHT,
                'cmd': str(i + 1), 'step': 1
            })
        
        # Yes/Noボタン
        button_configs.extend([
            {'type': YesNoButton, 'img': YES, 'wait': YES_WAIT, 'wait_sel': YES_SELECTED, 'sel': YES_SELECTED, 'cx_r': 0.75, 'cy_r': 3/8, 'w': BUTTON_SIZE, 'h': BUTTON_SIZE, 'cmd': 'y1', 'step': 2},
            {'type': YesNoButton, 'img': NO, 'wait': NO_WAIT, 'wait_sel': NO_SELECTED, 'sel': NO_SELECTED, 'cx_r': 0.90, 'cy_r': 3/8, 'w': BUTTON_SIZE, 'h': BUTTON_SIZE, 'cmd': 'n1', 'step': 2},
            {'type': YesNoButton, 'img': YES, 'wait': YES_WAIT, 'wait_sel': YES_SELECTED, 'sel': YES_SELECTED, 'cx_r': 0.75, 'cy_r': 6/8, 'w': BUTTON_SIZE, 'h': BUTTON_SIZE, 'cmd': 'y2', 'step': 3},
            {'type': YesNoButton, 'img': NO, 'wait': NO_WAIT, 'wait_sel': NO_SELECTED, 'sel': NO_SELECTED, 'cx_r': 0.90, 'cy_r': 6/8, 'w': BUTTON_SIZE, 'h': BUTTON_SIZE, 'cmd': 'n2', 'step': 3},
        ])

        buttons = []
        for config in button_configs:
            center_x = config['cx_r'] * self.width
            center_y = config['cy_r'] * self.height
            w, h = config['w'], config['h']
            area = (center_x - w/2, center_y - h/2, center_x + w/2, center_y + h/2)
            buttons.append(config['type'](
                self.canvas, config['img'], config['wait'], config['wait_sel'], config['sel'],
                area, config['cmd'], config['step']
            ))
        return buttons

    def _handle_command(self, command):
        """受け取ったコマンドを現在のステップに応じて処理する"""
        handler = self.state_handlers.get(self.step)
        if handler:
            handler(command)

    def _handle_step_1(self, command):
        """ステップ1の処理: 最初の候補者選択"""
        if command.isdigit():
            self.selected_candidate = command
            self.step = 2
            print(f"候補者 {self.selected_candidate} を選択。")
            print("--- ステップ2: 選択を確定しますか？（候補者の再選択も可能） ---")

    def _handle_step_2(self, command):
        """ステップ2の処理: 候補者変更または最初の確認"""
        if command.isdigit():
            self.selected_candidate = command
            self.last_decision = None # 決定をリセット
            print(f"候補者を {self.selected_candidate} に変更。")
        elif command == 'y1':
            self.last_decision = command
            self.step = 3
            print("1回目の確認「はい」。")
            print(f"--- ステップ3: 本当に候補者 {self.selected_candidate} で確定しますか？ ---")
        elif command == 'n1':
            self._reset_to_start()

    def _handle_step_3(self, command):
        """ステップ3の処理: 最終確認"""
        if command == 'y2':
            self.last_decision = command
            self.step = 4
            print(f"最終決定: 候補者 {self.selected_candidate} で確定しました。")
            print("--- 処理終了 ---")
        elif command == 'n2':
            self._reset_to_start()
            
    def check_cursor(self):
        """カーソル位置を監視し、ボタンの状態を更新・コマンドを処理するメインループ"""
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
        else: # ステップ4では表示更新のみ
            for button in self.buttons:
                button.update(x, y, self.step, self.selected_candidate, self.last_decision)

        if command:
            self._handle_command(command)

        self.root.after(20, self.check_cursor)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = GUIApp()
    app.run()