function switchManagerSubTab(subId) {
    document.querySelectorAll('#tab-quan-ly .sub-btn').forEach(btn => btn.classList.remove('active'));
    
    const sachSec = document.getElementById('mgr-sach-section');
    const nccSec = document.getElementById('mgr-ncc-section');
    const tkSec = document.getElementById('mgr-thongke-section');

    // Ẩn tất cả các section con trước
    sachSec.style.display = 'none';
    nccSec.style.display = 'none';
    tkSec.style.display = 'none';

    if (subId === 'sach') {
        document.getElementById('btn-mgr-sach').classList.add('active');
        sachSec.style.display = 'block';
        loadQuanLyData();
    } else if (subId === 'ncc') {
        document.getElementById('btn-mgr-ncc').classList.add('active');
        nccSec.style.display = 'block';
        loadQuanLyData();
    } else if (subId === 'thongke') {
        document.getElementById('btn-mgr-thongke').classList.add('active');
        tkSec.style.display = 'block';
    }
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
    form.scrollIntoView({block: 'nearest'});
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

let managementRequest = 0;
let bookPage = 1;
const bookPageSize = 10;
let bookResults = [];

function resetBookSearch() {
    document.getElementById('ql-sach-search').value = '';
    document.getElementById('ql-sach-sort').value = '';
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
    const requestId = ++managementRequest;
    const params = new URLSearchParams({
        q: document.getElementById('ql-sach-search').value.trim(),
        sort: document.getElementById('ql-sach-sort').value
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
    if (requestId !== managementRequest) return;
    if (dataS) {
        bookResults = dataS;
        renderBooks();
    }
    
    if (suppliers) {
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
    if(res.ok) { alert(result.message); loadQuanLyData(); loadSachSelect(); document.getElementById('form-sach').reset(); }
    else { alert(result.error); }
}

async function deleteSach(ma) {
    if(confirm(`Xóa sách ${ma}?`)) {
        const res = await fetch(`/api/sach/${ma}`, { method: 'DELETE' });
        const result = await res.json();
        if(res.ok) { loadQuanLyData(); loadSachSelect(); } else { alert(result.error); }
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
    if(res.ok) { alert(result.message); loadQuanLyData(); loadNCCSelect(); document.getElementById('form-ncc').reset(); }
    else { alert(result.error); }
}

async function deleteNCC(ma) {
    if(confirm(`Xóa nhà cung cấp ${ma}?`)) {
        const res = await fetch(`/api/ncc/${ma}`, { method: 'DELETE' });
        const result = await res.json();
        if(res.ok) { loadQuanLyData(); loadNCCSelect(); } else { alert(result.error); }
    }
}

let historyRequest = 0;

async function loadThongKe() {
    const requestId = ++historyRequest;
    const tbody = document.querySelector('#table-thongke tbody');
    const params = new URLSearchParams({
        thang: document.getElementById('stat-thang').value,
        nam: document.getElementById('stat-nam').value
    });

    tbody.replaceChildren();
    showManagementEmpty(tbody, 6, 'Đang tải lịch sử nhập kho…');
    try {
        const response = await fetch('/api/phieu-nhap?' + params);
        const receipts = await response.json();
        if (!response.ok) throw new Error(receipts.error);
        if (requestId !== historyRequest) return;
        tbody.replaceChildren();
        if (!receipts.length) showManagementEmpty(tbody, 6, 'Không có phiếu nhập trong kỳ đã chọn.');
        receipts.forEach(receipt => appendReceiptRow(tbody, receipt));
    } catch (error) {
        if (requestId !== historyRequest) return;
        tbody.replaceChildren();
        showManagementEmpty(tbody, 6, error.message || 'Không tải được lịch sử nhập kho.');
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
    button.textContent = 'Xem / In';
    button.addEventListener('click', () => viewPhieu(p));
    row.insertCell().append(button);
}

function viewPhieu(p) {
    const area = document.getElementById('print-area');
    area.innerHTML = `
        <h2>PHIẾU NHẬP KHO</h2>
        <p><b>Mã phiếu:</b> <span></span></p>
        <p><b>Ngày nhập:</b> <span></span></p>
        <p><b>Nhà cung cấp:</b> <span></span></p>
        <p><b>Người lập:</b> <span></span></p>
        <table>
            <thead><tr><th>Mã sách</th><th>Số lượng</th><th>Đơn giá</th><th>Thành tiền</th></tr></thead>
            <tbody></tbody>
        </table>
        <h3>Tổng tiền: <span></span></h3>
    `;
    const money = value => (value ?? 0).toLocaleString('vi-VN') + ' đ';
    const summary = [p.ma_phieu_nhap, p.ngay_nhap, p.ma_ncc, p.nguoi_lap, money(p.tong_tien)];
    area.querySelectorAll('span').forEach((field, index) => {
        field.textContent = summary[index] ?? '';
    });
    const body = area.querySelector('tbody');
    for (const item of p.chi_tiet) {
        const row = body.insertRow();
        const values = [item.ma_sach, item.so_luong_nhap, money(item.don_gia_nhap), money(item.thanh_tien)];
        for (const value of values) row.insertCell().textContent = value;
    }
    document.getElementById('print-modal').classList.add('is-open');
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