// Chuẩn hóa lỗi API và cập nhật giao diện khi quyền phiên bị thu hồi.
let sessionRefreshPending = false;
function apiErrorResponse(message, status = 503) {
    return new Response(JSON.stringify({error: message}), {
        status, headers: {'Content-Type': 'application/json'}
    });
}
async function apiFetch(url, options = {}) {
    try {
        const response = await window.fetch(url, {...options, cache: 'no-store'});
        if ([401, 403].includes(response.status) && url !== '/api/login' && url !== '/api/check-session') {
            void refreshCurrentSession();
        }
        try {
            await response.clone().json();
        } catch {
            return apiErrorResponse(`Máy chủ trả dữ liệu không hợp lệ (${response.status}).`,
                response.status >= 400 && response.status <= 599 ? response.status : 502);
        }
        return response;
    } catch {
        return apiErrorResponse('Không thể kết nối máy chủ. Vui lòng kiểm tra mạng và thử lại.');
    }
}
async function refreshCurrentSession() {
    const main = document.getElementById('main-app');
    if (!main?.dataset.role || sessionRefreshPending) return;
    sessionRefreshPending = true;
    try {
        const res = await apiFetch('/api/check-session');
        if (!res.ok) return; // Lỗi mạng không đồng nghĩa với mất phiên.
        const data = await res.json();
        if (!data.logged_in || data.role !== main.dataset.role || data.username !== main.dataset.username) {
            // Đóng các màn hình và dữ liệu thuộc quyền cũ; yêu cầu đăng nhập lại khi bị thu hồi.
            await checkSession();
        }
    } finally {
        sessionRefreshPending = false;
    }
}
window.addEventListener('focus', refreshCurrentSession);
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) void refreshCurrentSession();
});
setInterval(() => { if (!document.hidden) void refreshCurrentSession(); }, 15000);

document.addEventListener("DOMContentLoaded", () => {
    checkSession();
});

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-user').value.trim();
    const password = document.getElementById('login-pass').value;

    const res = await apiFetch('/api/login', {
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
    window.warehouseTheme?.closeStockSummary();
    const res = await apiFetch('/api/logout', { method: 'POST' });
    if (!res.ok) { alert((await res.json()).error); return; }
    await checkSession();
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.toggle('active', el.id === 'tab-' + tabId));
    document.getElementById('library-overview').hidden = ['export-history','import-history'].includes(tabId);
}

async function loadNCCSelect() {
    const res = await apiFetch('/api/ncc');
    if(!res.ok) { alert((await res.json()).error); return; }
    const data = await res.json();
    const filterNcc = document.getElementById('filter-ncc');
    const pnNcc = document.getElementById('pn-ncc');
    const sNcc = document.getElementById('s-ncc');

    const selected = [filterNcc.value, pnNcc.value, sNcc.value];
    filterNcc.replaceChildren(new Option('-- Tất cả NCC --', ''));
    pnNcc.replaceChildren(new Option('-- Chọn nhà cung cấp --', ''));
    sNcc.replaceChildren(new Option('-- Chọn nhà cung cấp --', ''));

    for (const [index, select] of [filterNcc, pnNcc, sNcc].entries()) {
        for (const n of data) select.add(new Option(n.ten_ncc, n.ma_ncc));
        if (Array.from(select.options).some(option => option.value === selected[index])) {
            select.value = selected[index];
        }
    }
}

// --- Quản trị hệ thống ---

async function loadAdminData() {
    const [usersRes, positionsRes] = await Promise.all([
        apiFetch('/api/admin/users'),
        apiFetch('/api/admin/positions')
    ]);
    if (!usersRes.ok || !positionsRes.ok) {
        document.querySelector('#table-admin-users tbody').replaceChildren();
        document.querySelector('#table-admin-positions tbody').replaceChildren();
        document.getElementById('admin-user-count').textContent = 'Không tải được dữ liệu';
        window.adminUI?.toast('Không thể tải dữ liệu quản trị. Vui lòng kiểm tra kết nối và quyền truy cập.', 'error');
        return;
    }

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
    window.adminUI?.render({users, positions});
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
    window.adminUI?.openDrawer('user', true);
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
    const res = await apiFetch(url, {
        method: editing ? 'PUT' : 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (!res.ok) {
        alert(result.error || 'Không thể lưu tài khoản.');
        return;
    }
    form.reset();
    window.adminUI?.closeDrawer();
    window.adminUI?.toast(result.message, 'success');
    await loadAdminData();
}

async function deleteAdminUser(username) {
    if (!confirm(`Xóa tài khoản ${username}?`)) return;
    const res = await apiFetch(`/api/admin/users/${encodeURIComponent(username)}`, {method: 'DELETE'});
    const result = await res.json();
    if (!res.ok) {
        alert(result.error || 'Không thể xóa tài khoản.');
        return;
    }
    window.adminUI?.toast(result.message || 'Đã xóa tài khoản.', 'success');
    await loadAdminData();
}

function editAdminPosition(position) {
    const form = document.getElementById('form-admin-position');
    form.dataset.editPosition = position;
    document.getElementById('admin-position-name').value = position;
    document.getElementById('admin-position-submit').textContent = 'Lưu thay đổi';
    document.getElementById('admin-position-cancel').hidden = false;
    window.adminUI?.openDrawer('position', true);
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
    const res = await apiFetch(url, {
        method: oldName ? 'PUT' : 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ten_chuc_vu: name})
    });
    const result = await res.json();
    if (!res.ok) {
        alert(result.error || 'Không thể lưu chức vụ.');
        return;
    }
    form.reset();
    window.adminUI?.closeDrawer();
    window.adminUI?.toast(result.message, 'success');
    await loadAdminData();
}

async function deleteAdminPosition(position) {
    if (!confirm(`Xóa chức vụ "${position}"?`)) return;
    const res = await apiFetch(`/api/admin/positions/${encodeURIComponent(position)}`, {method: 'DELETE'});
    const result = await res.json();
    if (!res.ok) {
        alert(result.error || 'Không thể xóa chức vụ.');
        return;
    }
    window.adminUI?.toast(result.message || 'Đã xóa chức vụ.', 'success');
    await loadAdminData();
}

async function checkSession() {
    const res = await apiFetch('/api/check-session');
    if (!res.ok) { alert((await res.json()).error); return; }
    const data = await res.json();
    if (data.logged_in) {
        document.getElementById('login-container').style.display = 'none';
        document.getElementById('main-app').style.display = 'grid';

        window.warehouseTheme?.setRole(data);
        resetExportHistory();
        resetImportHistory();
        if (data.role === 'admin') {
            document.getElementById('user-info').innerText = `Xin chào: ${data.ho_ten} (Quản trị hệ thống)`;
            switchTab('admin');
            window.adminUI?.showSection('overview');
            loadAdminData();
            return;
        }
        await loadNCCSelect();
        if (data.role === 'manager') {
            document.getElementById('user-info').innerText = `Xin chào: ${data.ho_ten} (Quản lý Kho)`;
            switchManagerSubTab('sach');
        } else {
            document.getElementById('user-info').innerText = `Xin chào: ${data.ho_ten} (Nhân viên Kho)`;
            switchStaffSubTab('tra-cuu');
        }
    } else {
        window.warehouseTheme?.closeStockSummary();
        window.warehouseTheme?.closeDrawer();
        window.warehouseTheme?.closeManagerDrawer();
        window.adminUI?.closeDrawer();
        resetExportHistory();
        resetImportHistory();
        closePrintModal();
        document.getElementById('print-area').replaceChildren();
        document.getElementById('print-receipt').replaceChildren();
        document.getElementById('main-app').dataset.role = '';
        document.getElementById('main-app').dataset.username = '';
        resetVoucherSession();
        document.getElementById('login-container').style.display = 'flex';
        document.getElementById('main-app').style.display = 'none';
    }
}
