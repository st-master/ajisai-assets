import os
import re
import mimetypes
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

def parse_simple_yaml(yaml_path: Path) -> dict:
    """structure.yaml (Film) から title, icon, template を簡易解析"""
    if not yaml_path.exists():
        return {}

    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {}
    title_match = re.search(r'title:\s*["\']?(.*?)["\']?\n', content)
    icon_match = re.search(r'icon:\s*["\']?(.*?)["\']?\n', content)
    template_match = re.search(r'template:\s*\|\n(.*)', content, re.DOTALL)

    data['title'] = title_match.group(1).strip() if title_match else ""
    data['icon'] = icon_match.group(1).strip() if icon_match else "📁"
    
    if template_match:
        # インデント調整
        lines = template_match.group(1).splitlines()
        clean_lines = [l[2:] if l.startswith('  ') else l for l in lines]
        data['template'] = '\n'.join(clean_lines)
    else:
        data['template'] = ""

    return data

def scan_folder(target_dir: Path):
    """フォルダー内の子ノードとアセットを自動抽出"""
    children = []
    assets = []

    for entry in target_dir.iterdir():
        if entry.name.startswith('.'):
            continue
        if entry.is_dir():
            children.append(entry.name)
        elif entry.is_file():
            # 制御用ファイルは排除
            if entry.name not in ['structure.yaml', 'index.html', 'build.py', 'style.css', 'script.js']:
                assets.append(entry.name)

    return sorted(children), sorted(assets, reverse=True)

def build_cards_html(children: list, assets: list, target_dir: Path) -> str:
    """Screen に投影するためのカードUI HTMLを生成"""
    cards_html = ""

    # 1. 子ノード (サブポータル) カード
    for child in children:
        child_yaml = target_dir / child / "structure.yaml"
        meta = parse_simple_yaml(child_yaml)
        title = meta.get('title') or child
        icon = meta.get('icon') or '📁'

        cards_html += f"""
<article class="gallery-card portal-card">
  <div class="card-info">
    <h3 class="card-title">{icon} {title}</h3>
    <a href="./{child}/" class="portal-btn">ノードを開く →</a>
  </div>
</article>"""

    # 2. アセット (ファイル) カード
    for filename in assets:
        filepath = target_dir / filename
        mime_type, _ = mimetypes.guess_type(filepath)

        if mime_type and mime_type.startswith('image/'):
            media_tag = f'<img src="{filename}" alt="{filename}" loading="lazy">'
        elif mime_type and mime_type.startswith('video/'):
            media_tag = f'<video src="{filename}" controls preload="metadata"></video>'
        elif mime_type and mime_type.startswith('audio/'):
            media_tag = f'<audio src="{filename}" controls></audio>'
        else:
            media_tag = f'<div style="padding:40px 20px; text-align:center;"><a href="{filename}" target="_blank" class="card-title" style="font-size:1.1rem; color:#0366d6;">📄 {filename}</a></div>'

        cards_html += f"""
<article class="gallery-card">
  {media_tag}
  <div class="card-info">
    <div class="card-title">{filename}</div>
  </div>
</article>"""

    return cards_html

def project_node(current_dir: Path, fallback_template: str, depth: int = 0):
    """【Projector】Film(structure.yaml)を読み込み、Screen(index.html)へ投影"""
    yaml_path = current_dir / "structure.yaml"
    meta = parse_simple_yaml(yaml_path)

    title = meta.get('title') or f"{current_dir.name.capitalize()} ギャラリー"
    icon = meta.get('icon') or "📁"
    template = meta.get('template') or fallback_template

    # フォルダー走査
    children, assets = scan_folder(current_dir)

    # 配下ノードの再帰的プロジェクション
    for child in children:
        project_node(current_dir / child, template, depth + 1)

    # パスとカードの流し込み
    rel_css_path = "../" * depth + "style.css" if depth > 0 else "./style.css"
    cards_html = build_cards_html(children, assets, current_dir)

    # 投影用 HTML の組み立て
    html = template.replace('{{TITLE}}', title)
    html = html.replace('{{ICON}}', icon)
    html = html.replace('{{CSS_PATH}}', rel_css_path)
    html = html.replace('{{CARDS}}', cards_html)

    # Screen (index.html) の出力
    index_path = current_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"🎬 Screen 投影完了 [{ 'Root' if depth==0 else f'Depth:{depth}' }]: {current_dir.relative_to(BASE_DIR)}/index.html")

def main():
    print("🎥 Projector 起動: フィルム(structure.yaml)からスクリーン(index.html)へ投影を開始します...")
    
    # ルートのフィルムを読み込み
    root_yaml = BASE_DIR / "structure.yaml"
    root_meta = parse_simple_yaml(root_yaml)
    fallback_template = root_meta.get('template', '')

    project_node(BASE_DIR, fallback_template, depth=0)
    print("\n✨ 画面の再構築が完了しました！")

if __name__ == '__main__':
    main()