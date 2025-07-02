# シンプルなToDoアプリ（CLIバージョン）

tasks = []

while True:
    print("\n--- ToDo アプリ ---")
    print("1. タスクを追加")
    print("2. タスクを表示")
    print("3. タスクを削除")
    print("4. 終了")
    choice = input("選択してください（1-4）: ")

    if choice == "1":
        task = input("追加するタスク: ")
        tasks.append(task)
        print("タスクを追加しました。")

    elif choice == "2":
        print("\n現在のタスク:")
        if not tasks:
            print("（タスクはありません）")
        else:
            for i, task in enumerate(tasks):
                print(f"{i+1}. {task}")

    elif choice == "3":
        if not tasks:
            print("削除するタスクがありません。")
            continue
        try:
            task_num = int(input("削除するタスク番号: ")) - 1
            if 0 <= task_num < len(tasks):
                removed = tasks.pop(task_num)
                print(f"「{removed}」を削除しました。")
            else:
                print("無効な番号です。")
        except ValueError:
            print("番号を入力してください。")

    elif choice == "4":
        print("アプリを終了します。")
        break

    else:
        print("無効な選択です。1〜4を入力してください。")
