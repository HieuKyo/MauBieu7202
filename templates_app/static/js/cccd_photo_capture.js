// Chụp CCCD 2 mặt → in A5 (dùng chung cho In mẫu biểu và Doanh nghiệp).
// Cần nạp SAU giao diện includes/cccd_photo_modal.html và sau các hàm camera dùng chung
// (openCameraInto, savedCameraId, renderCameraHelp, cameraWaitHtml, cccdBrowser, beepCccdQr).

// ============================================
// Chụp CCCD 2 mặt → in A5 ngang (trái mặt trước, phải mặt sau)
// Chỉ cắt vùng trong khung hướng dẫn (tỉ lệ thẻ 85.6 x 54mm) → 2 ảnh cùng kích thước, in đúng cỡ thẻ thật
// ============================================

const CCCD_RATIO = 85.6 / 54;
const CCCD_OUT_W = 1518, CCCD_OUT_H = 957;   // ~450 dpi ở cỡ thẻ thật (giữ đủ chi tiết từ webcam Full HD)
let cccdPhotoStream = null;
let cccdPhotoModalOpen = false;
let cccdPhotoCrop = null;                     // vùng cắt theo pixel gốc của video
const cccdPhotos = { front: null, back: null };       // ảnh đã chuẩn hóa (dataURL) để in
const cccdPhotoSources = { front: null, back: null }; // ảnh gốc (canvas) để xoay không bị mờ

function stopCccdPhotoCamera() {
    if (cccdPhotoStream) {
        cccdPhotoStream.getTracks().forEach(t => t.stop());
        cccdPhotoStream = null;
    }
}

// Khung hướng dẫn = vùng cắt ảnh (pixel gốc của video), luôn đúng tỉ lệ thẻ.
// Mặc định: rộng 80% khung hình (tối đa cao 85%), nằm giữa. GĐV chỉnh được và được nhớ theo từng camera
// (máy đặt thẻ trên giá cố định → chỉnh 1 lần là các lần sau vừa khít).
function cccdGuideKey() {
    const track = cccdPhotoStream && cccdPhotoStream.getVideoTracks()[0];
    return track ? 'cccdGuide:' + track.label : null;
}

function defaultCccdGuide(vw, vh) {
    let w = vw * 0.8, h = w / CCCD_RATIO;
    if (h > vh * 0.85) { h = vh * 0.85; w = h * CCCD_RATIO; }
    return { x: (vw - w) / 2, y: (vh - h) / 2, w, h };
}

// Giữ khung trong khung hình, đúng tỉ lệ thẻ, không nhỏ hơn 25% chiều ngang
function clampCccdGuide(c, vw, vh) {
    let w = Math.min(Math.max(c.w, vw * 0.25), vw, vh * CCCD_RATIO);
    const h = w / CCCD_RATIO;
    return { x: Math.min(Math.max(c.x, 0), vw - w), y: Math.min(Math.max(c.y, 0), vh - h), w, h };
}

function applyCccdGuide(c, save) {
    const video = document.getElementById('cccdPhotoVideo');
    const vw = video.videoWidth, vh = video.videoHeight;
    if (!vw || !vh) return;
    cccdPhotoCrop = clampCccdGuide(c, vw, vh);

    const guide = document.getElementById('cccdPhotoGuide');
    guide.style.left = `${cccdPhotoCrop.x / vw * 100}%`;
    guide.style.top = `${cccdPhotoCrop.y / vh * 100}%`;
    guide.style.width = `${cccdPhotoCrop.w / vw * 100}%`;
    guide.style.height = `${cccdPhotoCrop.h / vh * 100}%`;

    const key = cccdGuideKey();
    if (save && key) {
        // Lưu theo tỉ lệ khung hình để vẫn đúng nếu độ phân giải đổi
        const r = { x: cccdPhotoCrop.x / vw, y: cccdPhotoCrop.y / vh, w: cccdPhotoCrop.w / vw };
        try { localStorage.setItem(key, JSON.stringify(r)); } catch (e) {}
    }
}

function layoutCccdPhotoGuide() {
    const video = document.getElementById('cccdPhotoVideo');
    const vw = video.videoWidth, vh = video.videoHeight;
    if (!vw || !vh) return;
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem(cccdGuideKey())); } catch (e) {}
    applyCccdGuide(saved ? { x: saved.x * vw, y: saved.y * vh, w: saved.w * vw, h: saved.w * vw / CCCD_RATIO }
                         : defaultCccdGuide(vw, vh), false);
}

function resizeCccdGuide(factor) {
    if (!cccdPhotoCrop) return;
    const c = cccdPhotoCrop, w = c.w * factor, h = w / CCCD_RATIO;
    // Phóng to / thu nhỏ quanh tâm khung
    applyCccdGuide({ x: c.x + (c.w - w) / 2, y: c.y + (c.h - h) / 2, w, h }, true);
}

function resetCccdGuide() {
    const key = cccdGuideKey();
    try { if (key) localStorage.removeItem(key); } catch (e) {}
    layoutCccdPhotoGuide();
}

// Kéo chuột / chạm: kéo khung để di chuyển, kéo nút tròn ở góc để đổi cỡ (neo góc trên-trái)
(function initCccdGuideDrag() {
    const guide = document.getElementById('cccdPhotoGuide');
    const handle = document.getElementById('cccdPhotoGuideHandle');
    const video = document.getElementById('cccdPhotoVideo');
    let drag = null;

    const start = (e, mode) => {
        if (!cccdPhotoCrop || !video.videoWidth) return;
        e.preventDefault();
        e.stopPropagation();
        drag = { mode, x0: e.clientX, y0: e.clientY, crop: Object.assign({}, cccdPhotoCrop),
                 scale: video.videoWidth / video.clientWidth };   // px màn hình → px gốc của video
        (e.target).setPointerCapture(e.pointerId);
    };
    guide.addEventListener('pointerdown', e => start(e, 'move'));
    handle.addEventListener('pointerdown', e => start(e, 'resize'));

    const moveTo = e => {
        if (!drag) return;
        const dx = (e.clientX - drag.x0) * drag.scale, dy = (e.clientY - drag.y0) * drag.scale;
        const c = drag.crop;
        if (drag.mode === 'move') {
            applyCccdGuide({ x: c.x + dx, y: c.y + dy, w: c.w, h: c.h }, false);
        } else {
            // Lấy thay đổi theo chiều kéo nhiều hơn (ngang hoặc dọc, quy về chiều ngang) → kéo ra phóng to, kéo vào thu nhỏ
            const dw = Math.abs(dx) >= Math.abs(dy * CCCD_RATIO) ? dx : dy * CCCD_RATIO;
            const w = c.w + dw;
            applyCccdGuide({ x: c.x, y: c.y, w, h: w / CCCD_RATIO }, false);
        }
    };
    const end = () => {
        if (!drag) return;
        drag = null;
        applyCccdGuide(cccdPhotoCrop, true);
    };
    [guide, handle].forEach(el => {
        el.addEventListener('pointermove', moveTo);
        el.addEventListener('pointerup', end);
        el.addEventListener('pointercancel', end);
    });
})();

function nextCccdSide() {
    return !cccdPhotos.front ? 'front' : !cccdPhotos.back ? 'back' : null;
}

function refreshCccdPhotoUi() {
    const side = nextCccdSide();
    const label = side === 'front' ? 'MẶT TRƯỚC' : side === 'back' ? 'MẶT SAU' : '';
    document.getElementById('cccdPhotoGuideLabel').textContent = label ? `Đặt ${label} thẻ vừa khung vàng` : 'Đã chụp đủ 2 mặt';
    document.getElementById('cccdPhotoShootText').textContent = label ? `Chụp ${label.toLowerCase()}` : 'Đã chụp đủ 2 mặt';
    document.getElementById('cccdPhotoShootBtn').disabled = !side || !cccdPhotoStream;
    document.getElementById('cccdPhotoPrintBtn').disabled = !(cccdPhotos.front && cccdPhotos.back);

    document.querySelectorAll('#cccdPhotoModal .cccd-photo-slot').forEach(slot => {
        const src = cccdPhotos[slot.dataset.side];
        slot.innerHTML = src
            ? `<img src="${src}" class="w-100 h-100 rounded" style="object-fit:cover;">`
            : '<span class="text-muted small">Chưa chụp</span>';
    });
}

async function startCccdPhotoCamera(deviceId, manual = false) {
    stopCccdPhotoCamera();
    const status = document.getElementById('cccdPhotoStatus');
    status.className = 'small text-muted mt-2';
    status.innerHTML = cameraWaitHtml();
    document.getElementById('cccdPhotoHelp').innerHTML = '';
    let stream;
    try {
        stream = await openCameraInto('cccdPhotoVideo', 'cccdPhotoCameraSelect', deviceId, 3840, 2160, manual);
    } catch (error) {
        status.className = 'small text-danger mt-2';
        status.textContent = 'Chưa dùng được camera — làm theo hướng dẫn bên dưới, hoặc bấm "Tải ảnh" nếu đã có sẵn file ảnh.';
        renderCameraHelp('cccdPhotoHelp', error.message, 'startCccdPhotoCamera(savedCameraId())', error.detail);
        refreshCccdPhotoUi();
        return;
    }
    if (!cccdPhotoModalOpen) {
        stream.getTracks().forEach(t => t.stop());
        return;
    }
    cccdPhotoStream = stream;
    layoutCccdPhotoGuide();
    const track = stream.getVideoTracks()[0];
    const { width = 0, height = 0 } = track.getSettings();
    const lowRes = width < 1280;
    status.className = `small mt-2 ${lowRes ? 'text-danger' : 'text-muted'}`;
    status.innerHTML = `Camera: <strong>${track.label.replace(/[&<>"']/g, '')}</strong> · độ phân giải <strong>${width}×${height}</strong>`
        + (lowRes ? ' — <strong>thấp, ảnh sẽ kém nét</strong>: thử chọn camera khác ở ô Camera hoặc mở trang bằng Edge/Chrome.' : '')
        + '<br>Đặt thẻ trên nền phẳng, đủ sáng, vừa khít khung vàng rồi bấm Chụp (hoặc phím Space).';
    buildCameraTuning(track);
    refreshCccdPhotoUi();
}

// ---- Chỉnh thông số webcam qua trình duyệt (Chrome/Edge hỗ trợ; Firefox không) ----
// Giá trị GĐV chỉnh được nhớ theo tên camera và tự áp dụng lần sau.
const CAM_TUNE_PARAMS = [
    ['sharpness', 'Độ nét'],
    ['contrast', 'Tương phản'],
    ['brightness', 'Độ sáng'],
    ['saturation', 'Độ đậm màu'],
    ['exposureCompensation', 'Bù sáng'],
    ['focusDistance', 'Lấy nét tay (khoảng cách)'],
    ['zoom', 'Phóng to'],
];

function camTuneKey(track) { return 'cccdCamTune:' + track.label; }

function loadCamTune(track) {
    try { return JSON.parse(localStorage.getItem(camTuneKey(track))) || {}; } catch (e) { return {}; }
}

async function applyCamTune(track, values) {
    const c = Object.assign({}, values);
    if ('focusDistance' in c) c.focusMode = 'manual';   // lấy nét tay cần tắt lấy nét tự động
    try { await track.applyConstraints({ advanced: [c] }); } catch (e) {}
}

async function buildCameraTuning(track) {
    const box = document.getElementById('cccdPhotoTune');
    const caps = track.getCapabilities ? track.getCapabilities() : {};
    const params = CAM_TUNE_PARAMS.filter(([k]) => caps[k] && caps[k].max > caps[k].min);
    if (!params.length) {
        box.innerHTML = `<div class="text-muted">Webcam hoặc trình duyệt này không cho chỉnh thông số
            ${cccdBrowser() === 'firefox' ? '(Firefox không hỗ trợ — mở bằng <strong>Edge/Chrome</strong> để chỉnh)' : ''}.
            Hãy bật <strong>Tăng nét chữ</strong> bên dưới. Có thể chỉnh độ nét trong phần mềm của webcam (vd. CyberLink),
            nhiều webcam giữ lại thông số đó cho mọi chương trình.</div>`;
        return;
    }

    // Áp dụng lại thông số đã nhớ cho camera này; giữ thông số gốc để nút "Mặc định" trả về
    const original = track.getSettings();
    const saved = loadCamTune(track);
    if (Object.keys(saved).length) await applyCamTune(track, saved);
    const current = track.getSettings();

    box.innerHTML = params.map(([k, label]) => {
        const cap = caps[k];
        const val = current[k] ?? cap.min;
        return `<div class="row g-2 align-items-center mb-1">
            <label class="col-4 col-form-label py-0">${label}</label>
            <div class="col-6"><input type="range" class="form-range" data-param="${k}"
                min="${cap.min}" max="${cap.max}" step="${cap.step || 1}" value="${val}"></div>
            <div class="col-2 text-end" data-out="${k}">${val}</div>
        </div>`;
    }).join('') + `<div class="d-flex gap-2 mt-1">
            <button type="button" class="btn btn-sm btn-outline-primary" data-tune="text">Gợi ý cho chữ rõ</button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-tune="reset">Mặc định</button>
        </div>
        ${caps.focusDistance ? '<div class="text-muted mt-1">Kéo "Lấy nét tay" sẽ tắt tự động lấy nét. Bấm "Mặc định" để bật lại.</div>' : ''}`;

    const sliders = [...box.querySelectorAll('input[data-param]')];
    // Chỉ nhớ thông số GĐV đã thay đổi (không nhớ "Lấy nét tay" nếu chưa chạm vào → giữ tự động lấy nét)
    const changed = Object.assign({}, saved);
    const save = () => {
        try { localStorage.setItem(camTuneKey(track), JSON.stringify(changed)); } catch (e) {}
    };
    sliders.forEach(sl => sl.addEventListener('input', () => {
        changed[sl.dataset.param] = Number(sl.value);
        box.querySelector(`[data-out="${sl.dataset.param}"]`).textContent = sl.value;
        applyCamTune(track, { [sl.dataset.param]: Number(sl.value) });
        save();
    }));

    // Gợi ý: độ nét & tương phản ở mức 75% thang của webcam (chữ rõ hơn, chưa bị vỡ hạt)
    box.querySelector('[data-tune="text"]').addEventListener('click', () => {
        const v = {};
        ['sharpness', 'contrast'].forEach(k => {
            const sl = sliders.find(x => x.dataset.param === k);
            if (!sl) return;
            const cap = caps[k];
            const step = cap.step || 1;
            v[k] = cap.min + Math.round((cap.max - cap.min) * 0.75 / step) * step;
            changed[k] = v[k];
            sl.value = v[k];
            box.querySelector(`[data-out="${k}"]`).textContent = v[k];
        });
        applyCamTune(track, v);
        save();
    });

    box.querySelector('[data-tune="reset"]').addEventListener('click', async () => {
        try { localStorage.removeItem(camTuneKey(track)); } catch (e) {}
        const v = {};
        params.forEach(([k]) => { if (original[k] !== undefined) v[k] = original[k]; });
        delete v.focusDistance;
        try { await track.applyConstraints({ advanced: [Object.assign(v, caps.focusMode && caps.focusMode.includes('continuous') ? { focusMode: 'continuous' } : {})] }); } catch (e) {}
        buildCameraTuning(track);
    });
}

let cccdShooting = false;

// Độ nét của ảnh = phương sai Laplacian (ảnh mờ/rung → giá trị nhỏ)
function cccdSharpness(src) {
    const w = 640, h = Math.round(640 * src.height / src.width);
    const c = document.createElement('canvas');
    c.width = w;
    c.height = h;
    const ctx = c.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(src, 0, 0, w, h);
    const d = ctx.getImageData(0, 0, w, h).data;
    const g = new Float32Array(w * h);
    for (let i = 0; i < w * h; i++) g[i] = d[i * 4] * 0.299 + d[i * 4 + 1] * 0.587 + d[i * 4 + 2] * 0.114;
    let sum = 0, sum2 = 0, n = 0;
    for (let y = 1; y < h - 1; y++) {
        for (let x = 1; x < w - 1; x++) {
            const i = y * w + x;
            const lap = 4 * g[i] - g[i - 1] - g[i + 1] - g[i - w] - g[i + w];
            sum += lap;
            sum2 += lap * lap;
            n++;
        }
    }
    return sum2 / n - (sum / n) ** 2;
}

// Chụp liền 5 khung hình trong ~0.6 giây, giữ khung NÉT NHẤT (tránh ảnh mờ do rung tay / camera đang lấy nét)
async function shootCccdPhoto() {
    const side = nextCccdSide();
    const video = document.getElementById('cccdPhotoVideo');
    if (!side || !cccdPhotoStream || !cccdPhotoCrop || cccdShooting) return;

    cccdShooting = true;
    const btn = document.getElementById('cccdPhotoShootBtn');
    btn.disabled = true;
    document.getElementById('cccdPhotoShootText').textContent = 'Đang chụp... giữ yên thẻ';

    const c = cccdPhotoCrop;
    let best = null, bestScore = -1;
    for (let i = 0; i < 5 && cccdPhotoStream; i++) {
        if (i) await new Promise(r => setTimeout(r, 150));
        const frame = document.createElement('canvas');
        frame.width = Math.round(c.w);
        frame.height = Math.round(c.h);
        frame.getContext('2d').drawImage(video, c.x, c.y, c.w, c.h, 0, 0, frame.width, frame.height);
        const score = cccdSharpness(frame);
        if (score > bestScore) { best = frame; bestScore = score; }
    }
    cccdShooting = false;
    if (!cccdPhotoStream || !best) { refreshCccdPhotoUi(); return; }   // đóng cửa sổ giữa chừng
    setCccdPhotoSource(side, best);
    beepCccdQr();
}

// Đưa ảnh gốc vào khung chuẩn 1518x957 (tỉ lệ thẻ): giữ nguyên toàn bộ ảnh, phần thừa để nền trắng
// "Tăng nét chữ": kéo giãn tương phản (bỏ 1% điểm tối/sáng nhất) + làm nét (unsharp mask) — giống phần mềm webcam
function isCccdEnhanceOn() {
    return document.getElementById('cccdPhotoEnhance').checked;
}

function enhanceCccdCanvas(canvas) {
    const w = canvas.width, h = canvas.height;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const img = ctx.getImageData(0, 0, w, h);
    const d = img.data;

    // 1) Tương phản tự động theo độ sáng: chỉ kéo giãn độ sáng, cộng cùng một lượng vào R, G, B để giữ nguyên màu
    const hist = new Uint32Array(256);
    for (let i = 0; i < d.length; i += 4) hist[(d[i] * 77 + d[i + 1] * 150 + d[i + 2] * 29) >> 8]++;
    const total = w * h;
    let lo = 0, hi = 255, acc = 0;
    while (lo < 255 && (acc += hist[lo]) < total * 0.01) lo++;
    acc = 0;
    while (hi > 0 && (acc += hist[hi]) < total * 0.01) hi--;
    const range = Math.max(hi - lo, 1);
    const lut = new Uint8ClampedArray(256);
    for (let v = 0; v < 256; v++) lut[v] = (v - lo) * 255 / range;
    for (let i = 0; i < d.length; i += 4) {
        const y = (d[i] * 77 + d[i + 1] * 150 + d[i + 2] * 29) >> 8;
        const delta = lut[y] - y;
        d[i] += delta;
        d[i + 1] += delta;
        d[i + 2] += delta;
    }
    ctx.putImageData(img, 0, 0);

    // 2) Làm nét: ảnh + 1.0 × (ảnh − ảnh làm mờ 1.2px)
    const blur = document.createElement('canvas');
    blur.width = w;
    blur.height = h;
    const bctx = blur.getContext('2d', { willReadFrequently: true });
    if (!('filter' in bctx)) return;   // trình duyệt cũ không có canvas filter → chỉ tăng tương phản
    bctx.filter = 'blur(1.2px)';
    bctx.drawImage(canvas, 0, 0);
    const b = bctx.getImageData(0, 0, w, h).data;
    const sharp = ctx.getImageData(0, 0, w, h);
    const sd = sharp.data;
    for (let i = 0; i < sd.length; i += 4) {
        sd[i] = sd[i] + (sd[i] - b[i]);
        sd[i + 1] = sd[i + 1] + (sd[i + 1] - b[i + 1]);
        sd[i + 2] = sd[i + 2] + (sd[i + 2] - b[i + 2]);
    }
    ctx.putImageData(sharp, 0, 0);
}

function onCccdEnhanceChange(on) {
    try { localStorage.setItem('cccdPhotoEnhance', on ? '1' : '0'); } catch (e) {}
    // Xử lý lại ảnh đã chụp từ ảnh gốc
    ['front', 'back'].forEach(side => { if (cccdPhotoSources[side]) setCccdPhotoSource(side, cccdPhotoSources[side]); });
}

function setCccdPhotoSource(side, src) {
    cccdPhotoSources[side] = src;
    const out = document.createElement('canvas');
    out.width = CCCD_OUT_W;
    out.height = CCCD_OUT_H;
    const ctx = out.getContext('2d');
    ctx.imageSmoothingQuality = 'high';
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, CCCD_OUT_W, CCCD_OUT_H);
    const scale = Math.min(CCCD_OUT_W / src.width, CCCD_OUT_H / src.height);
    const w = src.width * scale, h = src.height * scale;
    ctx.drawImage(src, (CCCD_OUT_W - w) / 2, (CCCD_OUT_H - h) / 2, w, h);
    if (isCccdEnhanceOn()) enhanceCccdCanvas(out);
    cccdPhotos[side] = out.toDataURL('image/jpeg', 0.95);
    refreshCccdPhotoUi();
}

function rotateCccdPhoto(side) {
    const src = cccdPhotoSources[side];
    if (!src) return;
    const rotated = document.createElement('canvas');
    rotated.width = src.height;
    rotated.height = src.width;
    const ctx = rotated.getContext('2d');
    ctx.translate(rotated.width, 0);
    ctx.rotate(Math.PI / 2);
    ctx.drawImage(src, 0, 0);
    setCccdPhotoSource(side, rotated);
}

// GĐV có sẵn file ảnh (scan / chụp điện thoại): ảnh dọc tự xoay ngang, sai chiều thì bấm "Xoay"
function uploadCccdPhoto(side, input) {
    const file = input.files[0];
    input.value = '';   // cho phép chọn lại cùng file
    if (!file) return;
    const img = new Image();
    img.onload = () => {
        const src = document.createElement('canvas');
        src.width = img.naturalWidth;
        src.height = img.naturalHeight;
        src.getContext('2d').drawImage(img, 0, 0);
        URL.revokeObjectURL(img.src);
        setCccdPhotoSource(side, src);
        if (src.height > src.width) rotateCccdPhoto(side);
    };
    img.onerror = () => alert('Không đọc được file ảnh. Vui lòng chọn file JPG hoặc PNG.');
    img.src = URL.createObjectURL(file);
}

function retakeCccdPhoto(side) {
    // Chụp lại 1 mặt: xóa mặt đó (nếu xóa mặt trước khi đã có mặt sau thì mặt trước sẽ được chụp tiếp theo)
    cccdPhotos[side] = cccdPhotoSources[side] = null;
    refreshCccdPhotoUi();
}

function printCccdPhotos() {
    if (!cccdPhotos.front || !cccdPhotos.back) return;
    const esc = s => String(s).replace(/[&<>"']/g, c => `&#${c.charCodeAt(0)};`);
    const diaDanh = esc(document.getElementById('cccdPhotoDiaDanh').value.trim() || '..................');

    const html = `<!doctype html><html><head><meta charset="utf-8"><title>CCCD 2 mặt</title><style>
        @page { size: A5 landscape; margin: 0; }
        html, body { margin: 0; }
        /* Toàn bộ nội dung canh giữa trang A5 (ngang và dọc) */
        body { width: 210mm; height: 148mm; overflow: hidden; display: flex; flex-direction: column;
               align-items: center; justify-content: center;
               font-family: "Times New Roman", serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .cards { display: flex; gap: 10mm; }
        .cards img { width: 85.6mm; height: 54mm; display: block; border: 0.3mm solid #555; border-radius: 3mm; }
        .note { margin-top: 10mm; text-align: center; font-size: 13pt; line-height: 1.7; }
        .sign-space { height: 20mm; }   /* chỗ ký của người đối chiếu */
    </style></head><body>
        <div class="cards"><img src="${cccdPhotos.front}"><img src="${cccdPhotos.back}"></div>
        <div class="note">
            <div><b>ĐÃ ĐỐI CHIẾU KHỚP ĐÚNG VỚI BẢN GỐC</b></div>
            <div><i>${diaDanh}, ngày ...... tháng ...... năm ........</i></div>
            <div><b>Người đối chiếu</b></div>
            <div class="sign-space"></div>
        </div>
    </body></html>`;

    const iframe = document.createElement('iframe');
    iframe.style.cssText = 'position:fixed; right:0; bottom:0; width:0; height:0; border:0;';
    document.body.appendChild(iframe);
    const doc = iframe.contentDocument;
    doc.open();
    doc.write(html);
    doc.close();
    Promise.all([...doc.images].map(img => img.decode())).then(() => {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
        setTimeout(() => iframe.remove(), 1000);
    });
}

const cccdPhotoModalEl = document.getElementById('cccdPhotoModal');
cccdPhotoModalEl.addEventListener('shown.bs.modal', () => {
    cccdPhotoModalOpen = true;
    let enhance = '1';
    try { enhance = localStorage.getItem('cccdPhotoEnhance') ?? '1'; } catch (e) {}
    document.getElementById('cccdPhotoEnhance').checked = enhance === '1';
    refreshCccdPhotoUi();
    startCccdPhotoCamera(savedCameraId());
});
cccdPhotoModalEl.addEventListener('hidden.bs.modal', () => {
    // Xóa ảnh khi đóng để không in nhầm ảnh của khách trước cho khách sau
    cccdPhotoModalOpen = false;
    stopCccdPhotoCamera();
    cccdPhotos.front = cccdPhotos.back = null;
    cccdPhotoSources.front = cccdPhotoSources.back = null;
});
// Phím Space = Chụp. Chặn cả keyup để Space không "bấm" thêm nút đang được focus (tránh chụp 2 lần / bấm nhầm Đóng)
const isCccdShootKey = e => e.code === 'Space' && !['INPUT', 'SELECT', 'SUMMARY'].includes(e.target.tagName);
cccdPhotoModalEl.addEventListener('keydown', e => {
    if (!isCccdShootKey(e)) return;
    e.preventDefault();
    if (!e.repeat) shootCccdPhoto();
});
cccdPhotoModalEl.addEventListener('keyup', e => { if (isCccdShootKey(e)) e.preventDefault(); });
// Phím mũi tên: dịch khung vàng (giữ Shift để dịch nhanh); phím + / -: phóng to / thu nhỏ khung
cccdPhotoModalEl.addEventListener('keydown', e => {
    if (!cccdPhotoCrop || ['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) return;
    const step = (e.shiftKey ? 0.02 : 0.004) * document.getElementById('cccdPhotoVideo').videoWidth;
    const move = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }[e.key];
    if (move) {
        e.preventDefault();
        const c = cccdPhotoCrop;
        applyCccdGuide({ x: c.x + move[0], y: c.y + move[1], w: c.w, h: c.h }, true);
    } else if (e.key === '+' || e.key === '=') {
        e.preventDefault();
        resizeCccdGuide(1.02);
    } else if (e.key === '-') {
        e.preventDefault();
        resizeCccdGuide(0.98);
    }
});
document.getElementById('cccdPhotoVideo').addEventListener('loadedmetadata', layoutCccdPhotoGuide);
// Camera có thể đổi độ phân giải sau khi đã mở (vài khung hình đầu nhỏ, hoặc nâng độ phân giải sau khi mở dự phòng)
// → tính lại khung vàng theo kích thước mới (vị trí GĐV đã chỉnh được lưu theo tỉ lệ nên vẫn giữ đúng)
document.getElementById('cccdPhotoVideo').addEventListener('resize', layoutCccdPhotoGuide);
