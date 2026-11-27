async function b4Api(url, options = {}) {
    let response;
    try {
        response = await fetch(url, options);
    } catch {
        throw new Error('Không kết nối được máy chủ. Vui lòng thử lại.');
    }
    let data;
    try {
        data = await response.json();
    } catch {
        throw new Error('Máy chủ trả về phản hồi không hợp lệ. Vui lòng tải lại trang.');
    }
    if (!response.ok) throw new Error(data.error || 'Không thực hiện được thao tác.');
    return data;
}

async function submitB4Form(form, entity, payload) {
    const button = form.querySelector('[type=submit]');
    if (button.disabled) return;
    button.disabled = true;
    try {
        const code = form.dataset.editCode;
        const url = code ? '/api/' + entity + '/' + encodeURIComponent(code) : '/api/' + entity;
        const result = await b4Api(url, {
            method: code ? 'PUT' : 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        form.reset();
        window.warehouseTheme?.closeManagerDrawer();
        alert(result.message);
        loadQuanLyData();
        if (entity === 'sach') loadSachSelect();
        else loadNCCSelect();
        window.warehouseTheme?.refreshMetrics();
    } catch (error) {
        alert(error.message);
    } finally {
        button.disabled = false;
    }
}

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
        sort: document.getElementById('ql-sach-sort').value
    });
    const supplierQuery = document.getElementById('ql-ncc-search').value.trim().toLocaleLowerCase('vi');
    const supplierSort = document.getElementById('ql-ncc-sort').value;
    let dataS, suppliers;
    try {
        [dataS, suppliers] = await Promise.all([
            b4Api('/api/sach?' + params), b4Api('/api/ncc')
        ]);
    } catch (error) {
        if (requestId !== b4ManagementRequest) return;
        bookResults = [];
        renderBooks();
        for (const [selector, columns] of [['#table-ql-sach tbody', 9], ['#table-ql-ncc tbody', 6]]) {
            const body = document.querySelector(selector);
            body.replaceChildren();
            showManagementEmpty(body, columns, error.message);
        }
        return;
    }
    if (requestId !== b4ManagementRequest) return;
    if (dataS) {
        bookResults = dataS;
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
        gia_nhap: Number(document.getElementById('s-gianhap').value),
        gia_ban: Number(document.getElementById('s-giaban').value),
        so_luong_ton: Number(document.getElementById('s-ton').value),
        vi_tri: document.getElementById('s-vitri').value.trim()
    };
    if (e.currentTarget.dataset.editCode) delete payload.so_luong_ton;
    await submitB4Form(e.currentTarget, 'sach', payload);
}

async function deleteSach(ma) {
    if (!confirm('Xóa sách ' + ma + '?')) return;
    try {
        await b4Api('/api/sach/' + encodeURIComponent(ma), {method: 'DELETE'});
        loadQuanLyData();
        loadSachSelect();
        window.warehouseTheme?.refreshMetrics();
    } catch (error) {
        alert(error.message);
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
    await submitB4Form(e.currentTarget, 'ncc', payload);
}

async function deleteNCC(ma) {
    if (!confirm('Xóa nhà cung cấp ' + ma + '?')) return;
    try {
        await b4Api('/api/ncc/' + encodeURIComponent(ma), {method: 'DELETE'});
        loadQuanLyData();
        loadNCCSelect();
        window.warehouseTheme?.refreshMetrics();
    } catch (error) {
        alert(error.message);
    }
}

let b4HistoryRequest = 0;

async function loadThongKe() {
    const requestId = ++b4HistoryRequest;
    const tbody = document.querySelector('#table-thongke tbody');
    const params = new URLSearchParams({
        thang: document.getElementById('stat-thang').value,
        nam: document.getElementById('stat-nam').value
    });

    document.getElementById('b4-history-summary').textContent = '';
    tbody.replaceChildren();
    showManagementEmpty(tbody, 6, 'Đang tải lịch sử nhập kho…');
    try {
        const receipts = await b4Api('/api/phieu-nhap?' + params);
        if (requestId !== b4HistoryRequest) return;
        tbody.replaceChildren();
        if (!receipts.length) showManagementEmpty(tbody, 6, 'Không có phiếu nhập trong kỳ đã chọn.');
        receipts.forEach(receipt => appendReceiptRow(tbody, receipt));
        const quantity = receipts.reduce((total, receipt) =>
            total + receipt.chi_tiet.reduce((count, line) => count + line.so_luong_nhap, 0), 0);
        const amount = receipts.reduce((total, receipt) => total + receipt.tong_tien, 0);
        document.getElementById('b4-history-summary').textContent =
            receipts.length + ' phiếu · ' + quantity.toLocaleString('vi-VN') +
            ' cuốn · Tổng tiền ' + amount.toLocaleString('vi-VN') + ' đ';
    } catch (error) {
        if (requestId !== b4HistoryRequest) return;
        tbody.replaceChildren();
        showManagementEmpty(tbody, 6, error.message || 'Không tải được lịch sử nhập kho.');
    }
}

function appendReceiptRow(tbody, p) {
    const row = tbody.insertRow();
    const values = [
        p.ma_phieu_nhap, p.ngay_nhap, p.ma_ncc, p.nguoi_lap || 'Chưa ghi nhận',
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
    const summary = [p.ma_phieu_nhap, p.ngay_nhap, p.ma_ncc, p.nguoi_lap || 'Chưa ghi nhận', money(p.tong_tien)];
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