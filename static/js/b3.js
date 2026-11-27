// Giao diện B3: tra cứu, lọc và phiếu nhập/xuất; gọi API Flask b3.py, b4.py.
let b3Catalog = [];
let b3LookupRequest = 0;
let b3Submitting = false;

async function b3Fetch(url, options) {
    const res = await apiFetch(url, options);
    let data;
    try { data = await res.json(); }
    catch { throw new Error(`Máy chủ trả về dữ liệu không hợp lệ (${res.status}).`); }
    if (!res.ok) throw new Error(data?.error || `Yêu cầu thất bại (${res.status}).`);
    return data;
}

const voucherDrafts = {nhap: [], xuat: []};
const voucherMoneyLimit = 9999999999999.99;
const v = id => document.getElementById(id);
const voucherMode = () => v('phieu-loai').value;
const fmt = value => Number(value).toLocaleString('vi-VN', {maximumFractionDigits: 2});
const money = value => fmt(value) + ' đ';
function filterStockRows(items, stock, sort) {
    const rows = items.filter(item => stock === 'low' ? Number(item.so_luong_ton) < 10 : stock === 'available' ? Number(item.so_luong_ton) > 0 : true);
    if (sort === 'ton-desc' || sort === 'ton-asc') rows.sort((a,b) => (Number(a.so_luong_ton)-Number(b.so_luong_ton)) * (sort === 'ton-desc' ? -1 : 1));
    return rows;
}
function voucherError(message = '') {
    v('voucher-error').textContent = message;
    v('voucher-error').hidden = !message;
}
function clearVoucherEntry() {
    ['phieu-sach','phieu-sl','phieu-gia'].forEach(id => v(id).value = '');
    voucherError();
    updateB3StockPreview();
}
function resetVoucherDraft(force = false) {
    if (b3Submitting && !force) return;
    const mode = voucherMode();
    if (!force && !confirm('Xóa toàn bộ nội dung nháp của phiếu này?')) return;
    voucherDrafts[mode] = [];
    (mode === 'nhap' ? ['pn-ma','pn-ncc'] : ['px-ma','px-nguoinhan','px-lydo']).forEach(id => v(id).value = '');
    clearVoucherEntry(); renderVoucherDraft();
}
function resetVoucherSession() {
    voucherDrafts.nhap = []; voucherDrafts.xuat = []; b3Catalog = [];
    ['pn-ma','pn-ncc','px-ma','px-nguoinhan','px-lydo','voucher-creator','voucher-date'].forEach(id => v(id).value = '');
    clearVoucherEntry(); renderVoucherDraft();
}
function currentVoucherLine() {
    const book = b3Catalog.find(s => s.ma_sach === v('phieu-sach').value);
    const quantity = Number(v('phieu-sl').value);
    const priceRaw = v('phieu-gia').value.trim();
    return {book, quantity, priceRaw, price: Number(priceRaw)};
}
function validateVoucherLines(mode, lines) {
    let total = 0; const quantities = new Map();
    for (const line of lines) {
        if (!Number.isSafeInteger(line.quantity) || line.quantity <= 0) return 'Số lượng phải là số nguyên dương hợp lệ.';
        const book = b3Catalog.find(b => b.ma_sach === line.code);
        if (!book) return `Không tìm thấy sách ${line.code}. Hãy tải lại danh sách.`;
        const quantity = (quantities.get(line.code) || 0) + line.quantity;
        if (!Number.isSafeInteger(quantity)) return 'Tổng số lượng vượt giới hạn.';
        quantities.set(line.code, quantity);
        if (mode === 'xuat' && quantity > Number(book.so_luong_ton)) return `Sách ${book.ten_sach}: còn ${fmt(book.so_luong_ton)} cuốn, tổng yêu cầu ${fmt(quantity)} cuốn.`;
        if (mode === 'nhap') {
            if (!Number.isFinite(line.price) || line.price < 0 || line.price > voucherMoneyLimit) return 'Đơn giá nhập không hợp lệ.';
            total += line.quantity * line.price;
            if (!Number.isFinite(total) || total > voucherMoneyLimit) return 'Tổng tiền nhập vượt giới hạn cho phép.';
        }
    }
    return '';
}
function updateB3StockPreview() {
    const mode = voucherMode();
    const {book,quantity,priceRaw,price} = currentVoucherLine();
    const raw = v('phieu-sl').value;
    const validQty = raw !== '' && Number.isSafeInteger(quantity) && quantity > 0;
    const pending = book ? voucherDrafts[mode].filter(l => l.code === book.ma_sach).reduce((sum,l) => sum+l.quantity,0) : 0;
    const stock = book ? Number(book.so_luong_ton) : null;
    const future = book ? stock + (mode === 'nhap' ? 1 : -1) * (pending + (validQty ? quantity : 0)) : null;
    v('voucher-book-name').textContent = book?.ten_sach || 'Chọn một đầu sách';
    v('voucher-book-meta').textContent = book ? [book.ma_sach, book.tac_gia, book.vi_tri].filter(Boolean).join(' · ') : 'Mã sách · Vị trí kệ';
    v('b3-stock-current').textContent = stock === null ? '—' : fmt(stock);
    v('b3-stock-after').textContent = future === null ? '—' : fmt(future);
    v('b3-stock-action').textContent = mode === 'nhap' ? 'Tồn dự kiến sau nhập' : 'Tồn dự kiến sau xuất';
    let error = raw !== '' && !validQty ? 'Số lượng phải là số nguyên dương.' : '';
    if (!error && book && mode === 'xuat' && future < 0) error = `Không đủ tồn kho: còn ${fmt(stock)}, tổng yêu cầu ${fmt(pending + (validQty ? quantity : 0))}.`;
    if (!error && mode === 'nhap' && priceRaw && (!Number.isFinite(price) || price < 0 || price > voucherMoneyLimit)) error = 'Đơn giá nhập không hợp lệ.';
    v('b3-stock-warning').textContent = error; v('b3-stock-warning').hidden = !error;
    const showTotal = mode === 'nhap' && validQty && priceRaw !== '' && Number.isFinite(price) && price >= 0 && price * quantity <= voucherMoneyLimit;
    v('b3-import-total').hidden = !showTotal;
    v('b3-import-total').textContent = showTotal ? 'Thành tiền dòng này: ' + money(price*quantity) : '';
    v('voucher-add-line').disabled = b3Submitting || !book || !validQty || !!error || (mode === 'nhap' && !showTotal);
}
function renderVoucherDraft() {
    const mode = voucherMode(), lines = voucherDrafts[mode], body = v('voucher-lines');
    body.replaceChildren();
    if (!lines.length) {
        const cell = body.insertRow().insertCell(); cell.colSpan = mode === 'nhap' ? 5 : 3; cell.className = 'voucher-empty'; cell.textContent = 'Chưa có sách. Thêm sách ở bước 02.';
    }
    for (const [i,line] of lines.entries()) {
        const row = body.insertRow();
        const cell = row.insertCell(); const title = document.createElement('strong'); title.textContent = line.name;
        const code = document.createElement('small'); code.textContent = line.code; cell.append(title,code);
        row.insertCell().textContent = fmt(line.quantity);
        if (mode === 'nhap') { row.insertCell().textContent = money(line.price); row.insertCell().textContent = money(line.price*line.quantity); }
        const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'voucher-remove'; remove.textContent = 'Xóa'; remove.setAttribute('aria-label','Xóa '+line.name);
        remove.onclick = () => { if (b3Submitting) return; lines.splice(i,1); voucherError(); renderVoucherDraft(); updateB3StockPreview(); };
        row.insertCell().append(remove);
    }
    v('voucher-line-count').textContent = fmt(new Set(lines.map(l=>l.code)).size);
    v('voucher-quantity').textContent = fmt(lines.reduce((sum,l)=>sum+l.quantity,0));
    v('voucher-total-wrap').hidden = mode !== 'nhap';
    v('voucher-total').textContent = money(lines.reduce((sum,l)=>sum+l.quantity*l.price,0));
    document.querySelector('.drawer-submit').disabled = b3Submitting || !lines.length;
}
function addVoucherLine() {
    if (b3Submitting) return;
    const mode = voucherMode(), {book,quantity,priceRaw,price} = currentVoucherLine();
    if (!book || !Number.isSafeInteger(quantity) || quantity <= 0 || (mode === 'nhap' && !priceRaw)) { voucherError('Chọn sách và nhập đủ số lượng, đơn giá (nếu nhập kho).'); return; }
    const line = {code:book.ma_sach,name:book.ten_sach,quantity,price:mode === 'nhap' ? price : 0};
    const error = validateVoucherLines(mode,[...voucherDrafts[mode],line]);
    if (error) { voucherError(error); return; }
    voucherDrafts[mode].push(line); clearVoucherEntry(); renderVoucherDraft(); v('phieu-sach').focus();
}

async function loadSachNhanVien() {
    const currentRequest = ++b3LookupRequest;
    const params = new URLSearchParams({
        q: document.getElementById('search-keyword').value,
        ncc: document.getElementById('filter-ncc').value,
        sort: ['ten','gia'].includes(v('sort-select').value) ? v('sort-select').value : ''
    });
    const minPrice = document.getElementById('filter-min-price').value.trim();
    const maxPrice = document.getElementById('filter-max-price').value.trim();
    if (minPrice) params.set('min_price', minPrice);
    if (maxPrice) params.set('max_price', maxPrice);

    const tbody = document.querySelector('#table-nv-sach tbody');
    const showMessage = message => {
        tbody.replaceChildren();
        const cell = tbody.insertRow().insertCell();
        cell.colSpan = 7;
        cell.textContent = message;
    };
    try {
        const result = await b3Fetch('/api/sach?' + params.toString());
        if (currentRequest !== b3LookupRequest) return;
        if (!Array.isArray(result)) throw new Error('Danh sách sách không hợp lệ.');
        const data = filterStockRows(result, v('filter-stock').value, v('sort-select').value);
        v('staff-result-count').textContent = data.length + ' đầu sách';
        tbody.replaceChildren();
        if (!data.length) { showMessage('Không tìm thấy sách phù hợp.'); return; }
        for (const sach of data) {
            const row = tbody.insertRow();
            const values = [
                sach.ma_sach, sach.ten_sach, sach.the_loai, sach.tac_gia,
                (sach.gia_ban ?? 0).toLocaleString('vi-VN') + ' đ',
                sach.so_luong_ton, sach.vi_tri || ''
            ];
            for (const value of values) row.insertCell().textContent = value ?? '';
            const stockCell = row.cells[5];
            if (Number(sach.so_luong_ton) < 10) {
                const badge = document.createElement('small');
                badge.className = 'stock-warning-label';
                badge.textContent = Number(sach.so_luong_ton) === 0 ? 'Hết hàng' : 'Sắp hết';
                stockCell.append(badge);
            }
        }
    } catch (error) {
        if (currentRequest === b3LookupRequest) { v('staff-result-count').textContent = ''; showMessage(error.message || 'Không thể tải danh sách sách.'); }
    }
}



async function loadSachSelect() {
    const select = document.getElementById('phieu-sach');
    const selectedMaSach = select.value;
    try {
        const data = await b3Fetch('/api/sach');
        if (!Array.isArray(data)) throw new Error('Danh sách sách không hợp lệ.');
        b3Catalog = data;
        select.replaceChildren(new Option('-- Chọn sách --', ''));
        for (const book of data) {
            select.add(new Option(`${book.ma_sach} · ${book.ten_sach} (Tồn: ${book.so_luong_ton})`, book.ma_sach));
        }
        if (Array.from(select.options).some(option => option.value === selectedMaSach)) select.value = selectedMaSach;
    } catch (error) {
        b3Catalog = [];
        select.replaceChildren(new Option('Không tải được danh sách sách', ''));
        alert(error.message || 'Không thể tải sách.');
    }
    updateB3StockPreview();
}

function togglePhieuForm() {
    const loai = document.getElementById('phieu-loai').value;
    if(loai === 'nhap') {
        document.getElementById('nhap-fields').style.display = 'grid';
        document.getElementById('xuat-fields').style.display = 'none';
        document.getElementById('phieu-gia-wrapper').style.display = 'block';
    } else {
        document.getElementById('nhap-fields').style.display = 'none';
        document.getElementById('xuat-fields').style.display = 'grid';
        document.getElementById('phieu-gia-wrapper').style.display = 'none';
    }
    updateB3StockPreview();
}

function todayLocalISO() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

async function submitPhieu() {
    if (b3Submitting || v('main-app').dataset.role !== 'staff') return;
    const mode = voucherMode(), lines = voucherDrafts[mode];
    if (v('phieu-sl').value || (mode === 'nhap' && v('phieu-gia').value)) { voucherError('Bạn còn một dòng chưa thêm. Hãy thêm vào phiếu hoặc xóa số lượng/đơn giá trước khi lưu.'); return; }
    if (!lines.length) { voucherError('Phiếu cần ít nhất một dòng sách.'); return; }
    const invalid = validateVoucherLines(mode,lines);
    if (invalid) { voucherError(invalid); return; }
    const code = v(mode === 'nhap' ? 'pn-ma' : 'px-ma').value.trim();
    if (!code || code.length > 20) { voucherError('Nhập mã phiếu từ 1 đến 20 ký tự.'); return; }
    const date = todayLocalISO();
    const creator = v('main-app').dataset.username || v('voucher-creator').value;
    let payload, receipt, url;
    if (mode === 'nhap') {
        const supplier = v('pn-ncc').value;
        if (!supplier) { voucherError('Chọn nhà cung cấp.'); return; }
        url = '/api/phieu-nhap';
        payload = {ma_phieu_nhap:code, ngay_nhap:date, ma_ncc:supplier, chi_tiet:lines.map(l=>({ma_sach:l.code,so_luong_nhap:l.quantity,don_gia_nhap:l.price}))};
        receipt = {...payload, nguoi_lap:creator, ten_ncc:v('pn-ncc').selectedOptions[0]?.textContent, tong_tien:lines.reduce((sum,l)=>sum+l.quantity*l.price,0), chi_tiet:payload.chi_tiet.map((l,i)=>({...l,ten_sach:lines[i].name,thanh_tien:l.so_luong_nhap*l.don_gia_nhap}))};
    } else {
        const receiver = v('px-nguoinhan').value.trim(), reason = v('px-lydo').value.trim();
        if (receiver.length > 100 || reason.length > 200) { voucherError('Người nhận tối đa 100 ký tự, lý do tối đa 200 ký tự.'); return; }
        url = '/api/phieu-xuat';
        payload = {ma_phieu_xuat:code, ngay_xuat:date, nguoi_nhan:receiver, ly_do:reason, chi_tiet:lines.map(l=>({ma_sach:l.code,so_luong_xuat:l.quantity}))};
        receipt = {...payload,nguoi_lap:creator,chi_tiet:payload.chi_tiet.map((l,i)=>({...l,ten_sach:lines[i].name}))};
    }
    b3Submitting = true; voucherError();
    const controls = [...document.querySelectorAll('.voucher-card input,.voucher-card select,.voucher-card textarea,.voucher-card button')];
    const previous = controls.map(el=>el.disabled); controls.forEach(el=>el.disabled=true);
    const button = document.querySelector('.drawer-submit'); button.textContent = 'Đang lưu…';
    let saved = false;
    try {
        await b3Fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
        saved = true;
        resetVoucherDraft(true);
        window.warehouseTheme.closeDrawer(true);
        renderWarehouseReceipt(mode,receipt,true);
        await Promise.allSettled([loadSachNhanVien(),loadSachSelect(),window.warehouseTheme.refreshMetrics()]);
        if (v('tab-export-history').classList.contains('active')) await loadExportHistory();
        if (v('tab-import-history').classList.contains('active')) await loadThongKe();
    } catch (error) {
        if (!saved) { voucherError(error.message || 'Không thể lưu phiếu.'); await loadSachSelect(); }
        else console.warn('Phiếu đã lưu, không cập nhật được giao diện:',error);
    } finally {
        b3Submitting = false;
        controls.forEach((el,i)=>el.disabled=previous[i]);
        button.textContent = mode === 'nhap' ? 'Lưu phiếu nhập' : 'Lưu phiếu xuất';
        renderVoucherDraft(); updateB3StockPreview();
    }
}

// --- Điều hướng Sub-tabs cho Nhân viên kho ---
function switchStaffSubTab(subId) {
    if (document.getElementById('main-app').dataset.role !== 'staff') return;
    if (subId === 'lap-phieu') {
        window.warehouseTheme.openDrawer('nhap');
        return;
    }
    switchTab('nhan-vien');
    window.warehouseTheme.closeDrawer();
    window.warehouseTheme.setNav('side-staff-lookup');
    document.getElementById('page-title').textContent = 'Tra cứu kho hàng';
    loadSachNhanVien();
}

// Cập nhật số lượng tồn dự kiến ngay khi nhân viên chọn sách / số lượng.
document.addEventListener('DOMContentLoaded', () => {
    ['phieu-sach','phieu-sl','phieu-gia'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', updateB3StockPreview);
            element.addEventListener('change', updateB3StockPreview);
        }
    });
});

// Lịch sử xuất kho: chỉ đọc; API giới hạn quyền theo phiên đăng nhập.
let exportHistoryRequest = 0;

function resetExportHistory() {
    ++exportHistoryRequest;
    document.getElementById('export-month').value = '';
    document.getElementById('export-year').value = '';
    document.getElementById('export-count').textContent = '';
    document.querySelector('#table-export-history tbody').replaceChildren();
}

function showExportHistory() {
    const role = document.getElementById('main-app').dataset.role;
    if (!['staff', 'manager'].includes(role)) return;
    switchTab('export-history');
    window.warehouseTheme.closeDrawer();
    window.warehouseTheme.closeManagerDrawer();
    window.warehouseTheme.setNav(role === 'staff' ? 'side-staff-history' : 'side-manager-history');
    document.getElementById('page-title').textContent = 'Lịch sử xuất kho';
    document.getElementById('export-history-scope').textContent = role === 'staff'
        ? 'Xem lại các phiếu xuất do bạn lập.' : 'Xem toàn bộ phiếu xuất đã lưu trong kho.';
    loadExportHistory();
}

function resetExportFilters() {
    document.getElementById('export-month').value = '';
    document.getElementById('export-year').value = '';
    loadExportHistory();
}

async function loadExportHistory() {
    const role = document.getElementById('main-app').dataset.role;
    if (!['staff', 'manager'].includes(role)) return;
    const requestId = ++exportHistoryRequest;
    const tbody = document.querySelector('#table-export-history tbody');
    const count = document.getElementById('export-count');
    const params = new URLSearchParams({thang: document.getElementById('export-month').value,
        nam: document.getElementById('export-year').value});
    const message = text => {
        tbody.replaceChildren();
        const cell = tbody.insertRow().insertCell();
        cell.colSpan = 6;
        cell.textContent = text;
    };
    count.textContent = '';
    message('Đang tải phiếu xuất kho…');
    try {
        const receipts = await b3Fetch('/api/phieu-xuat?' + params.toString());
        if (requestId !== exportHistoryRequest) return;
        if (!Array.isArray(receipts)) throw new Error('Danh sách phiếu xuất không hợp lệ.');
        tbody.replaceChildren();
        count.textContent = receipts.length.toLocaleString('vi-VN') + ' phiếu';
        if (!receipts.length) { message('Không có phiếu xuất phù hợp.'); return; }
        for (const receipt of receipts) {
            const row = tbody.insertRow();
            const quantity = receipt.chi_tiet.reduce((sum, item) => sum + Number(item.so_luong_xuat), 0);
            for (const value of [receipt.ma_phieu_xuat, receipt.ngay_xuat, receipt.nguoi_nhan,
                receipt.nguoi_lap, quantity.toLocaleString('vi-VN')]) row.insertCell().textContent = value ?? '—';
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'history-view-button';
            button.textContent = 'Xem / In';
            button.addEventListener('click', () => viewExportReceipt(receipt));
            row.insertCell().append(button);
        }
    } catch (error) {
        if (requestId === exportHistoryRequest) message(error.message || 'Không tải được phiếu xuất kho.');
    }
}

function viewExportReceipt(receipt) {
    const app = v('main-app');
    if (app.dataset.role === 'manager' || (app.dataset.role === 'staff' && receipt.nguoi_lap === app.dataset.username)) renderWarehouseReceipt('xuat',receipt);
}

// Một mẫu chứng từ dùng chung cho phiếu nhập và xuất, dữ liệu động gán bằng textContent.
function renderWarehouseReceipt(mode, receipt, justSaved = false) {
    const inbound = mode === 'nhap';
    const area = v('print-area');
    const el = (tag, text, cls) => { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (cls) node.className = cls; return node; };
    const doc = el('article',undefined,'warehouse-receipt ' + (inbound ? 'receipt-in' : 'receipt-out'));
    const top = el('div',undefined,'receipt-top');
    const brand = el('div',undefined,'receipt-brand'); brand.append(el('strong','KHO SÁCH'),el('small','HỆ THỐNG QUẢN LÝ & LƯU TRỮ'));
    top.append(brand,el('span',justSaved ? 'Đã lưu thành công' : 'Chứng từ đã lưu','receipt-status')); doc.append(top);
    const title = el('div',undefined,'receipt-title'); title.append(el('h2',inbound ? 'PHIẾU NHẬP KHO' : 'PHIẾU XUẤT KHO'),el('p','Số: '+(inbound ? receipt.ma_phieu_nhap : receipt.ma_phieu_xuat))); doc.append(title);
    const meta = el('dl',undefined,'receipt-meta');
    const addMeta = (label,value,wide=false) => { const box = el('div',undefined,wide?'receipt-wide':''); box.append(el('dt',label),el('dd',value || '—')); meta.append(box); };
    const date = inbound ? receipt.ngay_nhap : receipt.ngay_xuat;
    addMeta(inbound?'Ngày nhập':'Ngày xuất', /^\d{4}-\d{2}-\d{2}$/.test(date) ? date.split('-').reverse().join('/') : date);
    addMeta('Người lập',receipt.nguoi_lap);
    if (inbound) addMeta('Nhà cung cấp', [receipt.ma_ncc,receipt.ten_ncc].filter(Boolean).join(' · '),true);
    else { addMeta('Người nhận / Bộ phận',receipt.nguoi_nhan,true); addMeta('Lý do xuất kho',receipt.ly_do,true); }
    doc.append(meta,el('h3','Chi tiết hàng hóa','receipt-table-title'));
    const table = el('table',undefined,'receipt-table'); const head=table.createTHead().insertRow();
    for (const label of ['STT','Mã sách','Tên sách','Số lượng',...(inbound?['Đơn giá (đ)','Thành tiền (đ)']:[])]) head.append(el('th',label));
    const body=table.createTBody(), items=receipt.chi_tiet || [];
    items.forEach((item,i)=>{ const row=body.insertRow(); const values=[i+1,item.ma_sach,item.ten_sach || '—',fmt(inbound?item.so_luong_nhap:item.so_luong_xuat),...(inbound?[fmt(item.don_gia_nhap),fmt(item.thanh_tien)]:[])]; values.forEach(value=>row.insertCell().textContent=value); });
    doc.append(table);
    const totals=el('div',undefined,'receipt-totals');
    const addTotal=(label,value)=>{ const box=el('div'); box.append(el('span',label),el('strong',value)); totals.append(box); };
    addTotal('Số đầu sách',fmt(new Set(items.map(i=>i.ma_sach)).size));
    addTotal('Tổng số cuốn',fmt(items.reduce((sum,i)=>sum+Number(inbound?i.so_luong_nhap:i.so_luong_xuat),0)));
    if(inbound) addTotal('Tổng tiền nhập',money(receipt.tong_tien));
    doc.append(totals);
    const sign=el('div',undefined,'receipt-signatures');
    for(const label of ['Người lập phiếu',inbound?'Người giao hàng':'Người nhận hàng','Thủ kho']) { const box=el('div'); box.append(el('strong',label),el('small','(Ký, ghi rõ họ tên)')); sign.append(box); }
    doc.append(sign); area.replaceChildren(doc);
    v('print-modal').classList.add('is-open'); document.querySelector('#print-modal .modal-content').scrollTop = 0; document.querySelector('#print-modal .close').focus({preventScroll:true});
}
