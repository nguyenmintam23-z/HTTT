document.addEventListener("DOMContentLoaded", () => {
    checkSession();
});

// --- Điều hướng Sub-tabs cho Quản lý Kho ---
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
    } else {
        document.getElementById('tab-quan-ly').classList.add('active');
        document.getElementById('btn-ql').classList.add('active');
        loadQuanLyData();
    }
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

    window.warehouseTheme?.updateSupplierMetrics(data);
    for (const [index, select] of [filterNcc, pnNcc, sNcc].entries()) {
        for (const n of data) select.add(new Option(n.ten_ncc, n.ma_ncc));
        if (Array.from(select.options).some(option => option.value === selected[index])) {
            select.value = selected[index];
        }
    }
}

async function checkSession() {
    const res = await fetch('/api/check-session');
    const data = await res.json();
    if (data.logged_in) {
        document.getElementById('login-container').style.display = 'none';
        document.getElementById('main-app').style.display = 'grid';
        
        await loadNCCSelect();

        const btnNv = document.getElementById('btn-nv');
        const btnQl = document.getElementById('btn-ql');

        if (data.role === 'manager') {
            document.getElementById('user-info').innerText = `Xin chào: ${data.ho_ten} (Quản lý Kho)`;
            
            // Ẩn nút Nhân viên, chỉ chừa tab Quản lý
            btnNv.style.display = 'none';
            btnQl.style.display = 'inline-block';
            switchTab('quan-ly');
            window.warehouseTheme?.setRole(data);
        } else {
            document.getElementById('user-info').innerText = `Xin chào: ${data.ho_ten} (Nhân viên Kho)`;
            
            // Ẩn nút Quản lý, chỉ chừa tab Nhân viên
            btnQl.style.display = 'none';
            btnNv.style.display = 'inline-block';
            switchTab('nhan-vien');
            window.warehouseTheme?.setRole(data);
        }
    } else {
        window.warehouseTheme?.closeDrawer();
        window.warehouseTheme?.closeManagerDrawer();
        document.getElementById('login-container').style.display = 'flex';
        document.getElementById('main-app').style.display = 'none';
    }
}
