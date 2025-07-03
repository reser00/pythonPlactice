# GUI版 ToDoアプリ（tkinter使用）

# tkinterライブラリのtkモジュールをtkという名前でインポート
import tkinter as tk
# tkinterのサブモジュールmessageboxをインポート（警告や通知ダイアログの表示に使用）
from tkinter import messagebox

# タスクを保持するリスト
tasks = []

# タスク追加処理
def add_task():
    task = entry.get()
    if task:
        tasks.append(task)  # 入力されたタスクをtasksリストに追加する
        listbox.insert(tk.END, task)  # listbox（画面上のリスト表示）に追加したタスクを表示する
        entry.delete(0, tk.END)  # 入力欄（entry）を空にする（次の入力に備える）
    else:
        messagebox.showwarning("入力エラー", "タスクを入力してください。")

# タスク削除処理
def delete_task():
    selected = listbox.curselection()
    if selected:
      index = selected[0]       # listboxで選択された最初の項目のインデックスを取得
      removed = tasks.pop(index)# tasksリストからそのインデックスのタスクを取り出し（削除）変数removedに格納
      listbox.delete(index)     # listbox（画面上のリスト）から同じインデックスの項目を削除
      messagebox.showinfo("削除完了", f"「{removed}」を削除しました。")
      
    else:
        messagebox.showwarning("選択エラー", "削除するタスクを選んでください。")

# ウィンドウ作成
root = tk.Tk()  # アプリのメインウィンドウを作成する（ここがGUIのスタート地点）
root.title("ToDoアプリ")  # ウィンドウのタイトルを「ToDoアプリ」に設定

# 入力欄と追加ボタン
entry = tk.Entry(root, width=40)#入力欄を
entry.pack(pady=5)

add_button = tk.Button(root, text="タスクを追加", command=add_task)
add_button.pack()

# タスクリスト表示
listbox = tk.Listbox(root, width=50)
listbox.pack(pady=5)

# 削除ボタン
delete_button = tk.Button(root, text="選択したタスクを削除", command=delete_task)
delete_button.pack()

# メインループ開始
root.mainloop()
