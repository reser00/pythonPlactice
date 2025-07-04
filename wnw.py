# wnw.py - Watch and Weather Application

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import json

# --- 設定 --- #
API_KEY = "7f947de9886f2e3182e1aac7d4147461" # 例: "abcdef1234567890abcdef1234567890"
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

# ★変更点: フォントをArialに変更し、サイズを調整します。
FONT_DEFAULT = ('Arial', 10)
FONT_CITY = ('Arial', 28, 'bold') # 都市名用
FONT_TIME = ('Arial', 48, 'bold') # 時刻用
FONT_WEATHER_TITLE = ('Arial', 14, 'bold') # 天気予報見出し用
FONT_WEATHER_DETAIL = ('Arial', 12) # 天気予報詳細用

class WatchAndWeatherApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        # ★変更点: pack()ではなくgrid()を使用します。
        # アプリケーションのメインフレームをウィンドウ全体に広げます。
        self.grid(row=0, column=0, sticky="nsew")
        # ウィンドウのリサイズ時にフレームが伸縮するように設定します。
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        
        self.current_city_api_name = CITIES["東京"]
        self.timezone_offset_seconds = 0

        self.create_widgets()
        self.update_weather_and_time_display()

    def create_widgets(self):
        # ★変更点: grid()レイアウトを使用します。
        # 各ウィジェットをグリッドの特定の行と列に配置します。

        # 都市選択フレーム
        self.city_selection_frame = tk.Frame(self)
        # grid()で配置。columnspan=2で2列分を占有し、padyで上下に余白。
        self.city_selection_frame.grid(row=0, column=0, columnspan=2, pady=(15, 5))
        # ★学習用コメント: 以前のpack()はコメントアウトします。
        # self.city_selection_frame.pack(pady=(10, 0))

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
        # ★変更点: FONT_CITYを使用し、中央寄せにします。
        self.city_label = tk.Label(self, text="", font=FONT_CITY)
        self.city_label.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        # ★学習用コメント: 以前のpack()はコメントアウトします。
        # self.city_label.pack(pady=(10, 0))

        # 時刻表示ラベル
        # ★変更点: FONT_TIMEを使用し、中央寄せにします。
        self.time_label = tk.Label(self, text="", font=FONT_TIME)
        self.time_label.grid(row=2, column=0, columnspan=2, pady=20)
        # ★学習用コメント: 以前のpack()はコメントアウトします。
        # self.time_label.pack(pady=20)

        # 天気予報表示フレーム
        self.weather_display_frame = tk.Frame(self)
        # ★変更点: grid()で配置し、sticky="ew"で左右に引き伸ばします。
        self.weather_display_frame.grid(row=3, column=0, columnspan=2, pady=(10, 15), sticky="ew")
        # ★学習用コメント: 以前のpack()はコメントアウトします。
        # self.weather_display_frame.pack(pady=10)

        tk.Label(self.weather_display_frame, text="天気予報", font=FONT_WEATHER_TITLE).pack(pady=(0, 5))

        self.forecast_labels = []
        for _ in range(6):
            label = tk.Label(self.weather_display_frame, text="", font=FONT_WEATHER_DETAIL)
            label.pack(anchor='w', padx=10) # 各予報ラベルも左寄せで、左右に少しパディング
            self.forecast_labels.append(label)

        # ★変更点: grid()の列の伸縮設定
        # これにより、ウィンドウサイズが変更されたときに、コンテンツが適切に伸縮します。
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def on_city_selected(self, event):
        """Comboboxで都市が選択されたときに呼び出されます。"""
        selected_display_name = self.city_combobox.get()
        self.current_city_api_name = CITIES[selected_display_name]
        self.update_weather_and_time_display()

    def get_weather(self, city_api_name, api_key):
        """OpenWeatherMap APIから天気予報情報を取得します。"""
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
        """予報リストから指定されたUTC時刻に最も近い予報エントリを見つけます。"""
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
        """天気予報情報を取得し、ラベルを更新して、定期的に再度この関数を呼び出します。"""
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
        """選択された都市のローカル時刻を計算し、ラベルを更新します。""" 
        utc_now = datetime.utcnow()
        local_time = utc_now + timedelta(seconds=self.timezone_offset_seconds)
        formatted_time = local_time.strftime('%H:%M:%S')
        self.time_label.config(text=formatted_time)
        self.after(1000, self.update_local_time)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Watch and Weather")
    app = WatchAndWeatherApp(master=root)
    app.mainloop()
