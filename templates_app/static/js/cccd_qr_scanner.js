// Quét QR CCCD / Căn cước bằng webcam — dùng chung cho các form (vd. business/form.html).
// Tách từ dashboard.html (dashboard.html vẫn giữ bản riêng của mình).
// Trang dùng file này cần có:
//   - Modal #cccdQrModal (các id: cccdQrCameraSelect, cccdQrVideo, cccdQrSuccess, cccdQrSuccessName, cccdQrStatus, cccdQrHelp, cccdQrManualInput)
//   - <script src="js/jsQR.min.js">
//   - Hàm applyCccdQr(text): parse bằng parseCccdQr(), điền form, trả về true nếu hợp lệ
//   - Gọi loadAddressConversionData(url chuyen_doi.json) để đổi địa chỉ cũ → mới

let addressConversionData = {};

function loadAddressConversionData(url) {
    fetch(url)
        .then(response => response.json())
        .then(data => { addressConversionData = data; addrConvIndex = null; })
        .catch(error => console.error('Error loading address conversion data:', error));
}

let cccdQrStream = null;
let cccdQrTimer = null;
let cccdQrModalOpen = false;
const cccdQrCanvas = document.createElement('canvas');

// Ngày hết hạn theo Luật Căn cước: đổi thẻ khi đủ 14, 25, 40, 60 tuổi;
// thẻ cấp trong vòng 2 năm trước mốc tuổi thì có giá trị đến mốc tiếp theo; từ 58 tuổi trở đi không thời hạn.
function tinhNgayHetHanCccd(ngaySinh, ngayCap) {
    if (!ngaySinh || !ngayCap) return '';
    const namSinh = parseInt(ngaySinh.slice(0, 4), 10);
    const thangNgay = ngaySinh.slice(4); // "-mm-dd"
    for (const tuoi of [14, 25, 40, 60]) {
        if (ngayCap < `${namSinh + tuoi - 2}${thangNgay}`) return `${namSinh + tuoi}${thangNgay}`;
    }
    return '';
}

// ---- Đổi địa chỉ cũ trên CCCD sang địa chỉ mới (dữ liệu chuyen_doi.json) ----
// Địa chỉ trên QR thường không có tiền tố: "Ấp Béc Hen Nhỏ, Long Thạnh, Vĩnh Lợi, Bạc Liêu"
// → so khớp bỏ dấu, bỏ tiền tố (Ấp/Xã/Huyện/Tỉnh...), thử có huyện trước rồi bỏ huyện (từ 7/2025 không còn cấp huyện).
let addrConvIndex = null;

function normAddrPart(s) {
    return s.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[đĐ]/g, 'd').toLowerCase()
        .replace(/^(ap|khom|xa|phuong|thi tran|huyen|quan|thi xa|thanh pho|tinh|tp\.?)\s+/, '')
        .replace(/\b0+(\d)/g, '$1').replace(/\s+/g, ' ').trim();
}

// Bỏ "(mới)" và cấp huyện trong địa chỉ mới
function cleanNewAddr(addr) {
    const parts = addr.replace(/\s*\(mới\)\s*$/, '').split(',').map(s => s.trim()).filter(Boolean);
    return parts.filter((p, i) => i === parts.length - 1 || !/^(Huyện|Quận|Thị xã|Thành phố) /.test(p));
}

function buildAddrConvIndex() {
    const hamlet = new Map(), ward = new Map();
    const add = (map, key, val) => { if (!map.has(key)) map.set(key, new Set()); map.get(key).add(val); };
    for (const [oldAddr, newAddr] of Object.entries(addressConversionData)) {
        const o = oldAddr.split(',').map(s => s.trim());
        const n = cleanNewAddr(newAddr);
        if (o.length === 4 && o[0]) {
            const [h, w, d, p] = o.map(normAddrPart);
            add(hamlet, `${h}|${w}|${d}|${p}`, n.join(', '));
            add(hamlet, `${h}|${w}|${p}`, n.join(', '));
            add(ward, `${w}|${d}|${p}`, n.slice(1).join(', '));
            add(ward, `${w}|${p}`, n.slice(1).join(', '));
        } else if (o.length >= 3) {
            const [w, d, p] = o.slice(-3).map(normAddrPart);
            add(ward, `${w}|${d}|${p}`, n.join(', '));
            add(ward, `${w}|${p}`, n.join(', '));
        }
    }
    return { hamlet, ward };
}

// Trả về địa chỉ mới, hoặc null nếu không có trong dữ liệu chuyển đổi
function convertToNewAddress(addr) {
    if (!addrConvIndex && Object.keys(addressConversionData).length) addrConvIndex = buildAddrConvIndex();
    if (!addrConvIndex || !addr) return null;

    const parts = addr.split(',').map(s => s.trim()).filter(Boolean);
    if (parts.length < 3) return null;
    // Chỉ dùng kết quả khi duy nhất (tránh trùng tên như "Phường 1" ở nhiều huyện)
    const get = (map, key) => { const s = map.get(key); return s && s.size === 1 ? [...s][0] : null; };
    const [p, d, w] = [parts[parts.length - 1], parts[parts.length - 2], parts[parts.length - 3]].map(normAddrPart);

    if (parts.length >= 4) {
        const h = normAddrPart(parts[parts.length - 4]);
        const full = get(addrConvIndex.hamlet, `${h}|${w}|${d}|${p}`) || get(addrConvIndex.hamlet, `${h}|${w}|${p}`);
        if (full) return [...parts.slice(0, -4), full].join(', ');
    }
    // Không có ấp/khóm trong dữ liệu → giữ ấp/số nhà như trên thẻ, đổi xã/tỉnh
    const newWard = get(addrConvIndex.ward, `${w}|${d}|${p}`) || get(addrConvIndex.ward, `${w}|${p}`);
    if (newWard) return [...parts.slice(0, -3), newWard].join(', ');
    return null;
}

function parseCccdQr(text) {
    const p = (text || '').trim().split('|').map(s => s.trim());
    if (p.length < 7 || !/^\d{12}$/.test(p[0])) return null;

    const toIsoDate = s => /^\d{8}$/.test(s) ? `${s.slice(4, 8)}-${s.slice(2, 4)}-${s.slice(0, 2)}` : '';
    const ngaySinh = toIsoDate(p[3]);
    const ngayCap = toIsoDate(p[6]);
    const diaChiMoi = convertToNewAddress(p[5]);

    return {
        so_cmnd: p[0],
        cmnd_cu: p[1],
        ho_ten: p[2],
        ngay_sinh: ngaySinh,
        gioi_tinh: p[4].toLowerCase() === 'nam' ? 'Nam' : 'Nữ',
        dia_chi: diaChiMoi || p[5],
        dia_chi_tren_the: p[5],
        da_doi_dia_chi: !!diaChiMoi,
        ngay_cap_cmnd: ngayCap,
        ngay_het_han_cmnd: tinhNgayHetHanCccd(ngaySinh, ngayCap),
        // Căn cước mẫu mới (từ 01/07/2024) do Bộ Công an cấp
        noi_cap_cmnd: ngayCap >= '2024-07-01' ? 'Bộ Công An' : 'Cục CSQLHC về TTXH',
    };
}

function setCccdQrStatus(html, cls = 'text-muted') {
    const el = document.getElementById('cccdQrStatus');
    el.className = `small mt-2 ${cls}`;
    el.innerHTML = html;
}

function beepCccdQr() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        osc.frequency.value = 1000;
        osc.connect(ctx.destination);
        osc.onended = () => ctx.close();
        osc.start();
        osc.stop(ctx.currentTime + 0.15);
    } catch (e) {}
}

function cccdBrowser() {
    const ua = navigator.userAgent;
    return /Firefox\//.test(ua) ? 'firefox' : /Edg\//.test(ua) ? 'edge' : 'chrome';
}

function cameraWaitHtml() {
    return '<i class="bi bi-hourglass-split"></i> Đang mở camera... Nếu trình duyệt hỏi quyền dùng camera, '
        + (cccdBrowser() === 'firefox' ? 'chọn đúng webcam (vd. FaceX1000, <u>không</u> chọn CyberLink Webcam Splitter) ở ô danh sách trong khung hỏi rồi bấm <strong>Allow</strong>.' : 'bấm <strong>Cho phép (Allow)</strong>.');
}

// Hướng dẫn xử lý lỗi camera cho GDV, theo từng trình duyệt (Chrome / Edge / Firefox)
// kind: insecure (mở bằng http://IP) | denied (bị từ chối quyền) | notfound (không có camera) | busy (camera đang bận)
function renderCameraHelp(containerId, kind, retryJs, detail) {
    const browser = cccdBrowser();
    const name = { chrome: 'Chrome', edge: 'Edge', firefox: 'Firefox' }[browser];
    const copyBtn = (text, label) =>
        `<button type="button" class="btn btn-sm btn-primary" onclick="copyCccdQrText('${text}', this)"><i class="bi bi-clipboard"></i> ${label}</button>`;
    const keys = (...k) => k.map(x => `<kbd>${x}</kbd>`).join('+');
    const pickReal = 'Ở ô <strong>Camera</strong> phía trên, chọn <strong>webcam thật</strong> (vd. FaceX1000). <u>Không</u> chọn <strong>CyberLink Webcam Splitter</strong> hoặc dòng có chữ "(camera ảo)"';
    const cyberlink = 'Máy có cài <strong>CyberLink YouCam</strong> (sinh ra "CyberLink Webcam Splitter"): tắt YouCam ở khay đồng hồ, hoặc gỡ trong <strong>Settings → Apps → CyberLink YouCam → Uninstall</strong>, rồi khởi động lại máy';
    const useEdge = browser === 'firefox'
        ? `Firefox trên một số máy không nhận được webcam → mở trang này bằng <strong>Microsoft Edge</strong>: bấm ${copyBtn(location.href, 'Sao chép địa chỉ')} → mở Edge → ${keys('Ctrl', 'V')} → ${keys('Enter')}`
        : null;
    const winPrivacy = `Vẫn không được: mở <strong>Settings (Cài đặt) của Windows → Privacy &amp; security → Camera</strong> → bật
        <strong>Camera access</strong> và <strong>Let desktop apps access your camera</strong>`;
    let title, steps;

    if (kind === 'insecure') {
        title = `${name} đang chặn camera vì trang mở bằng địa chỉ <code>${location.host}</code>. Bật cho máy này (chỉ làm 1 lần):`;
        steps = browser === 'firefox' ? [
            `Bấm ${copyBtn('about:config', 'Sao chép 1')} → ${keys('Ctrl', 'T')} (mở tab mới) → ${keys('Ctrl', 'V')} → ${keys('Enter')} → bấm nút <strong>Accept the Risk and Continue</strong>`,
            `Bấm ${copyBtn('media.devices.insecure.enabled', 'Sao chép 2')} → bấm vào ô tìm kiếm trên cùng → ${keys('Ctrl', 'V')} → bấm <strong>đúp chuột</strong> vào dòng hiện ra để chữ <strong>false</strong> đổi thành <strong>true</strong>`,
            `Bấm ${copyBtn('media.getusermedia.insecure.enabled', 'Sao chép 3')} → xóa chữ trong ô tìm kiếm → ${keys('Ctrl', 'V')} → bấm <strong>đúp chuột</strong> để đổi thành <strong>true</strong>`,
            `Tắt hẳn Firefox rồi mở lại trang này → khi Firefox hỏi quyền camera, bấm <strong>Allow</strong> (Firefox có thể hỏi lại mỗi lần mở camera)`,
        ] : [
            `Bấm ${copyBtn(`${browser}://flags/#unsafely-treat-insecure-origin-as-secure`, 'Sao chép 1')} → ${keys('Ctrl', 'T')} (mở tab mới) → ${keys('Ctrl', 'V')} → ${keys('Enter')}`,
            `Bấm ${copyBtn(location.origin, 'Sao chép 2')} → trong tab mới, bấm vào <strong>ô trống</strong> của dòng được tô vàng → ${keys('Ctrl', 'V')}`,
            `Bên phải dòng đó: đổi <strong>Disabled</strong> thành <strong>Enabled</strong>`,
            `Bấm nút <strong>${browser === 'edge' ? 'Restart' : 'Relaunch'}</strong> ở góc dưới bên phải → ${name} tự mở lại → khi được hỏi quyền camera, bấm <strong>Cho phép (Allow)</strong>`,
        ];
    } else if (kind === 'denied') {
        title = 'Quyền dùng camera đang bị từ chối. Cho phép lại như sau:';
        steps = browser === 'firefox' ? [
            'Bấm vào <strong>biểu tượng camera bị gạch chéo</strong> ở đầu thanh địa chỉ',
            'Bấm dấu <strong>✕</strong> cạnh dòng <strong>Blocked Temporarily / Blocked</strong> (Đã chặn) để bỏ chặn',
            `Bấm ${keys('F5')} để tải lại trang → mở lại cửa sổ này → khi Firefox hỏi, bấm <strong>Allow</strong>`,
            winPrivacy,
        ] : [
            'Bấm vào <strong>biểu tượng camera có dấu ✕ đỏ</strong> ở cuối thanh địa chỉ (hoặc chữ <strong>Không bảo mật / Not secure</strong> ở đầu thanh địa chỉ)',
            `Ở mục <strong>Camera</strong>, chọn <strong>${browser === 'edge' ? 'Allow (Cho phép)' : 'Luôn cho phép / Always allow'}</strong> → bấm <strong>Xong / Done</strong>`,
            `Bấm ${keys('F5')} để tải lại trang → mở lại cửa sổ này`,
            winPrivacy,
        ];
    } else if (kind === 'notfound') {
        title = 'Không tìm thấy webcam nào trên máy này:';
        steps = [
            pickReal,
            'Kiểm tra dây USB của webcam đã cắm chặt. Rút webcam ra, đợi 5 giây, cắm vào <strong>cổng USB khác</strong> (ưu tiên cổng phía sau thùng máy) → bấm <strong>Thử lại</strong>',
            cyberlink,
            useEdge,
            winPrivacy,
        ];
    } else {
        title = 'Không mở được camera — thường do camera đang bị chương trình khác sử dụng:';
        steps = [
            pickReal,
            'Tắt các chương trình đang gọi video: <strong>Zalo, Teams, Zoom, Skype</strong>…',
            `Đóng các tab/cửa sổ trình duyệt khác đang mở camera (kể cả cửa sổ Quét QR / Chụp 2 mặt ở tab khác) → bấm <strong>Thử lại</strong>. Vẫn lỗi: rút webcam ra cắm lại`,
            cyberlink,
            useEdge,
            winPrivacy,
        ];
    }

    document.getElementById(containerId).innerHTML = `
        <div class="alert alert-warning mt-2 mb-0" style="font-size:16px;">
            <div class="fw-bold mb-2"><i class="bi bi-camera-video-off"></i> ${title}</div>
            <ol class="mb-2 ps-3">${steps.filter(Boolean).map(x => `<li class="mb-2">${x}</li>`).join('')}</ol>
            ${kind === 'insecure' ? '' : `<button type="button" class="btn btn-warning" onclick="${retryJs}"><i class="bi bi-arrow-clockwise"></i> Thử lại</button>`}
            ${detail ? `<div class="small text-muted mt-2">Thông tin kỹ thuật (chụp màn hình gửi IT nếu vẫn lỗi): <code>${detail.replace(/[&<>"']/g, c => `&#${c.charCodeAt(0)};`)}</code></div>` : ''}
        </div>`;
}

// navigator.clipboard không dùng được trên http://IP → dùng execCommand('copy')
function copyCccdQrText(text, btn) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    btn.closest('.modal').appendChild(ta); // trong modal để không bị focus-trap của Bootstrap chặn
    ta.select();
    document.execCommand('copy');
    ta.remove();

    const old = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-check-lg"></i> Đã sao chép';
    btn.classList.replace('btn-primary', 'btn-success');
    setTimeout(() => { btn.innerHTML = old; btn.classList.replace('btn-success', 'btn-primary'); }, 2000);
}

function stopCccdQrScan() {
    clearInterval(cccdQrTimer);
    cccdQrTimer = null;
    if (cccdQrStream) {
        cccdQrStream.getTracks().forEach(t => t.stop());
        cccdQrStream = null;
    }
}

// Camera ảo (CyberLink YouCam "Webcam Splitter", OBS, ManyCam...) hay chiếm camera thật hoặc cho hình kém → tự tránh
const VIRTUAL_CAMERA_RE = /splitter|virtual|youcam|cyberlink|manycam|\bobs\b|xsplit|snap camera/i;

async function listCameras() {
    try {
        return (await navigator.mediaDevices.enumerateDevices()).filter(d => d.kind === 'videoinput');
    } catch (e) {
        return [];
    }
}

function fillCameraSelect(selectId, cameras, activeId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '';
    cameras.forEach((cam, i) => {
        const label = (cam.label || `Camera ${i + 1}`) + (VIRTUAL_CAMERA_RE.test(cam.label) ? ' (camera ảo)' : '');
        const opt = new Option(label, cam.deviceId);
        opt.selected = cam.deviceId === activeId;
        select.appendChild(opt);
    });
}

// Mở camera vào thẻ <video> và nạp danh sách camera vào <select> (dùng chung cho Quét QR và Chụp 2 mặt).
// manual = GĐV tự chọn ở ô Camera → dùng đúng camera đó, không tự đổi.
// autoPick = lần thử do hệ thống tự chọn camera → không thử tiếp / không tự đổi nữa (tránh vòng lặp).
// Lỗi → ném Error('insecure'|'denied'|'notfound'|'busy'), kèm error.detail (tên lỗi + danh sách camera) để gửi IT.
async function openCameraInto(videoId, selectId, deviceId, width, height, manual = false, autoPick = false) {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) throw new Error('insecure');
    const isDenied = e => e.name === 'NotAllowedError' || e.name === 'SecurityError';
    const byId = deviceId ? { deviceId: { exact: deviceId } } : {};
    let stream;
    try {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: Object.assign({ width: { ideal: width }, height: { ideal: height } }, byId)
            });
        } catch (error) {
            if (isDenied(error)) throw error;
            // Một số webcam/driver (hay gặp trên Firefox) lỗi khi yêu cầu độ phân giải → thử lại không ràng buộc
            stream = await navigator.mediaDevices.getUserMedia({ video: deviceId ? byId : true });
            // Mở không ràng buộc thường chỉ được 640x480 → thử nâng độ phân giải lại (lỗi thì giữ nguyên)
            try {
                await stream.getVideoTracks()[0].applyConstraints({ width: { ideal: width }, height: { ideal: height } });
            } catch (e) {}
        }
    } catch (error) {
        if (!isDenied(error) && !manual && !autoPick) {
            // Camera đã nhớ không mở được (đã rút ra / đổi ID / đang bận) → thử camera mặc định
            if (deviceId) return openCameraInto(videoId, selectId, null, width, height);
            // Camera mặc định không mở được (vd. camera ảo lỗi trên Firefox) → thử lần lượt các camera khác, camera thật trước
            const others = (await listCameras()).filter(c => c.deviceId)
                .sort((a, b) => VIRTUAL_CAMERA_RE.test(a.label) - VIRTUAL_CAMERA_RE.test(b.label));
            for (const cam of others) {
                try {
                    return await openCameraInto(videoId, selectId, cam.deviceId, width, height, false, true);
                } catch (e) {}
            }
        }
        // Vẫn hiện danh sách camera để GĐV chọn camera khác (vd. camera thật thay vì camera ảo)
        const cameras = await listCameras();
        if (cameras.some(c => c.deviceId)) fillCameraSelect(selectId, cameras, deviceId);
        const err = new Error(isDenied(error) ? 'denied' : error.name === 'NotFoundError' ? 'notfound' : 'busy');
        err.detail = `${error.name}: ${error.message} | Camera trên máy: ${cameras.map(c => c.label || '(chưa có tên)').join(', ') || 'không có'}`;
        throw err;
    }

    const track = stream.getVideoTracks()[0];
    const activeId = track.getSettings().deviceId;
    const cameras = await listCameras();
    const activeIsVirtual = VIRTUAL_CAMERA_RE.test((cameras.find(c => c.deviceId === activeId) || {}).label || '');

    // Đang dùng camera ảo mà máy có camera thật → tự chuyển sang camera thật (không được thì quay lại camera ảo)
    if (activeIsVirtual && !manual && !autoPick) {
        const real = cameras.find(c => c.deviceId && !VIRTUAL_CAMERA_RE.test(c.label));
        if (real) {
            stream.getTracks().forEach(t => t.stop());
            try {
                return await openCameraInto(videoId, selectId, real.deviceId, width, height, false, true);
            } catch (e) {
                return openCameraInto(videoId, selectId, activeId, width, height, false, true);
            }
        }
    }

    // Chỉ nhớ camera thật hoặc camera GĐV tự chọn (không nhớ nhầm camera ảo)
    if (manual || !activeIsVirtual) {
        try { localStorage.setItem('cccdQrCameraId', activeId); } catch (e) {}
    }

    // Bật tự động lấy nét liên tục nếu webcam hỗ trợ (Chrome/Edge)
    try {
        const caps = track.getCapabilities ? track.getCapabilities() : {};
        if (caps.focusMode && caps.focusMode.includes('continuous')) {
            await track.applyConstraints({ advanced: [{ focusMode: 'continuous' }] });
        }
    } catch (e) {}

    const video = document.getElementById(videoId);
    video.srcObject = stream;
    await video.play();
    fillCameraSelect(selectId, cameras, activeId);
    return stream;
}

function savedCameraId() {
    try { return localStorage.getItem('cccdQrCameraId'); } catch (e) { return null; }
}

async function startCccdQrScan(deviceId, manual = false) {
    stopCccdQrScan();
    document.getElementById('cccdQrHelp').innerHTML = '';
    setCccdQrStatus(cameraWaitHtml());
    let stream;
    try {
        stream = await openCameraInto('cccdQrVideo', 'cccdQrCameraSelect', deviceId, 1280, 720, manual);
    } catch (error) {
        setCccdQrStatus('<i class="bi bi-x-circle"></i> Chưa dùng được camera — làm theo hướng dẫn bên dưới, hoặc dùng ô dán chuỗi QR.', 'text-danger');
        renderCameraHelp('cccdQrHelp', error.message, 'startCccdQrScan(savedCameraId())', error.detail);
        return;
    }

    // Modal đã đóng trong lúc chờ quyền camera
    if (!cccdQrModalOpen) {
        stream.getTracks().forEach(t => t.stop());
        return;
    }
    cccdQrStream = stream;

    setCccdQrStatus('<i class="bi bi-qr-code-scan"></i> Đang quét... Đưa mã QR mặt trước thẻ vào giữa khung hình, giữ yên 1-2 giây.', 'text-success');
    cccdQrTimer = setInterval(scanCccdQrFrame, 250);
}

function scanCccdQrFrame() {
    const video = document.getElementById('cccdQrVideo');
    if (!cccdQrStream || video.readyState < video.HAVE_ENOUGH_DATA) return;

    cccdQrCanvas.width = video.videoWidth;
    cccdQrCanvas.height = video.videoHeight;
    const ctx = cccdQrCanvas.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(video, 0, 0);
    const image = ctx.getImageData(0, 0, cccdQrCanvas.width, cccdQrCanvas.height);
    const code = jsQR(image.data, image.width, image.height, { inversionAttempts: 'dontInvert' });
    if (code && code.data) applyCccdQr(code.data);
}

document.getElementById('cccdQrModal').addEventListener('shown.bs.modal', () => {
    cccdQrModalOpen = true;
    document.getElementById('cccdQrSuccess').classList.replace('d-flex', 'd-none');
    startCccdQrScan(savedCameraId());
});
document.getElementById('cccdQrModal').addEventListener('hidden.bs.modal', () => {
    cccdQrModalOpen = false;
    stopCccdQrScan();
});
