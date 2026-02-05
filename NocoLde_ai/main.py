import openai
import json
import os

# 1. APIキーの設定
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def load_history(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(filename, history):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def start_session():
    # プロンプト一覧（業種一覧）を表示
    prompt_dir = "prompts"
    prompts = [f for f in os.listdir(prompt_dir) if f.endswith(".txt")]
    
    print("\n--- NocoLde AI SaaS 管理パネル ---")
    for i, p in enumerate(prompts):
        print(f"[{i}] {p.replace('.txt', '')}")
    
    choice = int(input("\n操作するクライアント番号を選択: "))
    client_name = prompts[choice].replace(".txt", "")
    
    # 専用プロンプトの読み込み
    with open(f"prompts/{prompts[choice]}", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # 専用履歴ファイルのパス
    history_file = f"histories/history_{client_name}.json"
    history = load_history(history_file)

    if not history:
        history.append({"role": "system", "content": system_prompt})

    print(f"\n>>> {client_name} モード起動中（'exit'で終了）")

    while True:
        user_input = input("\nあなた: ")
        if user_input.lower() == 'exit':
            break

        history.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=history
            )
            answer = response.choices[0].message.content
            print(f"\nAI: {answer}")

            history.append({"role": "assistant", "content": answer})
            save_history(history_file, history) # 毎回保存
            
        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    # historiesフォルダがなければ作る
    if not os.path.exists("histories"):
        os.makedirs("histories")
    start_session()