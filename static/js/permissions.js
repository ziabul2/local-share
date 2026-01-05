/**Permissions Education JS*/
document.addEventListener('DOMContentLoaded', async ()=>{
  const platformSelect = document.getElementById('platform-select');
  const permsList = document.getElementById('perms-list');
  const tipsList = document.getElementById('tips-list');
  const backBtn = document.getElementById('back-btn');
  const detailSection = document.getElementById('permission-detail');
  const closeDetailBtn = document.getElementById('close-detail');

  async function loadDangerousPerms(){
    const platform = platformSelect.value;
    try{
      const res = await fetch(`/api/permissions/dangerous?platform=${platform}`);
      const data = await res.json();
      permsList.innerHTML = Object.entries(data).map(([key, perm])=>`
        <div style="padding:12px; background:rgba(255,255,255,0.01); border-radius:8px; border-left:3px solid var(--accent); cursor:pointer;" onclick="showDetail('${key}', '${platform}')">
          <strong>${perm.name}</strong>
          <p style="margin:6px 0 0; font-size:13px; color:rgba(230,238,248,0.6);">${perm.description}</p>
        </div>
      `).join('');
    }catch(e){console.error(e);}
  }

  async function loadTips(){
    try{
      const res = await fetch('/api/permissions/tips');
      const data = await res.json();
      tipsList.innerHTML = data.tips.map(t=>`<li>${t}</li>`).join('');
    }catch(e){console.error(e);}
  }

  window.showDetail = async (permName, platform)=>{
    try{
      const res = await fetch(`/api/permissions/detail/${permName}?platform=${platform}`);
      const data = await res.json();
      document.getElementById('detail-name').textContent = data.name;
      document.getElementById('detail-desc').textContent = data.description;
      const ul = document.getElementById('detail-points');
      ul.innerHTML = (data.educational_points || []).map(p=>`<li>${p}</li>`).join('');
      detailSection.style.display = '';
    }catch(e){console.error(e);}
  };

  platformSelect.addEventListener('change', loadDangerousPerms);
  closeDetailBtn.addEventListener('click', ()=>{detailSection.style.display='none';});
  backBtn.addEventListener('click', ()=>{
    window.location.href = `/session/${SESSION_TOKEN}`;
  });

  // initial load
  loadDangerousPerms();
  loadTips();
});
