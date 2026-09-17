import os
import mimetypes

# 基準となるディレクトリ（assets/ 自体）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------
# 1. 共通ナビゲーション一括更新処理
# --------------------------------------------------
def update_common_nav():
    """各サブフォルダー内の index.html にある NAV マーカーを一括更新する"""
    
    # 相対パスによる共通ナビゲーション（どこへ持ち運んでも壊れない構成）
    nav_html = """<nav>
  <a href="../">資産トップ</a>
  <a href="../videos/">動画</a>
  <a href="../audios/">音声</a>
  <a href="../../">サイト本館へ</a>
</nav>"""

    # 管理対象の HTML ファイル一覧
    target_files = [
        os.path.join(BASE_DIR, 'images', 'index.html'),
        os.path.join(BASE_DIR, 'videos', 'index.html'),
        os.path.join(BASE_DIR, 'audios', 'index.html'),
    ]

    start_marker = '<!-- NAV-BUILD-START -->'
    end_marker = '<!-- NAV-BUILD-END -->'

    for filepath in target_files:
        if not os.path.exists(filepath):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if start_marker in content and end_marker in content:
            before = content.split(start_marker)[0]
            after = content.split(end_marker)[1]
            new_content = f"{before}{start_marker}\n{nav_html}\n{end_marker}{after}"

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"🧭 NAV更新完了: {os.path.relpath(filepath, BASE_DIR)}")

# --------------------------------------------------
# 2. 各メディア（画像・動画・音声）カード自動生成処理
# --------------------------------------------------
def build_media_gallery(sub_dir, mime_prefix, card_type):
    """
    指定フォルダー内のファイルを降順（新しい順）で読み込み、ギャラリーカードを生成する
    :param sub_dir: 'images', 'videos', 'audios' などのフォルダー名
    :param mime_prefix: 'image/', 'video/', 'audio/' などの判定用Prefix
    :param card_type: 'image', 'video', 'audio' などの HTML タグ用区分
    """
    target_dir = os.path.join(BASE_DIR, sub_dir)
    gallery_html = os.path.join(target_dir, 'index.html')

    if not os.path.exists(target_dir) or not os.path.exists(gallery_html):
        return

    cards_html = ""
    
    # reverse=True で yyyy.mmdd.nn の新しい日付順（降順）にソート
    for filename in sorted(os.listdir(target_dir), reverse=True):
        filepath = os.path.join(target_dir, filename)
        
        if os.path.isfile(filepath):
            mime_type, _ = mimetypes.guess_type(filepath)
            
            # 指定された MIME タイプに合致する場合のみカード化
            if mime_type and mime_type.startswith(mime_prefix):
                if card_type == 'image':
                    media_tag = f'<img src="{filename}" alt="{filename}" loading="lazy">'
                elif card_type == 'video':
                    media_tag = f'<video src="{filename}" controls preload="metadata"></video>'
                elif card_type == 'audio':
                    media_tag = f'<audio src="{filename}" controls></audio>'
                else:
                    media_tag = ''

                cards_html += f"""
<article class="{card_type}-card">
  <div class="card-media">
    {media_tag}
  </div>
  <div class="card-body">
    <p class="filename">{filename}</p>
  </div>
</article>
"""

    with open(gallery_html, 'r', encoding='utf-8') as f:
        content = f.read()

    start_marker = '<!-- GALLERY-START -->'
    end_marker = '<!-- GALLERY-END -->'

    if start_marker in content and end_marker in content:
        before = content.split(start_marker)[0]
        after = content.split(end_marker)[1]
        
        new_content = f"{before}{start_marker}\n<div class=\"gallery-grid\">\n{cards_html}</div>\n{end_marker}{after}"
        
        with open(gallery_html, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"📦 ギャラリー生成完了: {sub_dir}/index.html")

# --------------------------------------------------
# 実行エントリーポイント
# --------------------------------------------------
if __name__ == '__main__':
    print("🎨 assets 資産マネージャーを実行中...")
    
    # 1. 全ページのナビゲーションを一括同期
    update_common_nav()
    
    # 2. 各サブフォルダーのギャラリーカードを自動作成
    build_media_gallery('images', 'image/', 'image')
    build_media_gallery('videos', 'video/', 'video')
    build_media_gallery('audios', 'audio/', 'audio')