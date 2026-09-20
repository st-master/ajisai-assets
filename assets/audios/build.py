import os
import re
import mimetypes
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

def parse_simple_yaml(yaml_path: Path) -> dict:
    if not yaml_path.exists():
        return {}
    with open(yaml_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    data = {}
    title_match = re.search(r'title:\s*["\']?(.*?)["\']?\n', content)
    icon_match = re.search(r'icon:\s*["\']?(.*?)["\']?\n', content)
    template_match = re.search(r'template:\s*\|\n(.*)', content, re.DOTALL)
    
    data["title"] = title_match.group(1).strip() if title_match else ""
    data["icon"] = icon_match.group(1).strip() if icon_match else "📁"
    
    if template_match:
        lines = template_match.group(1).splitlines()
        clean_lines = [l[2:] if l.startswith("  ") else l for l in lines]
        data["template"] = "\n".join(clean_lines)
    else:
        data["template"] = ""
        
    return data

def scan_folder(target_dir: Path):
    children = []
    assets = []
    for entry in target_dir.iterdir():
        if entry.name.startswith(".") or entry.name.startswith("_"):
            continue
        if entry.is_dir():
            children.append(entry.name)
        elif entry.is_file():
            if entry.name not in ["structure.yaml", "index.html", "build.py", "style.css", "script.js"]:
                assets.append(entry.name)
    return sorted(children), sorted(assets, reverse=True)

def build_cards_html(children: list, assets: list, target_dir: Path) -> str:
    cards_html = ""
    for child in children:
        child_yaml = target_dir / child / "structure.yaml"
        meta = parse_simple_yaml(child_yaml)
        title = meta.get("title") or child
        icon = meta.get("icon") or "📁"
        cards_html += f"""
        <article class="gallery-card portal-card">
          <div class="card-info">
            <h3 class="card-title">{icon} {title}</h3>
            <a href="./{child}/" class="portal-btn">ノードを開く →</a>
          </div>
        </article>"""

    for filename in assets:
        filepath = target_dir / filename
        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type and mime_type.startswith("image/"):
            media_tag = f'<img src="{filename}" alt="{filename}" loading="lazy">'
        elif mime_type and mime_type.startswith("video/"):
            media_tag = f'<video src="{filename}" controls preload="metadata"></video>'
        elif mime_type and mime_type.startswith("audio/"):
            media_tag = f'<audio src="{filename}" controls></audio>'
        else:
            media_tag = f'<div style="padding:40px 20px; text-align:center;"><a href="{filename}" target="_blank" class="card-title">📄 {filename}</a></div>'
        
        cards_html += f"""
        <article class="gallery-card">
          {media_tag}
          <div class="card-info">
            <div class="card-title">{filename}</div>
          </div>
        </article>"""
    return cards_html

def build_current_directory():
    yaml_path = BASE_DIR / "structure.yaml"
    if not yaml_path.exists():
        return

    meta = parse_simple_yaml(yaml_path)
    title = meta.get("title", BASE_DIR.name)
    icon = meta.get("icon", "🎨")
    template = meta.get("template", "")

    children, assets = scan_folder(BASE_DIR)
    cards_html = build_cards_html(children, assets, BASE_DIR)

    html = template.replace("{{TITLE}}", title)
    html = html.replace("{{ICON}}", icon)
    html = html.replace("{{CARDS}}", cards_html)

    index_path = BASE_DIR / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    build_current_directory()
