document.addEventListener('DOMContentLoaded', ()=>{
  const storageBtn = document.getElementById('storage-btn');
  const permissionBtn = document.getElementById('permission-btn');
  const securityBtn = document.getElementById('security-btn');
  const storageView = document.getElementById('storage');
  const permissionView = document.getElementById('permission');
  const securityView = document.getElementById('security');
  const fileInput = document.getElementById('file-input');
  const uploadBtn = document.getElementById('upload-btn');
  const uploadedList = document.getElementById('uploaded-list');

  function show(v){
    storageView.style.display = v==='storage' ? '' : 'none';
    permissionView.style.display = v==='permission' ? '' : 'none';
    securityView.style.display = v==='security' ? '' : 'none';
  }

  storageBtn.addEventListener('click', ()=> show('storage'));
  permissionBtn.addEventListener('click', ()=> show('permission'));
  securityBtn.addEventListener('click', ()=> show('security'));

  async function pollFiles(){
    try{
      const res = await fetch(`/poll/${SESSION_TOKEN}`);
      const data = await res.json();
      uploadedList.innerHTML = '';
      for(const f of data.files){
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = f.url;
        a.textContent = f.name;
        a.target = '_blank';
        li.appendChild(a);
        uploadedList.appendChild(li);
      }
    }catch(e){ console.error(e) }
  }

  uploadBtn.addEventListener('click', async ()=>{
    const files = fileInput.files;
    if(!files || files.length===0) return alert('Select files first');
    for(let i=0;i<files.length;i++){
      const form = new FormData();
      form.append('file', files[i]);
      try{
        const res = await fetch(`/upload/${SESSION_TOKEN}`, { method:'POST', body: form });
        const j = await res.json();
        if(j.error) alert('Upload error: '+j.error);
      }catch(e){ console.error(e); alert('Upload failed') }
    }
    await pollFiles();
  });

  // start on storage view
  show('storage');
  pollFiles();
  setInterval(pollFiles, 4000);
});
