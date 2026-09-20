import os
import glob
import subprocess
import yaml

def build_portal():
    print("🎬 プロジェクター起動: HTMLを生成中...")
    
    # 1. structure.yaml の読み込み
    if not os.path.exists("structure.yaml"):
        print("⚠️ structure.yaml が見つかりません。")
        return

    with open("structure.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    template = data.get("template", "")
    nodes = data.get("nodes", [])
    
    # 2. カードHTMLの動的組み立て
    cards_html = []
    
    # ノード定義（サブディレクトリ）がある場合
    for node in nodes:
        name = node.get("name", "名称未設定")
        path = node.get("path", "#")
        card = f'''
        <div class="gallery-card">
          <div class="card-info">
            <h3 class="card-title">{name}</h3>
            <p><a href="{path}">ポータルを開く &rarr;</a></p>
          </div>
        </div>
        '''
        cards_html.append(card)

    # メディアファイル（音声・画像・動画等）が同階層にある場合もカード化
    media_files = glob.glob("*.m4a") + glob.glob("*.wav") + glob.glob("*.mp3") + glob.glob("*.mp4") + glob.glob("*.png") + glob.glob("*.jpg")
    for file in media_files:
        if file.endswith(('.m4a', '.wav', '.mp3')):
            card = f'''
            <div class="gallery-card">
              <div class="card-info">
                <div class="card-title">{file}</div>
                <audio controls src="{file}"></audio>
              </div>
            </div>
            '''
        elif file.endswith(('.mp4', '.webm')):
            card = f'''
            <div class="gallery-card">
              <video controls src="{file}"></video>
              <div class="card-info">
                <div class="card-title">{file}</div>
              </div>
            </div>
            '''
        elif file.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            card = f'''
            <div class="gallery-card">
              <img src="{file}" alt="{file}">
              <div class="card-info">
                <div class="card-title">{file}</div>
              </div>
            </div>
            '''
        cards_html.append(card)

    content_str = "\n".join(cards_html)
    
    # 3. テンプレートへ流し込み
    full_html = template.replace("{{ title }}", "資産ポータル").replace("{{ content }}", content_str)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print("✅ index.html の生成が完了しました！")

def trigger_sub_builds():
    """ サブディレクトリ内に build.py があれば再帰的に実行 """
    for root, dirs, files in os.walk("."):
        if root == ".":
            continue
        if "build.py" in files:
            print(f"🔄 サブポータルビルド中: {root}")
            subprocess.run(["python", "build.py"], cwd=root)

if __name__ == "__main__":
    build_portal()
    trigger_sub_builds()