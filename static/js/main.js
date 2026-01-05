document.addEventListener('DOMContentLoaded', function(){
  const form = document.getElementById('qr-form');
  const img = document.getElementById('qr-image');
  const spinner = document.getElementById('spinner');
  const downloadBtn = document.getElementById('download-btn');
  const generateBtn = document.getElementById('generate-btn');
  const card = document.getElementById('card');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = document.getElementById('text').value.trim();
    if (!text) return;
    const size = parseInt(document.getElementById('size').value, 10) || 10;
    // UI: show spinner, disable generate
    if (spinner) spinner.style.display = '';
    if (generateBtn) generateBtn.disabled = true;
    try {
      const res = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, size })
      });
      const data = await res.json();
      if (data.error) {
        alert(data.error + (data.detail ? '\n' + data.detail : ''));
        return;
      }
      img.src = data.data_url;
      if (downloadBtn){
        downloadBtn.href = data.data_url;
        downloadBtn.style.display = '';
      }
    } catch (err) {
      console.error(err);
      alert('Failed to generate QR');
    } finally {
      if (spinner) spinner.style.display = 'none';
      if (generateBtn) generateBtn.disabled = false;
    }
  });

  // subtle 3D parallax on mouse move
  if (card){
    card.addEventListener('mousemove', (ev)=>{
      const w = card.clientWidth, h = card.clientHeight;
      const x = (ev.offsetX - w/2)/(w/2);
      const y = (ev.offsetY - h/2)/(h/2);
      card.style.transform = `translateY(-6px) rotateX(${ -y * 3 }deg) rotateY(${ x * 6 }deg)`;
    });
    card.addEventListener('mouseleave', ()=>{ card.style.transform = '' });
  }
});
