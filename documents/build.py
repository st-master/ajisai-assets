import os
<<<<<<< HEAD
import mimetypes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. 各フォルダーの表示定義マップ（未定義の新規フォルダーが追加された場合も自動補完）
FOLDER_MAP = {
    'images': {'name': '画像ギャラリー', 'icon': '🖼️', 'mime': 'image/', 'type': 'image'},
    'videos': {'name': '動画ライブラリ', 'icon': '🎥', 'mime': 'video/', 'type': 'video'},
    'audios': {'name': '音声アーカイブ', 'icon': '🎵', 'mime': 'audio/', 'type': 'audio'},
    'documents': {'name': '文書アーカイブ', 'icon': '📄', 'mime': 'text/', 'type': 'document'},
}

def detect_subfolders():
    """assets/ 直下のディレクトリを動的に自動探索（自動検出インストーラーの役割）"""
    subfolders = {}
    for entry in os.listdir(BASE_DIR):
        full_path = os.path.join(BASE_DIR, entry)
        # ディレクトリであり、隠しフォルダー等でないものを管理対象とする
        if os.path.isdir(full_path) and not entry.startswith('.'):
            if entry in FOLDER_MAP:
                subfolders[entry] = FOLDER_MAP[entry]
            else:
                # 設定にない未知のフォルダーが追加された場合も汎用適用
                subfolders[entry] = {'name': f"{entry.capitalize()} ギャラリー", 'icon': '📁', 'mime': '', 'type': 'generic'}
    return subfolders

def build_nav_html(subfolders, current_level=1):
    """環境に応じてパス階層（../ や ./）を自動修復する動的ナビゲーション生成"""
    prefix = "../" if current_level == 1 else "./"
    root_link = "../../" if current_level == 1 else "../"

    links = [f'<a href="{prefix}">資産トップ</a>']
    for folder, info in subfolders.items():
        links.append(f'<a href="{prefix}{folder}/">{info["name"].replace("ギャラリー", "").replace("ライブラリ", "").replace("アーカイブ", "")}</a>')
    links.append(f'<a href="{root_link}">サイト本館へ</a>')

    return f"<nav>\n  " + "\n  ".join(links) + "\n</nav>"

def generate_cards(target_dir, mime_prefix, card_type):
    """降順ソートされたメディアカードHTMLの自動生成"""
    if not os.path.exists(target_dir):
        return ""

    cards_html = ""
    for filename in sorted(os.listdir(target_dir), reverse=True):
        filepath = os.path.join(target_dir, filename)
        if os.path.isfile(filepath) and not filename.startswith('.'):
            # index.html や スクリプト自体は除外
            if filename in ['index.html', 'build.py', 'template.html', 'config.json']:
                continue

            mime_type, _ = mimetypes.guess_type(filepath)
            
            if card_type == 'image' or (mime_type and mime_type.startswith('image/')):
                media_tag = f'<img src="{filename}" alt="{filename}" loading="lazy">'
            elif card_type == 'video' or (mime_type and mime_type.startswith('video/')):
                media_tag = f'<video src="{filename}" controls preload="metadata"></video>'
            elif card_type == 'audio' or (mime_type and mime_type.startswith('audio/')):
                media_tag = f'<audio src="{filename}" controls></audio>'
            else:
                media_tag = f'<a href="{filename}" target="_blank" class="doc-link">📄 {filename}</a>'

            cards_html += f"""
<article class="media-card">
  <div class="card-media">
    {media_tag}
  </div>
  <div class="card-body">
    <p class="filename">{filename}</p>
  </div>
</article>
"""
    return cards_html

def install_and_build():
    """インストーラー（具現化）メイン処理"""
    template_path = os.path.join(BASE_DIR, 'template.html')
    if not os.path.exists(template_path):
        print("⚠️ template.html が見つかりません。")
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    subfolders = detect_subfolders()

    # --- 1. サブフォルダー（images, videos, audios等）の全自動構築 ---
    nav_sub = build_nav_html(subfolders, current_level=1)
    
    for folder, info in subfolders.items():
        target_dir = os.path.join(BASE_DIR, folder)
        target_html = os.path.join(target_dir, 'index.html')

        page = template_content.replace('{{TITLE}}', info['name'])
        page = page.replace('{{HEADER}}', f"{info['icon']} {info['name']}")

        # NAV置換
        if '<!-- NAV-BUILD-START -->' in page and '<!-- NAV-BUILD-END -->' in page:
            b, a = page.split('<!-- NAV-BUILD-START -->')[0], page.split('<!-- NAV-BUILD-END -->')[1]
            page = f"{b}<!-- NAV-BUILD-START -->\n{nav_sub}\n<!-- NAV-BUILD-END -->{a}"

        # ギャラリーカード置換
        cards = generate_cards(target_dir, info['mime'], info['type'])
        if '<!-- GALLERY-START -->' in page and '<!-- GALLERY-END -->' in page:
            b, a = page.split('<!-- GALLERY-START -->')[0], page.split('<!-- GALLERY-END -->')[1]
            page = f"{b}<!-- GALLERY-START -->\n<div class=\"gallery-grid\">\n{cards}</div>\n<!-- GALLERY-END -->{a}"

        with open(target_html, 'w', encoding='utf-8') as f:
            f.write(page)
        print(f"📦 展開完了: {folder}/index.html ({info['name']})")

    # --- 2. assets/ 直下（ポータル：assets/index.html）の展開 ---
    portal_html_path = os.path.join(BASE_DIR, 'index.html')
    nav_portal = build_nav_html(subfolders, current_level=0)

    portal_page = template_content.replace('{{TITLE}}', '資産管理ポータル')
    portal_page = portal_page.replace('{{HEADER}}', '🏛️ 資産管理ポータル')

    if '<!-- NAV-BUILD-START -->' in portal_page and '<!-- NAV-BUILD-END -->' in portal_page:
        b, a = portal_page.split('<!-- NAV-BUILD-START -->')[0], portal_page.split('<!-- NAV-BUILD-END -->')[1]
        portal_page = f"{b}<!-- NAV-BUILD-START -->\n{nav_portal}\n<!-- NAV-BUILD-END -->{a}"

    # ポータル用カード（各エリアへのポータルカード）
    portal_cards = ""
    for folder, info in subfolders.items():
        portal_cards += f"""
<article class="media-card portal-card">
  <div class="card-body">
    <h3>{info['icon']} {info['name']}</h3>
    <a href="./{folder}/" class="portal-btn">ギャラリーを開く →</a>
  </div>
</article>
"""
    if '<!-- GALLERY-START -->' in portal_page and '<!-- GALLERY-END -->' in portal_page:
        b, a = portal_page.split('<!-- GALLERY-START -->')[0], portal_page.split('<!-- GALLERY-END -->')[1]
        portal_page = f"{b}<!-- GALLERY-START -->\n<div class=\"gallery-grid\">\n{portal_cards}</div>\n<!-- GALLERY-END -->{a}"

    with open(portal_html_path, 'w', encoding='utf-8') as f:
        f.write(portal_page)
    print("✨ ポータル展開完了: assets/index.html")

if __name__ == '__main__':
    print("⚡ インストーラー（assets資産マネージャー）を実行中...")
    install_and_build()
=======
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
>>>>>>> a145c871868f4b1ba7cb3da824fc5b70da190051
