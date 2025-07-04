# todayDo.py - Integrated ToDo and Watch/Weather Application

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import json

# --- グローバル設定（両アプリで共有） ---
# OpenWeatherMap APIキー
API_KEY = "7f947de9886f2e3182e1aac7d4147461" # ★重要: あなたのAPIキーを設定してください

# 天気アプリで使用する都市リスト
CITIES = {
    "東京": "Tokyo",
    "ロンドン": "London",
    "ニューヨーク": "New York",
    "パリ": "Paris",
    "北京": "Beijing",
    "シドニー": "Sydney",
    "カイロ": "Cairo",
    "リオデジャネイロ": "Rio de Janeiro"
}

# --- フォント設定（両アプリで共有し、モダンなArialフォントを使用） ---
FONT_DEFAULT = ('Arial', 10)
FONT_CITY = ('Arial', 28, 'bold')
FONT_TIME = ('Arial', 48, 'bold')
FONT_WEATHER_TITLE = ('Arial', 14, 'bold')
FONT_WEATHER_DETAIL = ('Arial', 12)
FONT_TODO_TITLE = ('Arial', 12, 'bold') # ToDoアプリのタイトル用


# --- WatchAndWeatherApp クラス (wnw.pyから統合) ---
class WatchAndWeatherApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master) # tk.Frameとして初期化
        
        self.current_city_api_name = CITIES["東京"]
        self.timezone_offset_seconds = 0

        self.create_widgets()
        self.update_weather_and_time_display()

    def create_widgets(self):
        # WatchAndWeatherApp自身の内部グリッドを設定
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 都市選択フレーム
        self.city_selection_frame = tk.Frame(self)
        self.city_selection_frame.grid(row=0, column=0, columnspan=2, pady=(15, 5))

        tk.Label(self.city_selection_frame, text="都市を選択: ", font=FONT_DEFAULT).pack(side=tk.LEFT)
        
        self.city_combobox = ttk.Combobox(
            self.city_selection_frame,
            values=list(CITIES.keys()),
            state="readonly",
            font=FONT_DEFAULT
        )
        self.city_combobox.set("東京")
        self.city_combobox.bind("<<ComboboxSelected>>", self.on_city_selected)
        self.city_combobox.pack(side=tk.LEFT)

        # 都市名表示ラベル
        self.city_label = tk.Label(self, text="", font=FONT_CITY)
        self.city_label.grid(row=1, column=0, columnspan=2, pady=(10, 0))

        # 時刻表示ラベル
        self.time_label = tk.Label(self, text="", font=FONT_TIME)
        self.time_label.grid(row=2, column=0, columnspan=2, pady=20)

        # 天気予報表示フレーム
        self.weather_display_frame = tk.Frame(self)
        self.weather_display_frame.grid(row=3, column=0, columnspan=2, pady=(10, 15), sticky="ew")

        tk.Label(self.weather_display_frame, text="天気予報", font=FONT_WEATHER_TITLE).pack(pady=(0, 5))

        self.forecast_labels = []
        for _ in range(6):
            label = tk.Label(self.weather_display_frame, text="", font=FONT_WEATHER_DETAIL)
            label.pack(anchor='w', padx=10)
            self.forecast_labels.append(label)

    def on_city_selected(self, event):
        selected_display_name = self.city_combobox.get()
        self.current_city_api_name = CITIES[selected_display_name]
        self.update_weather_and_time_display()

    def get_weather(self, city_api_name, api_key):
        encoded_city_name = urllib.parse.quote(city_api_name)
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={encoded_city_name}&appid={api_key}&units=metric&lang=ja"
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
                forecast_data = json.loads(data)
            return forecast_data
        except Exception as e:
            messagebox.showerror("エラー", f"天気情報の取得に失敗しました: {e}")
            return None

    def _find_closest_forecast(self, forecast_list, target_utc_dt):
        closest_entry = None
        min_diff = timedelta(days=365)

        for entry in forecast_list:
            entry_utc_dt = datetime.utcfromtimestamp(entry['dt'])
            
            diff = abs(target_utc_dt - entry_utc_dt)

            if diff < min_diff:
                min_diff = diff
                closest_entry = entry
        return closest_entry

    def update_weather_and_time_display(self):
        forecast_data = self.get_weather(self.current_city_api_name, API_KEY)
        if forecast_data:
            self.city_label.config(text=self.current_city_api_name.upper())

            self.timezone_offset_seconds = forecast_data['city'].get('timezone', 0)
            
            self.update_local_time()

            forecast_list = forecast_data['list']
            
            current_utc_time = datetime.utcnow()
            current_local_time = current_utc_time + timedelta(seconds=self.timezone_offset_seconds)

            forecast_periods = [
                ("現在", current_local_time),
                ("1時間後", current_local_time + timedelta(hours=1)),
                ("3時間後", current_local_time + timedelta(hours=3)),
                ("6時間後", current_local_time + timedelta(hours=6)),
                ("12時間後", current_local_time + timedelta(hours=12)),
            ]
            
            next_day_6am_local = (current_local_time + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
            forecast_periods.append(("翌日午前6時", next_day_6am_local))

            for i, (period_name, target_local_dt) in enumerate(forecast_periods):
                target_utc_dt = target_local_dt - timedelta(seconds=self.timezone_offset_seconds)
                closest_forecast = self._find_closest_forecast(forecast_list, target_utc_dt)

                if closest_forecast:
                    forecast_utc_dt = datetime.utcfromtimestamp(closest_forecast['dt'])
                    forecast_local_dt = forecast_utc_dt + timedelta(seconds=self.timezone_offset_seconds)
                    
                    description = closest_forecast['weather'][0]['description']
                    temperature = closest_forecast['main']['temp']
                    
                    if period_name == "現在":
                        display_text = f"現在: {description.capitalize()}, {temperature:.1f}°C"
                    elif period_name == "翌日午前6時":
                        display_text = f"翌日午前6時: {description.capitalize()}, {temperature:.1f}°C"
                    else:
                        display_text = f"{forecast_local_dt.strftime('%H時')}: {description.capitalize()}, {temperature:.1f}°C"
                    
                    self.forecast_labels[i].config(text=display_text)
                else:
                    self.forecast_labels[i].config(text=f"{period_name}: 予報なし")

        self.after(900000, self.update_weather_and_time_display)

    def update_local_time(self):
        utc_now = datetime.utcnow()
        local_time = utc_now + timedelta(seconds=self.timezone_offset_seconds)
        formatted_time = local_time.strftime('%H:%M:%S')
        self.time_label.config(text=formatted_time)
        self.after(1000, self.update_local_time)


# --- ToDoApp クラス (ToDo2.pyから統合) ---
class ToDoApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master) # tk.Frameとして初期化

        self.task_id_counter = 0
        self.tasks = [] # すべてのタスク情報を一元管理するリスト

        self.style = ttk.Style()
        self.style.theme_use('clam') # clamテーマの方がタグによるスタイル変更が反映されやすい
        self.style.configure("Treeview", font=FONT_DEFAULT, rowheight=25)
        self.style.configure("Treeview.Heading", font=(FONT_DEFAULT[0], FONT_DEFAULT[1], 'bold'))

        self.create_widgets()

    def create_widgets(self):
        # ToDoApp自身の内部グリッドを設定
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- 上部フレーム（入力欄と追加ボタン） ---
        input_frame = tk.Frame(self)
        input_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

        self.entry = tk.Entry(input_frame, width=40, font=FONT_DEFAULT)
        self.entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        add_button = tk.Button(input_frame, text="タスクを追加", command=self.add_task)
        add_button.pack(side=tk.LEFT)

        # --- 中央フレーム（2つのリストと移動ボタン） ---
        main_frame = tk.Frame(self)
        main_frame.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky="nsew")

        # main_frame内のグリッド設定
        main_frame.grid_columnconfigure(0, weight=1) # ToDoリストの列
        main_frame.grid_columnconfigure(1, weight=0) # 移動ボタンの列
        main_frame.grid_columnconfigure(2, weight=1) # Doneリストの列
        main_frame.grid_rowconfigure(0, weight=1)

        # --- 左側フレーム（ToDoリスト） ---
        todo_frame = tk.Frame(main_frame)
        todo_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        tk.Label(todo_frame, text="ToDoリスト", font=FONT_TODO_TITLE).pack(pady=(0,5))

        self.todo_tree = ttk.Treeview(todo_frame, columns=('status'), show='tree headings')
        self.todo_tree.heading('#0', text='タスク名')
        self.todo_tree.heading('status', text='状態')
        self.todo_tree.column('#0', stretch=tk.YES)
        self.todo_tree.column('status', width=80, anchor=tk.CENTER, stretch=tk.NO)

        self.todo_tree.tag_configure('Done', foreground='green')
        self.todo_tree.tag_configure('Cancel', foreground='gray')

        self.todo_tree.bind("<ButtonRelease-1>", self.toggle_todo_status)
        self.todo_tree.pack(expand=True, fill=tk.BOTH)

        # --- 中央の移動ボタン ---
        move_button = tk.Button(main_frame, text="⇄", command=self.move_tasks, font=('Helvetica', 16))
        move_button.grid(row=0, column=1, padx=5, pady=20, sticky="ns")

        # --- 右側フレーム（Doneリスト） ---
        done_frame = tk.Frame(main_frame)
        done_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))

        tk.Label(done_frame, text="Doneリスト", font=FONT_TODO_TITLE).pack(pady=(0,5))

        self.done_tree = ttk.Treeview(done_frame, columns=('status'), show='tree headings')
        self.done_tree.heading('#0', text='タスク名')
        self.done_tree.heading('status', text='状態')
        self.done_tree.column('#0', stretch=tk.YES)
        self.done_tree.column('status', width=80, anchor=tk.CENTER, stretch=tk.NO)

        self.done_tree.tag_configure('Reprocess', foreground='red')
        self.done_tree.bind("<ButtonRelease-1>", self.toggle_done_status)
        self.done_tree.pack(expand=True, fill=tk.BOTH)

        # --- 下部フレーム（削除ボタン） ---
        bottom_frame = tk.Frame(self)
        bottom_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        delete_button = tk.Button(bottom_frame, text="選択したタスクを削除", command=self.delete_task)
        delete_button.pack(side=tk.RIGHT)

    def add_task(self):
        task_text = self.entry.get()

        if not task_text:
            messagebox.showwarning("入力エラー", "タスクを入力してください。")
            return

        task_id = f"task_{self.task_id_counter}"
        new_task = {
            'id': task_id,
            'text': task_text,
            'status': 'todo',
            'location': 'todo_list'
        }
        self.tasks.append(new_task)
        self.task_id_counter += 1

        self.todo_tree.insert('', tk.END, iid=new_task['id'], text=new_task['text'], values=(["未完了"]))
        self.entry.delete(0, tk.END)

    def toggle_todo_status(self, event):
        selected_iid = self.todo_tree.focus()
        if not selected_iid:
            return

        task = next((t for t in self.tasks if t['id'] == selected_iid), None)
        if not task or task['location'] != 'todo_list':
            return

        current_status = task['status']
        if current_status == 'todo':
            task['status'] = 'done'
            display_status = "Done"
            display_text = f"✓ {task['text']}"
            self.todo_tree.item(selected_iid, text=display_text, tags=('Done',), values=([display_status]))
        elif current_status == 'done':
            task['status'] = 'cancel'
            display_status = "Cancel"
            display_text = task['text']
            self.todo_tree.item(selected_iid, text=display_text, tags=('Cancel',), values=([display_status]))
        elif current_status == 'cancel':
            task['status'] = 'todo'
            display_status = "未完了"
            display_text = task['text']
            self.todo_tree.item(selected_iid, text=display_text, tags=(), values=([display_status]))

    def toggle_done_status(self, event):
        selected_iid = self.done_tree.focus()
        if not selected_iid:
            return

        task = next((t for t in self.tasks if t['id'] == selected_iid), None)
        if not task or task['location'] != 'done_list':
            return

        current_status = task['status']
        if current_status == 'done_in_list':
            task['status'] = 'reprocess'
            display_status = "再処理"
            self.done_tree.item(selected_iid, tags=('Reprocess',), values=([display_status]))
        elif current_status == 'reprocess':
            task['status'] = 'done_in_list'
            display_status = "完了"
            self.done_tree.item(selected_iid, tags=(), values=([display_status]))

    def move_tasks(self):
        tasks_to_move_to_done = []
        tasks_to_reprocess = []

        for task in self.tasks:
            if task['location'] == 'todo_list' and task['status'] == 'done':
                tasks_to_move_to_done.append(task)
            elif task['location'] == 'done_list' and task['status'] == 'reprocess':
                tasks_to_reprocess.append(task)

        for task in tasks_to_move_to_done:
            task['location'] = 'done_list'
            task['status'] = 'done_in_list'
            
            self.todo_tree.delete(task['id'])
            self.done_tree.insert('', tk.END, iid=task['id'], text=task['text'], values=(["完了"]))

        for task in tasks_to_reprocess:
            task['location'] = 'todo_list'
            task['status'] = 'todo'

            self.done_tree.delete(task['id'])
            self.todo_tree.insert('', tk.END, iid=task['id'], text=task['text'], values=(["未完了"]))

    def delete_task(self):
        selected_iid = self.todo_tree.focus() or self.done_tree.focus()

        if not selected_iid:
            messagebox.showwarning("選択エラー", "削除するタスクを選択してください。")
            return

        self.tasks = [t for t in self.tasks if t['id'] != selected_iid]

        if self.todo_tree.exists(selected_iid):
            self.todo_tree.delete(selected_iid)
        if self.done_tree.exists(selected_iid):
            self.done_tree.delete(selected_iid)


# --- Main Application (統合されたアプリのエントリポイント) ---
if __name__ == '__main__':
    root = tk.Tk()
    root.title("今日のToDoと天気")
    # root.geometry("1200x800") # 必要に応じて初期サイズを設定

    # ★変更点: ttk.PanedWindowを使用します。
    # 水平方向に分割するPanedWindowを作成します。
    paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    # PanedWindowをrootウィンドウ全体に広げます。
    paned_window.pack(fill=tk.BOTH, expand=True)
    # ★学習用コメント: 以前のgrid()設定はPanedWindowを使用するため不要になります。
    # root.grid_columnconfigure(0, weight=1) # 天気アプリの列
    # root.grid_columnconfigure(1, weight=1) # ToDoアプリの列
    # root.grid_rowconfigure(0, weight=1) # 1つの行

    # WatchAndWeatherAppのインスタンスを作成し、PanedWindowに追加
    weather_app = WatchAndWeatherApp(master=paned_window)
    paned_window.add(weather_app, weight=1) # weightで伸縮比率を設定
    # ★学習用コメント: 以前のgrid()配置はPanedWindowを使用するため不要になります。
    # weather_app.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # ToDoAppのインスタンスを作成し、PanedWindowに追加
    todo_app = ToDoApp(master=paned_window)
    paned_window.add(todo_app, weight=1) # weightで伸縮比率を設定
    # ★学習用コメント: 以前のgrid()配置はPanedWindowを使用するため不要になります。
    # todo_app.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    root.mainloop()
