/**Camera & Storage Integration JS*/

document.addEventListener('DOMContentLoaded', async ()=>{
  const cameraFeed = document.getElementById('camera-feed');
  const cameraPlaceholder = document.getElementById('camera-placeholder');
  const captureBtn = document.getElementById('capture-btn');
  const toggleCameraBtn = document.getElementById('toggle-camera-btn');
  const permissionModal = document.getElementById('permission-modal');
  const grantPermsBtn = document.getElementById('grant-perms-btn');
  const skipPermsBtn = document.getElementById('skip-perms-btn');
  const fileInput = document.getElementById('file-input');
  const uploadBtn = document.getElementById('upload-btn');
  const refreshFilesBtn = document.getElementById('refresh-files-btn');
  const backBtn = document.getElementById('back-to-paths-btn');
  const photoCanvas = document.getElementById('photo-canvas');
  const photosGrid = document.getElementById('photos-grid');
  const fileList = document.getElementById('file-list');

  let stream = null;
  let cameraActive = false;
  let capturedPhotos = [];

  // Request permissions
  async function requestPermissions(){
    let cameraGranted = false;
    try{
      stream = await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'}, audio:false});
      cameraGranted = true;
      startCamera();
    }catch(e){
      console.warn('Camera permission denied:', e);
    }
    permissionModal.style.display = 'none';
    return cameraGranted;
  }

  function startCamera(){
    if(!stream) return;
    cameraFeed.srcObject = stream;
    cameraActive = true;
    cameraPlaceholder.style.display = 'none';
    toggleCameraBtn.textContent = 'Stop Camera';
  }

  function stopCamera(){
    if(stream){
      stream.getTracks().forEach(t=>t.stop());
      stream = null;
      cameraFeed.srcObject = null;
      cameraActive = false;
      cameraPlaceholder.style.display = 'flex';
      toggleCameraBtn.textContent = 'Start Camera';
    }
  }

  function capturePhoto(){
    if(!cameraActive || !cameraFeed.readyState) return;
    const ctx = photoCanvas.getContext('2d');
    const rect = cameraFeed.getBoundingClientRect();
    photoCanvas.width = cameraFeed.videoWidth || 640;
    photoCanvas.height = cameraFeed.videoHeight || 480;
    ctx.drawImage(cameraFeed, 0, 0);
    const dataUrl = photoCanvas.toDataURL('image/jpeg');
    capturedPhotos.push(dataUrl);
    renderPhotos();
  }

  function renderPhotos(){
    if(capturedPhotos.length === 0){
      photosGrid.innerHTML = '<div style="padding:12px; color:rgba(230,238,248,0.5); font-size:13px;">No photos yet</div>';
    }else{
      photosGrid.innerHTML = capturedPhotos.map((url, i)=>`
        <div style="position:relative; border-radius:8px; overflow:hidden; background:#000;">
          <img src="${url}" style="width:100%; height:120px; object-fit:cover; cursor:pointer;" onclick="downloadPhoto(${i})">
          <button onclick="deletePhoto(${i})" style="position:absolute; top:4px; right:4px; background:rgba(0,0,0,0.7); color:#fff; border:none; border-radius:4px; padding:4px 6px; cursor:pointer; font-size:11px;">Del</button>
        </div>
      `).join('');
    }
  }

  window.downloadPhoto = (idx)=>{
    const a = document.createElement('a');
    a.href = capturedPhotos[idx];
    a.download = `photo-${Date.now()}.jpg`;
    a.click();
  };

  window.deletePhoto = (idx)=>{
    capturedPhotos.splice(idx, 1);
    renderPhotos();
  };

  async function loadFiles(){
    try{
      const res = await fetch(`/api/storage/list/${SESSION_TOKEN}`);
      const data = await res.json();
      if(!data.files || data.files.length===0){
        fileList.innerHTML = '<li style="padding:12px; color:rgba(230,238,248,0.5); font-size:13px;">No files yet</li>';
      }else{
        fileList.innerHTML = data.files.map(f=>`
          <li style="padding:8px 12px; border-bottom:1px solid rgba(255,255,255,0.03); display:flex; justify-content:space-between; align-items:center;">
            <a href="/api/storage/download/${SESSION_TOKEN}/${encodeURIComponent(f.name)}" target="_blank" style="color:var(--accent); text-decoration:none; flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
              ${f.name}
            </a>
            <span style="font-size:11px; color:rgba(230,238,248,0.5); margin-left:8px; white-space:nowrap;">${(f.size/1024).toFixed(1)}KB</span>
          </li>
        `).join('');
      }
    }catch(e){console.error(e);}
  }

  grantPermsBtn.addEventListener('click', async ()=>{
    await requestPermissions();
  });

  skipPermsBtn.addEventListener('click', ()=>{
    permissionModal.style.display = 'none';
  });

  captureBtn.addEventListener('click', capturePhoto);

  toggleCameraBtn.addEventListener('click', ()=>{
    if(cameraActive) stopCamera();
    else requestPermissions();
  });

  uploadBtn.addEventListener('click', async ()=>{
    const files = fileInput.files;
    if(!files || files.length===0) return alert('Select files first');
    for(let i=0; i<files.length; i++){
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
  });

  refreshFilesBtn.addEventListener('click', loadFiles);

  backBtn.addEventListener('click', ()=>{
    stopCamera();
    window.location.href = `/session/${SESSION_TOKEN}`;
  });

  // Show permission modal on load
  permissionModal.style.display = 'flex';

  // Load files
  loadFiles();
  setInterval(loadFiles, 4000);
});
