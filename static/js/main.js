document.addEventListener("DOMContentLoaded", () => {
    checkSession();
});

// --- Điều hướng Sub-tabs cho Quản lý Kho ---
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

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-user').value.trim();
    const password = document.getElementById('login-pass').value.trim();

    const res = await fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username, password })
    });
    const result = await res.json();
    if(res.ok) {
        checkSession();
    } else {
        alert(result.error);
    }
}

async function handleLogout() {
    await fetch('/api/logout', { method: 'POST' });
    checkSession();
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.role-switch button').forEach(el => el.classList.remove('active'));

    if(tabId === 'nhan-vien') {
        document.getElementById('tab-nhan-vien').classList.add('active');
        document.getElementById('btn-nv').classList.add('active');
        loadSachNhanVien();
    } else if (tabId === 'quan-ly') {
        document.getElementById('tab-quan-ly').classList.add('active');
        document.getElementById('btn-ql').classList.add('active');
        loadQuanLyData();
    } else {
        document.getElementById('tab-admin').classList.add('active');
        document.getElementById('btn-admin').classList.add('active');
        loadAdminData();
    }
}

async function loadSachNhanVien() {
    const keyword = document.getElementById('search-keyword').value;
    const ncc = document.getElementById('filter-ncc').value;
    const sort = document.getElementById('sort-select').value;

    const res = await fetch(`/api/sach?q=${encodeURIComponent(keyword)}&ncc=${encodeURIComponent(ncc)}&sort=${sort}`);
    const data = await res.json();
    if(!res.ok) return;

    const tbody = document.querySelector('#table-nv-sach tbody');
    tbody.innerHTML = '';
    data.forEach(s => {
        tbody.innerHTML += `<tr>
            <td>${s.ma_sach}</td><td>${s.ten_sach}</td><td>${s.the_loai}</td><td>${s.tac_gia}</td>
            <td>${s.gia_ban.toLocaleString()} đ</td><td><b>${s.so_luong_ton}</b></td><td>${s.vi_tri || ''}</td>
        </tr>`;
    });
}

async function loadNCCSelect() {
    const res = await fetch('/api/ncc');
    if(!res.ok) return;
    const data = await res.json();
    const filterNcc = document.getElementById('filter-ncc');
    const pnNcc = document.getElementById('pn-ncc');
    const sNcc = document.getElementById('s-ncc');

    const selected = [filterNcc.value, pnNcc.value, sNcc.value];
    filterNcc.replaceChildren(new Option('-- Tất cả NCC --', ''));
    pnNcc.replaceChildren();
    sNcc.replaceChildren(new Option('-- Chọn nhà cung cấp --', ''));

    for (const [index, select] of [filterNcc, pnNcc, sNcc].entries()) {
        for (const n of data) select.add(new Option(n.ten_ncc, n.ma_ncc));
        if (Array.from(select.options).some(option => option.value === selected[index])) {
            select.value = selected[index];
        }
    }
}

async function loadSachSelect() {
    const res = await fetch('/api/sach');
    if(!res.ok) return;
    const data = await res.json();
    const select = document.getElementById('phieu-sach');
    select.innerHTML = '';
    data.forEach(s => {
        select.innerHTML += `<option value="${s.ma_sach}">${s.ten_sach} (Tồn: ${s.so_luong_ton})</option>`;
    });
}

function togglePhieuForm() {
    const loai = document.getElementById('phieu-loai').value;
    if(loai === 'nhap') {
        document.getElementById('nhap-fields').style.display = 'block';
        document.getElementById('xuat-fields').style.display = 'none';
        document.getElementById('phieu-gia').style.display = 'block';
    } else {
        document.getElementById('nhap-fields').style.display = 'none';
        document.getElementById('xuat-fields').style.display = 'block';
        document.getElementById('phieu-gia').style.display = 'none';
    }
}

async function submitPhieu() {
    const loai = document.getElementById('phieu-loai').value;
    const maSach = document.getElementById('phieu-sach').value;
    const soLuong = parseInt(document.getElementById('phieu-sl').value);

    if(!soLuong || soLuong <= 0) { alert('Số lượng không hợp lệ!'); return; }

    if(loai === 'nhap') {
        const maPhieu = document.getElementById('pn-ma').value.trim();
        const maNCC = document.getElementById('pn-ncc').value;
        const donGia = parseFloat(document.getElementById('phieu-gia').value) || 0;
        if(!maPhieu) { alert('Nhập mã phiếu nhập!'); return; }

        const res = await fetch('/api/phieu-nhap', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                ma_phieu_nhap: maPhieu, ngay_nhap: new Date().toISOString().split('T')[0],
                ma_ncc: maNCC, chi_tiet: [{ ma_sach: maSach, so_luong_nhap: soLuong, don_gia_nhap: donGia }]
            })
        });
        const result = await res.json();
        if(res.ok) { alert(result.message); loadSachNhanVien(); loadSachSelect(); }
        else { alert(result.error); }
    } else {
        const maPhieu = document.getElementById('px-ma').value.trim();
        const nguoiNhan = document.getElementById('px-nguoinhan').value.trim();
        const lyDo = document.getElementById('px-lydo').value.trim();
        if(!maPhieu) { alert('Nhập mã phiếu xuất!'); return; }

        const res = await fetch('/api/phieu-xuat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                ma_phieu_xuat: maPhieu, ngay_xuat: new Date().toISOString().split('T')[0],
                nguoi_nhan: nguoiNhan, ly_do: lyDo, chi_tiet: [{ ma_sach: maSach, so_luong_xuat: soLuong }]
            })
        });
        const result = await res.json();
        if(res.ok) { alert(result.message); loadSachNhanVien(); loadSachSelect(); }
        else { alert(result.error); }
    }
}

function editRecord(formId, fields, record) {
    const form = document.getElementById(formId);
    for (const [id, field] of Object.entries(fields)) {
        document.getElementById(id).value = record[field] ?? '';
    }
    const codeInput = form.querySelector('[data-record-code]');
    codeInput.readOnly = true;
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
        const tbS = document.querySelector('#table-ql-sach tbody');
        tbS.innerHTML = '';
        if (!dataS.length) showManagementEmpty(tbS, 8, 'Không tìm thấy sách.');
        dataS.forEach(s => {
            appendManagementRow(tbS, [
                s.ma_sach, s.ten_sach, s.the_loai, s.tac_gia,
                (s.gia_ban ?? 0).toLocaleString('vi-VN') + ' đ', s.so_luong_ton, s.vi_tri
            ], () => {
                editRecord('form-sach', {
                    's-ma': 'ma_sach',
                    's-ten': 'ten_sach',
                    's-theloai': 'the_loai',
                    's-tacgia': 'tac_gia',
                    's-nxb': 'nha_xuat_ban',
                    's-ncc': 'ma_ncc',
                    's-gianhap': 'gia_nhap',
                    's-giaban': 'gia_ban',
                    's-ton': 'so_luong_ton',
                    's-vitri': 'vi_tri'
                }, s);
            }, () => deleteSach(s.ma_sach));
        });
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

// --- Điều hướng Sub-tabs cho Nhân viên kho ---
function switchStaffSubTab(subId) {
    document.querySelectorAll('.sub-btn').forEach(btn => btn.classList.remove('active'));

    const traCuuSec = document.getElementById('staff-tra-cuu-section');
    const lapPhieuSec = document.getElementById('staff-lap-phieu-section');

    if (subId === 'tra-cuu') {
        document.getElementById('btn-sub-tra-cuu').classList.add('active');
        traCuuSec.style.display = 'block';
        lapPhieuSec.style.display = 'none';
        loadSachNhanVien(); // Tải lại danh sách mới nhất
    } else {
        document.getElementById('btn-sub-lap-phieu').classList.add('active');
        traCuuSec.style.display = 'none';
        lapPhieuSec.style.display = 'block';
        loadSachSelect(); // Cập nhật lại dropdown danh sách sách
    }
}

async function loadAdminData() {
    const [usersRes, positionsRes] = await Promise.all([
        fetch('/api/admin/users'),
        fetch('/api/admin/positions')
    ]);
    if (!usersRes.ok || !positionsRes.ok) return;

    const [users, positions] = await Promise.all([usersRes.json(), positionsRes.json()]);
    const positionSelect = document.getElementById('admin-user-position');
    const selectedPosition = positionSelect.value;
    positionSelect.replaceChildren(new Option('-- Chọn chức vụ --', ''));
    positions.forEach(position => positionSelect.add(new Option(position, position)));
    if (positions.includes(selectedPosition)) positionSelect.value = selectedPosition;

    const userBody = document.querySelector('#table-admin-users tbody');
    userBody.replaceChildren();
    document.getElementById('admin-user-count').textContent = `${users.length} tài khoản`;
    if (!users.length) showManagementEmpty(userBody, 5, 'Chưa có tài khoản nhân viên.');
    users.forEach(user => {
        appendManagementRow(userBody, [
            user.username,
            user.ho_ten,
            user.role === 'manager' ? 'Quản lý kho' : 'Nhân viên kho',
            user.chuc_vu
        ], () => editAdminUser(user), () => deleteAdminUser(user.username));
    });

    const positionBody = document.querySelector('#table-admin-positions tbody');
    positionBody.replaceChildren();
    const counts = users.reduce((result, user) => {
        result[user.chuc_vu] = (result[user.chuc_vu] || 0) + 1;
        return result;
    }, {});
    if (!positions.length) showManagementEmpty(positionBody, 3, 'Chưa có chức vụ.');
    positions.forEach(position => {
        appendManagementRow(positionBody, [position, counts[position] || 0],
            () => editAdminPosition(position), () => deleteAdminPosition(position));
    });
}

function editAdminUser(user) {
    const form = document.getElementById('form-admin-user');
    document.getElementById('admin-user-name').value = user.username;
    document.getElementById('admin-user-name').readOnly = true;
    document.getElementById('admin-user-fullname').value = user.ho_ten || '';
    document.getElementById('admin-user-role').value = user.role;
    document.getElementById('admin-user-position').value = user.chuc_vu || '';
    document.getElementById('admin-user-password').value = '';
    document.getElementById('admin-user-password').required = false;
    form.dataset.editUsername = user.username;
    document.getElementById('admin-user-submit').textContent = 'Lưu thay đổi';
    document.getElementById('admin-user-cancel').hidden = false;
    form.scrollIntoView({block: 'nearest'});
}

function clearAdminUserEdit() {
    const form = document.getElementById('form-admin-user');
    delete form.dataset.editUsername;
    document.getElementById('admin-user-name').readOnly = false;
    document.getElementById('admin-user-password').required = true;
    document.getElementById('admin-user-submit').textContent = 'Tạo tài khoản';
    document.getElementById('admin-user-cancel').hidden = true;
}

async function saveAdminUser(event) {
    event.preventDefault();
    const form = document.getElementById('form-admin-user');
    const username = document.getElementById('admin-user-name').value.trim();
    const payload = {
        username,
        ho_ten: document.getElementById('admin-user-fullname').value.trim(),
        role: document.getElementById('admin-user-role').value,
        chuc_vu: document.getElementById('admin-user-position').value,
        password: document.getElementById('admin-user-password').value
    };
    const editing = Boolean(form.dataset.editUsername);
    const url = editing ? `/api/admin/users/${encodeURIComponent(username)}` : '/api/admin/users';
    const res = await fetch(url, {
        method: editing ? 'PUT' : 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (!res.ok) {
        alert(result.error || 'Không thể lưu tài khoản.');
        return;
    }
    alert(result.message);
    form.reset();
    await loadAdminData();
}

async function deleteAdminUser(username) {
    if (!confirm(`Xóa tài khoản ${username}?`)) return;
    const res = await fetch(`/api/admin/users/${encodeURIComponent(username)}`, {method: 'DELETE'});
    const result = await res.json();
    if (!res.ok) {
        alert(result.error || 'Không thể xóa tài khoản.');
        return;
    }
    await loadAdminData();
}

function editAdminPosition(position) {
    const form = document.getElementById('form-admin-position');
    form.dataset.editPosition = position;
    document.getElementById('admin-position-name').value = position;
    document.getElementById('admin-position-submit').textContent = 'Lưu thay đổi';
    document.getElementById('admin-position-cancel').hidden = false;
    form.scrollIntoView({block: 'nearest'});
}

function clearAdminPositionEdit() {
    const form = document.getElementById('form-admin-position');
    delete form.dataset.editPosition;
    document.getElementById('admin-position-submit').textContent = 'Thêm chức vụ';
    document.getElementById('admin-position-cancel').hidden = true;
}

async function saveAdminPosition(event) {
    event.preventDefault();
    const form = document.getElementById('form-admin-position');
    const name = document.getElementById('admin-position-name').value.trim();
    const oldName = form.dataset.editPosition;
    const url = oldName
        ? `/api/admin/positions/${encodeURIComponent(oldName)}`
        : '/api/admin/positions';
    const res = await fetch(url, {
        method: oldName ? 'PUT' : 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ten_chuc_vu: name})
    });
    const result = await res.json();
    if (!res.ok) {
        alert(result.error || 'Không thể lưu chức vụ.');
        return;
    }
    alert(result.message);
    form.reset();
    await loadAdminData();
}

async function deleteAdminPosition(position) {
    if (!confirm(`Xóa chức vụ "${position}"?`)) return;
    const res = await fetch(`/api/admin/positions/${encodeURIComponent(position)}`, {method: 'DELETE'});
    const result = await res.json();
    if (!res.ok) {
        alert(result.error || 'Không thể xóa chức vụ.');
        return;
    }
    await loadAdminData();
}

async function checkSession() {
    const res = await fetch('/api/check-session');
    const data = await res.json();
    if (data.logged_in) {
        document.getElementById('login-container').style.display = 'none';
        document.getElementById('main-app').style.display = 'block';

        const btnNv = document.getElementById('btn-nv');
        const btnQl = document.getElementById('btn-ql');
        const btnAdmin = document.getElementById('btn-admin');

        if (data.role === 'admin') {
            document.getElementById('user-info').innerText = `Xin chào: ${data.ho_ten} (Quản trị hệ thống)`;
            btnNv.style.display = 'none';
            btnQl.style.display = 'none';
            btnAdmin.style.display = 'inline-block';
            switchTab('admin');
            return;
        }

        btnAdmin.style.display = 'none';
        await loadNCCSelect();

        if (data.role === 'manager') {
            document.getElementById('user-info').innerText = `Xin chào: ${data.ho_ten} (Quản lý Kho)`;

            // Ẩn nút Nhân viên, chỉ chừa tab Quản lý
            btnNv.style.display = 'none';
            btnQl.style.display = 'inline-block';
            switchTab('quan-ly');
        } else {
            document.getElementById('user-info').innerText = `Xin chào: ${data.ho_ten} (Nhân viên Kho)`;

            // Ẩn nút Quản lý, chỉ chừa tab Nhân viên
            btnQl.style.display = 'none';
            btnNv.style.display = 'inline-block';
            switchTab('nhan-vien');
        }
    } else {
        document.getElementById('login-container').style.display = 'flex';
        document.getElementById('main-app').style.display = 'none';
    }
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