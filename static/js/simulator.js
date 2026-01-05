/**Storage Explorer JS*/
document.addEventListener('DOMContentLoaded', async ()=>{
  const fileInput = document.getElementById('file-input');
  const uploadBtn = document.getElementById('upload-btn');
  const backBtn = document.getElementById('back-btn');
  const refreshBtn = document.getElementById('refresh-btn');

  async function loadFiles(){
    try{
      const res = await fetch(`/api/storage/list/${SESSION_TOKEN}`);
      const data = await res.json();
      const ul = document.getElementById('files');
      if(!data.files || data.files.length === 0){
        ul.innerHTML = '<li style="padding:8px; color:rgba(230,238,248,0.5);">No files yet</li>';
      }else{
        ul.innerHTML = data.files.map(f=>`
          <li style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.03);">
            <a href="/api/storage/download/${SESSION_TOKEN}/${encodeURIComponent(f.name)}" target="_blank" style="color:var(--accent); text-decoration:none;">
              📄 ${f.name}
            </a>
            <span style="float:right; font-size:12px; color:rgba(230,238,248,0.5);">${(f.size/1024).toFixed(2)} KB</span>
          </li>
        `).join('');
      }
    }catch(e){console.error(e);}
  }

  async function loadStats(){
    try{
      const res = await fetch(`/api/storage/stats/${SESSION_TOKEN}`);
      const data = await res.json();
      document.getElementById('file-count').textContent = data.total_files;
      document.getElementById('total-size').textContent = data.total_size_mb;
    }catch(e){console.error(e);}
  }

  uploadBtn.addEventListener('click', async ()=>{
    const files = fileInput.files;
    if(!files || files.length===0) return alert('Select files first');
    for(let i=0;i<files.length;i++){
      const form = new FormData();
      form.append('file', files[i]);
      try{
        const res = await fetch(`/api/storage/upload/${SESSION_TOKEN}`, {method:'POST', body:form});
        const j = await res.json();
        if(j.error) alert('Upload error: '+j.error);
      }catch(e){console.error(e); alert('Upload failed');}
    }
    fileInput.value = '';
    await loadFiles();
    await loadStats();
  });

  refreshBtn.addEventListener('click', ()=>{
    loadFiles();
    loadStats();
  });

  backBtn.addEventListener('click', ()=>{
    window.location.href = `/session/${SESSION_TOKEN}`;
  });

  // initial load
  loadFiles();
  loadStats();
  setInterval(()=>{loadFiles(); loadStats();}, 3000);
});
