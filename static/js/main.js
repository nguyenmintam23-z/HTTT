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

async function loadSachNhanVien() {
    const params = new URLSearchParams({
        q: document.getElementById('search-keyword').value,
        ncc: document.getElementById('filter-ncc').value,
        sort: document.getElementById('sort-select').value
    });
    const minPrice = document.getElementById('filter-min-price').value.trim();
    const maxPrice = document.getElementById('filter-max-price').value.trim();
    if (minPrice) params.set('min_price', minPrice);
    if (maxPrice) params.set('max_price', maxPrice);

    const res = await fetch('/api/sach?' + params.toString());
    const data = await res.json();
    const tbody = document.querySelector('#table-nv-sach tbody');
    tbody.replaceChildren();
    if (!res.ok) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 7;
        cell.textContent = data.error || 'Không thể tải danh sách sách.';
        return;
    }
    for (const sach of data) {
        const row = tbody.insertRow();
        const values = [
            sach.ma_sach, sach.ten_sach, sach.the_loai, sach.tac_gia,
            (sach.gia_ban ?? 0).toLocaleString('vi-VN') + ' đ',
            sach.so_luong_ton, sach.vi_tri || ''
        ];
        for (const value of values) row.insertCell().textContent = value ?? '';
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
    const selectedMaSach = select.value;
    select.replaceChildren();
    for (const s of data) {
        select.add(new Option(`${s.ten_sach} (Tồn: ${s.so_luong_ton})`, s.ma_sach));
    }
    if (Array.from(select.options).some(option => option.value === selectedMaSach)) {
        select.value = selectedMaSach;
    }
}

function togglePhieuForm() {
    const loai = document.getElementById('phieu-loai').value;
    if(loai === 'nhap') {
        document.getElementById('nhap-fields').style.display = 'block';
        document.getElementById('xuat-fields').style.display = 'none';
        document.getElementById('phieu-gia-wrapper').style.display = 'block';
    } else {
        document.getElementById('nhap-fields').style.display = 'none';
        document.getElementById('xuat-fields').style.display = 'block';
        document.getElementById('phieu-gia-wrapper').style.display = 'none';
    }
}

function todayLocalISO() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

async function submitPhieu() {
    const loai = document.getElementById('phieu-loai').value;
    const maSach = document.getElementById('phieu-sach').value;
    const soLuong = Number(document.getElementById('phieu-sl').value);
    
    if (!maSach || !Number.isInteger(soLuong) || soLuong <= 0) { alert('Chọn sách và nhập số lượng nguyên dương!'); return; }
    
    if(loai === 'nhap') {
        const maPhieu = document.getElementById('pn-ma').value.trim();
        const maNCC = document.getElementById('pn-ncc').value;
        const inputGia = document.getElementById('phieu-gia').value.trim();
        const donGia = Number(inputGia);
        if (!inputGia || !Number.isFinite(donGia) || donGia < 0) {
            alert('Đơn giá nhập phải là số không âm!'); return;
        }
        if (!maNCC) { alert('Chọn nhà cung cấp!'); return; }
        if(!maPhieu) { alert('Nhập mã phiếu nhập!'); return; }
        
        const res = await fetch('/api/phieu-nhap', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                ma_phieu_nhap: maPhieu, ngay_nhap: todayLocalISO(),
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
                ma_phieu_xuat: maPhieu, ngay_xuat: todayLocalISO(),
                nguoi_nhan: nguoiNhan, ly_do: lyDo, chi_tiet: [{ ma_sach: maSach, so_luong_xuat: soLuong }]
            })
        });
        const result = await res.json();
        if(res.ok) { alert(result.message); loadSachNhanVien(); loadSachSelect(); }
        else { alert(result.error); }
    }
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

async function checkSession() {
    const res = await fetch('/api/check-session');
    const data = await res.json();
    if (data.logged_in) {
        document.getElementById('login-container').style.display = 'none';
        document.getElementById('main-app').style.display = 'block';
        
        await loadNCCSelect();

        const btnNv = document.getElementById('btn-nv');
        const btnQl = document.getElementById('btn-ql');

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
