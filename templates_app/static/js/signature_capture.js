// Chụp ảnh chữ ký cho từng khách hàng (tab Khách hàng) → lưu trên máy chủ, đưa vào file ZIP "Folder chữ ký".
// Cần nạp sau cccd_qr_scanner.js (openCameraInto, renderCameraHelp, cameraWaitHtml, beepCccdQr...).

// Ảnh chữ ký lưu đúng 640x328 px; chụp bằng camera riêng (nhớ riêng, không ghi đè camera 2K dùng cho QR / chụp thẻ)
const SIG_W = 640, SIG_H = 328, SIG_RATIO = SIG_W / SIG_H;
let sigCustomerId = null;
let sigStream = null;
let sigModalOpen = false;
let sigCrop = null;
let sigShot = null;                  // ảnh vừa chụp (canvas), chưa lưu
let sigBusy = false;

function sigEl(id) { return document.getElementById(id); }

function openSignatureModal(customerId) {
    sigCustomerId = customerId;
    bootstrap.Modal.getOrCreateInstance(sigEl('signatureModal')).show();
}

function stopSigCamera() {
    if (sigStream) { sigStream.getTracks().forEach(t => t.stop()); sigStream = null; }
}

// Khung chữ ký: rộng 85% khung hình (tối đa cao 80%), nằm giữa
function layoutSigGuide() {
    const v = sigEl('sigVideo'), vw = v.videoWidth, vh = v.videoHeight;
    if (!vw || !vh) return;
    let w = vw * 0.85, h = w / SIG_RATIO;
    if (h > vh * 0.8) { h = vh * 0.8; w = h * SIG_RATIO; }
    sigCrop = { x: (vw - w) / 2, y: (vh - h) / 2, w, h };
    const g = sigEl('sigGuide');
    g.style.left = `${sigCrop.x / vw * 100}%`; g.style.top = `${sigCrop.y / vh * 100}%`;
    g.style.width = `${w / vw * 100}%`; g.style.height = `${h / vh * 100}%`;
}

function showSigShot(canvas) {
    sigShot = canvas;
    sigEl('sigPreview').src = canvas ? canvas.toDataURL('image/jpeg', 0.9) : '';
    sigEl('sigPreview').classList.toggle('d-none', !canvas);
    sigEl('sigGuide').classList.toggle('d-none', !!canvas);
    sigEl('sigShootBtn').classList.toggle('d-none', !!canvas);
    sigEl('sigRetakeBtn').classList.toggle('d-none', !canvas);
    sigEl('sigSaveBtn').classList.toggle('d-none', !canvas);
}

function renderSigList(data) {
    sigEl('sigTitle').textContent = ` — ${data.ho_ten}` + (data.ma_khach_hang ? ` (Mã KH ${data.ma_khach_hang})` : '');
    sigEl('sigNoCode').classList.toggle('d-none', !!data.ma_khach_hang);
    const esc = s => String(s).replace(/[&<>"']/g, c => `&#${c.charCodeAt(0)};`);
    sigEl('sigList').innerHTML = data.files.length
        ? data.files.map(f => `<div class="col-6 col-md-4"><div class="border rounded p-1 text-center">
              <a href="${f.url}" target="_blank"><img src="${f.url}" class="img-fluid rounded" style="max-height:110px"></a>
              <div class="small text-muted text-truncate">${esc(f.name)}</div>
              <button type="button" class="btn btn-sm btn-outline-danger mt-1" onclick="deleteSignature('${f.delete_url}')"><i class="bi bi-trash"></i> Xóa</button>
          </div></div>`).join('')
        : '<div class="col-12 text-muted small">Chưa có ảnh chữ ký.</div>';
    const badge = document.querySelector(`[data-sig-count="${sigCustomerId}"]`);
    if (badge) { badge.textContent = data.files.length; badge.classList.toggle('d-none', !data.files.length); }
}

function sigCsrf() { return document.querySelector('[name=csrfmiddlewaretoken]').value; }

function loadSignatures() {
    return fetch(`/customers/${sigCustomerId}/signatures/`).then(r => r.json()).then(renderSigList);
}

function savedSigCameraId() {
    try { return localStorage.getItem('sigCameraId'); } catch (e) { return null; }
}

// openCameraInto() nhớ camera vào khóa chung của Quét QR / Chụp thẻ → trả lại camera đó sau khi mở camera chữ ký
let sigCardCamera = null;
function keepCardCamera() {
    try {
        if (sigCardCamera) localStorage.setItem('cccdQrCameraId', sigCardCamera);
        else localStorage.removeItem('cccdQrCameraId');
    } catch (e) {}
}

async function startSigCamera(deviceId, manual = false) {
    stopSigCamera();
    sigCardCamera = savedCameraId();
    showSigShot(null);
    const status = sigEl('sigStatus');
    status.className = 'small text-muted mt-2';
    status.innerHTML = cameraWaitHtml();
    sigEl('sigHelp').innerHTML = '';
    sigEl('sigShootBtn').disabled = true;
    let stream;
    try {
        stream = await openCameraInto('sigVideo', 'sigCameraSelect', deviceId, 1280, 720, manual);
    } catch (error) {
        keepCardCamera();
        status.className = 'small text-danger mt-2';
        status.textContent = 'Chưa dùng được camera — làm theo hướng dẫn bên dưới.';
        renderCameraHelp('sigHelp', error.message, 'startSigCamera(savedSigCameraId())', error.detail);
        return;
    }
    keepCardCamera();
    if (!sigModalOpen) { stream.getTracks().forEach(t => t.stop()); return; }
    sigStream = stream;
    const track = stream.getVideoTracks()[0];
    try { localStorage.setItem('sigCameraId', track.getSettings().deviceId); } catch (e) {}
    layoutSigGuide();
    const { width = 0, height = 0 } = track.getSettings();
    status.innerHTML = `Camera: <strong>${track.label.replace(/[&<>"']/g, '')}</strong> · ${width}×${height}`
        + '<br>Đặt chữ ký trên giấy trắng, đủ sáng, nằm trong khung vàng rồi bấm Chụp (hoặc phím Space).';
    sigEl('sigShootBtn').disabled = false;
}

// Chụp 1 khung, cắt đúng khung vàng, thu về 640x328 px
function shootSignature() {
    if (!sigStream || !sigCrop || sigShot || sigBusy) return;
    const c = document.createElement('canvas');
    c.width = SIG_W;
    c.height = SIG_H;
    const ctx = c.getContext('2d');
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(sigEl('sigVideo'), sigCrop.x, sigCrop.y, sigCrop.w, sigCrop.h, 0, 0, SIG_W, SIG_H);
    showSigShot(c);
    beepCccdQr();
}

function saveSignature() {
    if (!sigShot || sigBusy) return;
    sigBusy = true;
    sigEl('sigSaveBtn').disabled = true;
    sigShot.toBlob(blob => {
        const fd = new FormData();
        fd.append('image', blob, 'chu_ky.jpg');
        fetch(`/customers/${sigCustomerId}/signatures/`, { method: 'POST', body: fd, headers: { 'X-CSRFToken': sigCsrf() } })
            .then(r => {
                const isJson = (r.headers.get('Content-Type') || '').includes('application/json');
                if (isJson) return r.json();
                // Hết phiên đăng nhập (trả về trang đăng nhập) / không có quyền / máy chủ lỗi
                throw new Error(r.redirected || r.status === 403
                    ? 'Phiên đăng nhập đã hết hạn. Hãy tải lại trang (F5), đăng nhập rồi chụp lại.'
                    : `Máy chủ báo lỗi (mã ${r.status}).`);
            })
            .then(data => {
                if (!data.success) throw new Error(data.error);
                renderSigList(data);
                showSigShot(null);
                sigEl('sigStatus').innerHTML = '<span class="text-success"><i class="bi bi-check-circle-fill"></i> Đã lưu ảnh chữ ký.</span>';
            })
            .catch(e => {
                // "Failed to fetch": mất kết nối tới máy chủ (mạng / máy chủ đang khởi động lại). Ảnh vừa chụp vẫn giữ để bấm Lưu lại.
                const msg = e instanceof TypeError
                    ? 'Không kết nối được tới máy chủ (mạng chập chờn hoặc máy chủ đang khởi động lại).\nẢnh vừa chụp vẫn còn — đợi vài giây rồi bấm "Lưu chữ ký" lại.'
                    : e.message;
                alert('Không lưu được ảnh chữ ký:\n' + msg);
            })
            .finally(() => { sigBusy = false; sigEl('sigSaveBtn').disabled = false; });
    }, 'image/jpeg', 0.92);
}

function deleteSignature(url) {
    if (!confirm('Xóa ảnh chữ ký này?')) return;
    fetch(url, { method: 'POST', headers: { 'X-CSRFToken': sigCsrf() } })
        .then(r => r.json()).then(renderSigList)
        .catch(e => alert('Không xóa được: ' + e.message));
}

(function initSignatureModal() {
    const modal = sigEl('signatureModal');
    if (!modal) return;
    modal.addEventListener('shown.bs.modal', () => {
        sigModalOpen = true;
        sigEl('sigList').innerHTML = '';
        loadSignatures();
        startSigCamera(savedSigCameraId());
    });
    modal.addEventListener('hidden.bs.modal', () => {
        sigModalOpen = false;
        stopSigCamera();
        showSigShot(null);
    });
    modal.addEventListener('keydown', e => {
        if (e.code !== 'Space' || ['INPUT', 'SELECT', 'TEXTAREA', 'BUTTON', 'A'].includes(e.target.tagName)) return;
        e.preventDefault();
        if (!e.repeat) shootSignature();
    });
    sigEl('sigVideo').addEventListener('loadedmetadata', layoutSigGuide);
    sigEl('sigVideo').addEventListener('resize', layoutSigGuide);
})();
