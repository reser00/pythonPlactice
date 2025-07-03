# GUI版 高機能ToDoアプリ（tkinter使用）

import tkinter as tk
from tkinter import ttk, messagebox

# --- 定数 ---
FONT_DEFAULT = ('Helvetica', 10)

# --- グローバル変数 ---
task_id_counter = 0
tasks = [] # すべてのタスク情報を一元管理するリスト

# --- Functions ---

def add_task():
    """入力欄から新しいタスクを取得し、データとUI（ToDoリスト）に追加します。"""
    global task_id_counter, tasks
    task_text = entry.get()

    if not task_text:
        messagebox.showwarning("入力エラー", "タスクを入力してください。")
        return

    task_id = f"task_{task_id_counter}"
    new_task = {
        'id': task_id,
        'text': task_text,
        'status': 'todo',      # 状態: todo, done, cancel, reprocess
        'location': 'todo_list' # 場所: todo_list, done_list
    }
    tasks.append(new_task)
    task_id_counter += 1

    todo_tree.insert('', tk.END, iid=new_task['id'], text=new_task['text'], values=(["未完了"]))
    entry.delete(0, tk.END)

def toggle_todo_status(event):
    """ToDoリストのタスクがクリックされた際に、その状態を切り替えます。"""
    selected_iid = todo_tree.focus()
    if not selected_iid:
        return

    task = next((t for t in tasks if t['id'] == selected_iid), None)
    if not task or task['location'] != 'todo_list':
        return

    current_status = task['status']
    if current_status == 'todo':
        task['status'] = 'done'
        display_status = "Done"
        display_text = f"✓ {task['text']}"
        todo_tree.item(selected_iid, text=display_text, tags=('Done',), values=([display_status]))
    elif current_status == 'done':
        task['status'] = 'cancel'
        display_status = "Cancel"
        display_text = task['text']
        todo_tree.item(selected_iid, text=display_text, tags=('Cancel',), values=([display_status]))
    elif current_status == 'cancel':
        task['status'] = 'todo'
        display_status = "未完了"
        display_text = task['text']
        todo_tree.item(selected_iid, text=display_text, tags=(), values=([display_status]))

def toggle_done_status(event):
    """Doneリストのタスクがクリックされた際に、その状態を切り替えます。"""
    selected_iid = done_tree.focus()
    if not selected_iid:
        return

    task = next((t for t in tasks if t['id'] == selected_iid), None)
    if not task or task['location'] != 'done_list':
        return

    current_status = task['status']
    if current_status == 'done_in_list':
        task['status'] = 'reprocess'
        display_status = "再処理"
        done_tree.item(selected_iid, tags=('Reprocess',), values=([display_status]))
    elif current_status == 'reprocess':
        task['status'] = 'done_in_list'
        display_status = "完了"
        done_tree.item(selected_iid, tags=(), values=([display_status]))

def move_tasks():
    """「⇄」ボタンが押された時、状態に応じてタスクをリスト間で移動します。"""
    # ★学習用コメント: ループ中にリストのサイズが変わると問題が起きるため、
    # 移動対象のタスクを一度別のリストに集めてから、ループ外で処理します。
    tasks_to_move_to_done = []
    tasks_to_reprocess = []

    for task in tasks:
        if task['location'] == 'todo_list' and task['status'] == 'done':
            tasks_to_move_to_done.append(task)
        elif task['location'] == 'done_list' and task['status'] == 'reprocess':
            tasks_to_reprocess.append(task)

    # ToDo -> Done への移動処理
    for task in tasks_to_move_to_done:
        task['location'] = 'done_list'
        task['status'] = 'done_in_list' # Doneリスト内でのデフォルト状態
        
        # UIから削除し、新しいリストに追加
        todo_tree.delete(task['id'])
        done_tree.insert('', tk.END, iid=task['id'], text=task['text'], values=(["完了"]))

    # Done -> ToDo への移動処理
    for task in tasks_to_reprocess:
        task['location'] = 'todo_list'
        task['status'] = 'todo' # ToDoリストに戻った際の初期状態

        # UIから削除し、新しいリストに追加
        done_tree.delete(task['id'])
        todo_tree.insert('', tk.END, iid=task['id'], text=task['text'], values=(["未完了"]))

    # ★学習用コメント: 以前の未実装のコードです。
    # print("Move tasks button clicked")

def delete_task():
    """いずれかのリストで選択されているタスクを削除します。"""
    # focus()は現在フォーカスのあるアイテムを返す。どちらかのリストで選択されていればそのIDが、されていなければ空文字が入る。
    selected_iid = todo_tree.focus() or done_tree.focus()

    if not selected_iid:
        messagebox.showwarning("選択エラー", "削除するタスクを選択してください。")
        return

    # 該当タスクをtasksリストから削除
    # ★学習用コメント: リスト内包表記を使うと、条件に合致しない要素だけで新しいリストを効率的に作成できます。
    # これにより、元のリストから特定の要素を削除するのと同じ効果が得られます。
    global tasks
    tasks = [t for t in tasks if t['id'] != selected_iid]

    # UI上からタスクを削除
    # exists()でアイテムが存在するか確認してからdelete()を呼ぶのが安全です。
    if todo_tree.exists(selected_iid):
        todo_tree.delete(selected_iid)
    if done_tree.exists(selected_iid):
        done_tree.delete(selected_iid)

    # ★学習用コメント: 以前の未実装のコードです。
    # print("Delete task button clicked")


# --- Main Application ---

root = tk.Tk()
root.title("高機能ToDoアプリ")
root.geometry("800x500")

# --- UI Elements ---

input_frame = tk.Frame(root)
input_frame.pack(pady=10, fill=tk.X, padx=10)

entry = tk.Entry(input_frame, width=40, font=FONT_DEFAULT)
entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

add_button = tk.Button(input_frame, text="タスクを追加", command=add_task)
add_button.pack(side=tk.LEFT)

main_frame = tk.Frame(root)
main_frame.pack(pady=5, padx=10, expand=True, fill=tk.BOTH)

# --- 左側フレーム（ToDoリスト） ---
todo_frame = tk.Frame(main_frame)
todo_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 5))

tk.Label(todo_frame, text="ToDoリスト", font=(FONT_DEFAULT[0], 12, 'bold')).pack(pady=(0,5))

todo_tree = ttk.Treeview(todo_frame, columns=('status',), show='tree headings')
todo_tree.heading('#0', text='タスク名')
todo_tree.heading('status', text='状態')
todo_tree.column('#0', stretch=tk.YES)
todo_tree.column('status', width=80, anchor=tk.CENTER, stretch=tk.NO)

todo_tree.tag_configure('Done', foreground='green')
todo_tree.tag_configure('Cancel', foreground='gray')

todo_tree.bind("<ButtonRelease-1>", toggle_todo_status)
todo_tree.pack(expand=True, fill=tk.BOTH)

move_button = tk.Button(main_frame, text="⇄", command=move_tasks, font=('Helvetica', 16))
move_button.pack(side=tk.LEFT, padx=5, pady=20)

# --- 右側フレーム（Doneリスト） ---
done_frame = tk.Frame(main_frame)
done_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(5, 0))

tk.Label(done_frame, text="Doneリスト", font=(FONT_DEFAULT[0], 12, 'bold')).pack(pady=(0,5))

done_tree = ttk.Treeview(done_frame, columns=('status',), show='tree headings')
done_tree.heading('#0', text='タスク名')
done_tree.heading('status', text='状態')
done_tree.column('#0', stretch=tk.YES)
done_tree.column('status', width=80, anchor=tk.CENTER, stretch=tk.NO)

done_tree.tag_configure('Reprocess', foreground='red')
# Doneリストにクリックイベントを紐付け、toggle_done_status関数を呼び出すようにします。
done_tree.bind("<ButtonRelease-1>", toggle_done_status)

done_tree.pack(expand=True, fill=tk.BOTH)

# --- 下部フレーム（削除ボタン） ---
bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=10, fill=tk.X, padx=10)

# 削除ボタンのcommandを、実装したdelete_task関数に変更します。
delete_button = tk.Button(bottom_frame, text="選択したタスクを削除", command=delete_task)
delete_button.pack(side=tk.RIGHT)

root.mainloop()