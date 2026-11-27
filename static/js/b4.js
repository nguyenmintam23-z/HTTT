function switchManagerSubTab(subId) {
    if (document.getElementById('main-app').dataset.role !== 'manager') return;
    if (subId === 'thongke') return showImportHistory(true);
    const sections = {sach: ['mgr-sach-section', 'Quản lý sách'],
        ncc: ['mgr-ncc-section', 'Nhà cung cấp']};
    if (!sections[subId]) return;
    switchTab('quan-ly');
    window.warehouseTheme.closeManagerDrawer();
    for (const [key, [id]] of Object.entries(sections)) {
        document.getElementById(id).style.display = key === subId ? 'block' : 'none';
    }
    window.warehouseTheme.setNav('side-manager-' + subId);
    document.getElementById('page-title').textContent = sections[subId][1];
    loadQuanLyData();
}

function editRecord(formId, fields, record) {
    const form = document.getElementById(formId);
    for (const [id, field] of Object.entries(fields)) {
        document.getElementById(id).value = record[field] ?? '';
    }
    const codeInput = form.querySelector('[data-record-code]');
    codeInput.readOnly = formId !== 'form-sach';
    form.dataset.editCode = codeInput.value;
    if (formId === 'form-sach') document.getElementById('s-ton').readOnly = true;
    form.querySelector('[type=submit]').textContent = 'Lưu thay đổi';
    form.querySelector('[type=reset]').hidden = false;
    window.warehouseTheme?.openManagerDrawer(formId === 'form-sach' ? 'sach' : 'ncc', false);
}

function clearEdit(form) {
    delete form.dataset.editCode;
    form.querySelector('[data-record-code]').readOnly = false;
    if (form.id === 'form-sach') document.getElementById('s-ton').readOnly = false;
    const submit = form.querySelector('[type=submit]');
    submit.textContent = submit.dataset.addLabel;
    form.querySelector('[type=reset]').hidden = true;
}

function appendManagementRow(body, values, edit, remove) {
    const row = body.insertRow();
    for (const value of values) row.insertCell().textContent = value ?? '';
    const cell = row.insertCell();
    const editButton = document.createElement('button');
    editButton.textContent = 'Sửa';
    editButton.addEventListener('click', edit);
    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Xóa';
    deleteButton.className = 'btn-danger';
    deleteButton.addEventListener('click', remove);
    cell.append(editButton, ' ', deleteButton);
}

function showManagementEmpty(body, columns, message) {
    const cell = body.insertRow().insertCell();
    cell.colSpan = columns;
    cell.textContent = message;
}

let b4ManagementRequest = 0;
let bookPage = 1;
const bookPageSize = 10;
let bookResults = [];

function resetBookSearch() {
    document.getElementById('ql-sach-search').value = '';
    document.getElementById('ql-sach-sort').value = '';
    document.getElementById('ql-sach-stock').value = '';
    bookPage = 1;
    loadQuanLyData();
}

function changeBookPage(direction) {
    bookPage = Math.max(1, Math.min(Math.ceil(bookResults.length / bookPageSize), bookPage + direction));
    renderBooks();
}

function decorateBookRow(row, index) {
    const number = row.insertCell(0);
    number.textContent = (bookPage - 1) * bookPageSize + index + 1;
    const title = row.cells[2];
    const icon = document.createElement('span');
    icon.className = 'book-tile book-color-' + (index % 6);
    icon.textContent = '▤';
    icon.setAttribute('aria-hidden', 'true');
    title.prepend(icon);
    for (const [column, className] of [[3, 'category-pill'], [6, 'stock-pill']]) {
        const cell = row.cells[column];
        const badge = document.createElement('span');
        badge.textContent = cell.textContent;
        badge.className = className;
        cell.replaceChildren(badge);
    }
    const buttons = row.cells[8].querySelectorAll('button');
    buttons[0].textContent = '✎';
    buttons[1].textContent = '';
    const trash = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    trash.setAttribute('viewBox', '0 0 24 24');
    trash.setAttribute('width', '20');
    trash.setAttribute('height', '20');
    trash.setAttribute('fill', 'none');
    trash.setAttribute('stroke', 'currentColor');
    trash.setAttribute('stroke-width', '1.8');
    trash.setAttribute('stroke-linecap', 'round');
    trash.setAttribute('stroke-linejoin', 'round');
    trash.setAttribute('aria-hidden', 'true');
    const outline = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    outline.setAttribute('d', 'M3 6h18M9 6V4h6v2M5 6l1 14h12l1-14M10 10v6M14 10v6');
    trash.append(outline);
    buttons[1].append(trash);
    buttons.forEach((button, i) => {
        button.title = i ? 'Xóa sách' : 'Sửa sách';
        button.setAttribute('aria-label', button.title);
    });
}

function renderBooks() {
    const tbS = document.querySelector('#table-ql-sach tbody');
    tbS.replaceChildren();
    bookPage = Math.max(1, Math.min(bookPage, Math.ceil(bookResults.length / bookPageSize)));
    if (!bookResults.length) showManagementEmpty(tbS, 9, 'Không tìm thấy sách.');
    const start = (bookPage - 1) * bookPageSize;
    bookResults.slice(start, start + bookPageSize).forEach((s, index) => {
        appendManagementRow(tbS, [
            s.ma_sach, s.ten_sach, s.the_loai, s.tac_gia,
            (s.gia_ban ?? 0).toLocaleString('vi-VN') + ' đ', s.so_luong_ton, s.vi_tri
        ], () => editRecord('form-sach', {
            's-ma': 'ma_sach', 's-ten': 'ten_sach', 's-theloai': 'the_loai',
            's-tacgia': 'tac_gia', 's-nxb': 'nha_xuat_ban', 's-ncc': 'ma_ncc',
            's-gianhap': 'gia_nhap', 's-giaban': 'gia_ban',
            's-ton': 'so_luong_ton', 's-vitri': 'vi_tri'
        }, s), () => deleteSach(s.ma_sach));
        decorateBookRow(tbS.rows[tbS.rows.length - 1], index);
    });
    document.getElementById('book-page').textContent = bookPage;
    document.getElementById('book-prev').disabled = bookPage === 1;
    document.getElementById('book-next').disabled = bookPage * bookPageSize >= bookResults.length;
}

async function loadQuanLyData() {
    const requestId = ++b4ManagementRequest;
    const params = new URLSearchParams({
        q: document.getElementById('ql-sach-search').value.trim(),
        sort: ['ten','gia'].includes(document.getElementById('ql-sach-sort').value) ? document.getElementById('ql-sach-sort').value : ''
    });
    const supplierQuery = document.getElementById('ql-ncc-search').value.trim().toLocaleLowerCase('vi');
    const supplierSort = document.getElementById('ql-ncc-sort').value;
    const [resS, resN] = await Promise.all([
        fetch('/api/sach?' + params),
        fetch('/api/ncc')
    ]);
    const [dataS, suppliers] = await Promise.all([
        resS.ok ? resS.json() : null,
        resN.ok ? resN.json() : null
    ]);
    if (requestId !== b4ManagementRequest) return;
    if (dataS) {
        bookResults = filterStockRows(dataS, document.getElementById('ql-sach-stock').value, document.getElementById('ql-sach-sort').value);
        document.getElementById('manager-result-count').textContent = bookResults.length + ' đầu sách';
        renderBooks();
    }
    
    if (suppliers) {
        window.warehouseTheme?.updateSupplierMetrics(suppliers);
        const dataN = suppliers.filter(n =>
            [n.ma_ncc, n.ten_ncc].some(value => value.toLocaleLowerCase('vi').includes(supplierQuery))
        );
        if (supplierSort) {
            const field = supplierSort === 'ten' ? 'ten_ncc' : 'ma_ncc';
            dataN.sort((a, b) => a[field].localeCompare(b[field], 'vi'));
        }
        const tbN = document.querySelector('#table-ql-ncc tbody');
        tbN.innerHTML = '';
        if (!dataN.length) showManagementEmpty(tbN, 6, 'Không tìm thấy nhà cung cấp.');
        dataN.forEach(n => {
            appendManagementRow(tbN, [n.ma_ncc, n.ten_ncc, n.dia_chi, n.so_dien_thoai, n.email], () => {
                editRecord('form-ncc', {
                    'ncc-ma': 'ma_ncc',
                    'ncc-ten': 'ten_ncc',
                    'ncc-diachi': 'dia_chi',
                    'ncc-sdt': 'so_dien_thoai',
                    'ncc-email': 'email'
                }, n);
            }, () => deleteNCC(n.ma_ncc));
        });
    }
}

async function saveSach(e) {
    e.preventDefault();
    const payload = {
        ma_sach: document.getElementById('s-ma').value.trim(),
        ten_sach: document.getElementById('s-ten').value.trim(),
        the_loai: document.getElementById('s-theloai').value.trim(),
        tac_gia: document.getElementById('s-tacgia').value.trim(),
        nha_xuat_ban: document.getElementById('s-nxb').value.trim(),
        ma_ncc: document.getElementById('s-ncc').value,
        gia_nhap: parseFloat(document.getElementById('s-gianhap').value) || 0,
        gia_ban: parseFloat(document.getElementById('s-giaban').value) || 0,
        so_luong_ton: parseInt(document.getElementById('s-ton').value) || 0,
        vi_tri: document.getElementById('s-vitri').value.trim()
    };
    const editCode = e.currentTarget.dataset.editCode;
    if (editCode) delete payload.so_luong_ton;
    const url = editCode ? `/api/sach/${encodeURIComponent(editCode)}` : '/api/sach';
    const res = await fetch(url, {
        method: editCode ? 'PUT' : 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    const result = await res.json();
    if(res.ok) { alert(result.message); loadQuanLyData(); loadSachSelect(); document.getElementById('form-sach').reset(); window.warehouseTheme?.closeManagerDrawer(); window.warehouseTheme?.refreshMetrics(); }
    else { alert(result.error); }
}

async function deleteSach(ma) {
    if(confirm(`Xóa sách ${ma}?`)) {
        const res = await fetch(`/api/sach/${ma}`, { method: 'DELETE' });
        const result = await res.json();
        if(res.ok) { loadQuanLyData(); loadSachSelect(); window.warehouseTheme?.refreshMetrics(); } else { alert(result.error); }
    }
}

async function saveNCC(e) {
    e.preventDefault();
    const payload = {
        ma_ncc: document.getElementById('ncc-ma').value.trim(),
        ten_ncc: document.getElementById('ncc-ten').value.trim(),
        dia_chi: document.getElementById('ncc-diachi').value.trim(),
        so_dien_thoai: document.getElementById('ncc-sdt').value.trim(),
        email: document.getElementById('ncc-email').value.trim()
    };
    const editCode = e.currentTarget.dataset.editCode;
    const url = editCode ? `/api/ncc/${encodeURIComponent(editCode)}` : '/api/ncc';
    const res = await fetch(url, {
        method: editCode ? 'PUT' : 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    const result = await res.json();
    if(res.ok) { alert(result.message); loadQuanLyData(); loadNCCSelect(); document.getElementById('form-ncc').reset(); window.warehouseTheme?.closeManagerDrawer(); window.warehouseTheme?.refreshMetrics(); }
    else { alert(result.error); }
}

async function deleteNCC(ma) {
    if(confirm(`Xóa nhà cung cấp ${ma}?`)) {
        const res = await fetch(`/api/ncc/${ma}`, { method: 'DELETE' });
        const result = await res.json();
        if(res.ok) { loadQuanLyData(); loadNCCSelect(); window.warehouseTheme?.refreshMetrics(); } else { alert(result.error); }
    }
}

let b4HistoryRequest = 0;
let importStatisticsMode = false;

function resetImportHistory() {
    ++b4HistoryRequest;
    importStatisticsMode = false;
    v('stat-thang').value = ''; v('stat-nam').value = '';
    clearImportYearError();
    v('import-count').textContent = '';
    document.querySelector('#table-thongke tbody').replaceChildren();
    clearImportStatistics();
    v('stat-period').textContent = '';
    setImportFeedback('');
    v('import-filter-submit').textContent = 'Lọc phiếu nhập';
    v('import-statistics').hidden = true;
}
function resetImportFilters() {
    v('stat-thang').value = ''; v('stat-nam').value = '';
    clearImportYearError();
    loadThongKe({reveal: true});
}
function showImportHistory(statistics = false) {
    const role = v('main-app').dataset.role;
    if (!['staff','manager'].includes(role) || (statistics && role !== 'manager')) return;
    importStatisticsMode = statistics;
    switchTab('import-history');
    window.warehouseTheme.closeDrawer();
    window.warehouseTheme.closeManagerDrawer();
    window.warehouseTheme.setNav(role === 'staff' ? 'side-staff-import' : statistics ? 'side-manager-thongke' : 'side-manager-import');
    v('page-title').textContent = statistics ? 'Thống kê nhập kho' : 'Lịch sử nhập kho';
    v('import-filter-title').textContent = statistics ? 'Chọn kỳ thống kê' : 'Tra cứu phiếu nhập kho';
    v('import-history-scope').textContent = role === 'staff' ? 'Chỉ hiển thị các phiếu nhập do bạn lập.' : statistics ? 'Tổng hợp số lượng và giá trị nhập kho theo tháng, năm.' : 'Xem toàn bộ phiếu nhập đã lưu trong kho.';
    v('import-filter-submit').textContent = statistics ? 'Xem thống kê' : 'Lọc phiếu nhập';
    v('import-history-list').hidden = statistics;
    v('import-statistics').hidden = !statistics;
    loadThongKe();
}
function setImportFeedback(message, state = '') {
    const feedback = v('import-filter-feedback');
    feedback.textContent = message;
    feedback.dataset.state = state;
    feedback.hidden = !message;
}
const importYearErrorMessage = 'Năm phải gồm đúng 4 chữ số (1000–9999), ví dụ 2026. Để trống nếu muốn xem tất cả năm.';
function isValidImportYear(year) {
    return year === '' || /^[1-9][0-9]{3}$/.test(year);
}
function showImportYearError() {
    v('stat-nam').setAttribute('aria-invalid', 'true');
    setImportFeedback(importYearErrorMessage, 'error');
}
function clearImportYearError() {
    if (!isValidImportYear(v('stat-nam').value)) return;
    v('stat-nam').removeAttribute('aria-invalid');
    if (v('import-filter-feedback').textContent === importYearErrorMessage) setImportFeedback('');
}
function importPeriodLabel(month, year) {
    if (month && year) return `Tháng ${Number(month)} / ${Number(year)}`;
    if (month) return `Tháng ${Number(month)} của tất cả các năm`;
    if (year) return `Năm ${Number(year)}`;
    return 'Tất cả tháng, tất cả năm';
}
function revealImportStatistics() {
    if (!v('tab-import-history').classList.contains('active') || !importStatisticsMode) return;
    const result = v('import-statistics');
    result.focus({preventScroll: true});
    result.scrollIntoView({block: 'start', behavior: 'auto'});
}
function clearImportStatistics(message = '') {
    ['stat-receipts','stat-quantity','stat-value'].forEach(id => v(id).textContent = '—');
    v('stat-status').textContent = message;
    document.querySelector('#table-import-summary tbody').replaceChildren();
}
function renderImportStatistics(receipts) {
    const periods = new Map(); let quantity = 0, value = 0;
    for (const receipt of receipts) {
        const month = receipt.ngay_nhap.slice(0,7);
        const q = receipt.chi_tiet.reduce((sum, item) => sum + Number(item.so_luong_nhap), 0);
        const total = Number(receipt.tong_tien);
        const period = periods.get(month) || {count:0, quantity:0, value:0};
        period.count++; period.quantity += q; period.value += total;
        periods.set(month,period); quantity += q; value += total;
    }
    v('stat-receipts').textContent = fmt(receipts.length);
    v('stat-quantity').textContent = fmt(quantity);
    v('stat-value').textContent = money(value);
    v('stat-status').textContent = receipts.length ? 'Số liệu tính từ các phiếu nhập đã lưu trong kỳ.' : 'Không có phiếu nhập trong kỳ đã chọn.';
    const body = document.querySelector('#table-import-summary tbody');
    body.replaceChildren();
    if (!periods.size) showManagementEmpty(body,4,'Không có dữ liệu.');
    for (const [month, period] of [...periods].sort((a,b) => b[0].localeCompare(a[0]))) {
        const row = body.insertRow();
        [month.split('-').reverse().join('/'),fmt(period.count),fmt(period.quantity),fmt(period.value)].forEach(value => row.insertCell().textContent = value);
    }
}
async function loadThongKe({reveal = false} = {}) {
    const role = v('main-app').dataset.role;
    if (!['staff','manager'].includes(role) || (importStatisticsMode && role !== 'manager')) return;
    const month = v('stat-thang').value, year = v('stat-nam').value;
    if (!isValidImportYear(year)) {
        showImportYearError();
        if (reveal) v('stat-nam').focus();
        return;
    }
    clearImportYearError();
    const requestId = ++b4HistoryRequest;
    const statistics = importStatisticsMode;
    const tbody = document.querySelector('#table-thongke tbody');
    const period = importPeriodLabel(month, year);
    const params = new URLSearchParams();
    if (month) params.set('thang', month);
    if (year) params.set('nam', year);
    const button = v('import-filter-submit');
    const current = () => requestId === b4HistoryRequest && v('main-app').dataset.role === role;
    v('import-count').textContent = '';
    tbody.replaceChildren();
    button.textContent = 'Đang tải…';
    setImportFeedback(statistics ? `Đang tổng hợp: ${period}…` : 'Đang tải phiếu nhập…', 'loading');
    if (statistics) {
        v('import-statistics').hidden = false;
        v('import-history-list').hidden = true;
        v('stat-period').textContent = period;
        clearImportStatistics('Đang tải thống kê…');
    } else {
        v('import-statistics').hidden = true;
        v('import-history-list').hidden = false;
        showManagementEmpty(tbody,6,'Đang tải lịch sử nhập kho…');
    }
    try {
        const receipts = await b3Fetch('/api/phieu-nhap?' + params, {cache: 'no-store'});
        if (!current()) return;
        if (!Array.isArray(receipts)) throw new Error('Danh sách phiếu nhập không hợp lệ.');
        if (statistics) {
            renderImportStatistics(receipts);
            setImportFeedback(receipts.length ? `Đã cập nhật thống kê: ${fmt(receipts.length)} phiếu nhập.` : 'Không có phiếu nhập trong kỳ đã chọn.', receipts.length ? 'success' : 'empty');
            if (reveal) revealImportStatistics();
            return;
        }
        tbody.replaceChildren();
        v('import-count').textContent = fmt(receipts.length) + ' phiếu';
        if (!receipts.length) showManagementEmpty(tbody,6,'Không có phiếu nhập trong kỳ đã chọn.');
        receipts.forEach(receipt => appendReceiptRow(tbody,receipt));
        setImportFeedback(receipts.length ? `Đã tìm thấy ${fmt(receipts.length)} phiếu nhập.` : 'Không có phiếu nhập trong kỳ đã chọn.', receipts.length ? 'success' : 'empty');
    } catch (error) {
        if (!current()) return;
        const message = error.message || (statistics ? 'Không tải được thống kê.' : 'Không tải được lịch sử nhập kho.');
        setImportFeedback(message + ' Vui lòng thử lại.', 'error');
        if (statistics) clearImportStatistics(message);
        else { tbody.replaceChildren(); showManagementEmpty(tbody,6,message); }
    } finally {
        if (current()) button.textContent = statistics ? 'Xem thống kê' : 'Lọc phiếu nhập';
    }
}

function appendReceiptRow(tbody, p) {
    const row = tbody.insertRow();
    const values = [
        p.ma_phieu_nhap, p.ngay_nhap, p.ma_ncc, p.nguoi_lap,
        (p.tong_tien ?? 0).toLocaleString('vi-VN') + ' đ'
    ];
    for (const value of values) row.insertCell().textContent = value ?? '';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'history-view-button';
    button.textContent = 'Xem / In';
    button.addEventListener('click', () => viewPhieu(p));
    row.insertCell().append(button);
}

function viewPhieu(p) {
    const app = v('main-app');
    if (app.dataset.role !== 'manager' && !(app.dataset.role === 'staff' && p.nguoi_lap === app.dataset.username)) return;
    renderWarehouseReceipt('nhap',p);
}

function printReceipt() {
    const preview = document.getElementById('print-area');
    const output = document.getElementById('print-receipt');
    output.replaceChildren(...Array.from(preview.children, node => node.cloneNode(true)));
    document.body.classList.add('printing-receipt');
    window.print();
}

window.addEventListener('afterprint', () => {
    document.body.classList.remove('printing-receipt');
    document.getElementById('print-receipt').replaceChildren();
});

function closePrintModal() {
    document.getElementById('print-modal').classList.remove('is-open');
}

document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && document.getElementById('print-modal').classList.contains('is-open')) closePrintModal();
});
