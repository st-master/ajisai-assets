async function loadGallery(folderName, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const repoOwner = "st-master";
  const repoName = "My-Site";
  
  try {
    const response = await fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/contents/${folderName}`);
    
    if (!response.ok) {
      throw new Error(`APIエラー: ${response.status}`);
    }

    const files = await response.json();
    container.innerHTML = ""; // 読み込み中表示のクリア

    // index.html や隠しファイルを除外
    const mediaFiles = files.filter(file => file.type === "file" && !file.name.startsWith("index.html") && !file.name.startsWith("."));

    if (mediaFiles.length === 0) {
      container.innerHTML = "<p>まだファイルがありません。</p>";
      return;
    }

    mediaFiles.forEach(file => {
      const card = document.createElement("div");
      card.className = "gallery-card";

      let mediaHtml = "";
      const ext = file.name.split('.').pop().toLowerCase();

      // ファイル形式に応じたタグの判定
      if (["jpg", "jpeg", "png", "webp", "gif"].includes(ext)) {
        mediaHtml = `<img src="${file.download_url}" alt="${file.name}" loading="lazy">`;
      } else if (["mp4", "webm"].includes(ext)) {
        mediaHtml = `<video controls src="${file.download_url}"></video>`;
      } else if (["mp3", "wav", "m4a", "ogg"].includes(ext)) {
        mediaHtml = `<div style="padding:20px; text-align:center;"><audio controls src="${file.download_url}"></audio></div>`;
      // 変更後: viewer.html を通して綺麗にレンダリング表示させる
      } else if (ext === "md") {
      // viewer.html 経由でパラメータ (?file=ファイル名) を渡して開く
      mediaHtml = `<div style="padding:20px; text-align:center;"><a href="viewer.html?file=${encodeURIComponent(file.name)}" style="font-weight:bold; color:#0366d6; text-decoration:none;">📄 ${file.name} を読む</a></div>`;
      }
      // 変更前: rawデータ（テキスト）を直接開いていた
      // mediaHtml = `<div style="padding:20px;"><a href="${file.download_url}" target="_blank">📄 ${file.name} を開く</a></div>`;

      card.innerHTML = `
        ${mediaHtml}
        <div class="card-info">
          <div class="card-title">${file.name}</div>
        </div>
      `;

      container.appendChild(card);
    });
  } catch (error) {
    console.error("ギャラリーの読み込みに失敗しました:", error);
    container.innerHTML = "<p>ファイルの読み込みに失敗しました。</p>";
  }
}
