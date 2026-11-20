// Giao diện B3: tra cứu, lọc và phiếu nhập/xuất; gọi API Flask b3.py, b4.py.
let b3Catalog = [];
let b3LookupRequest = 0;

function updateB3StockPreview() {
    const book = b3Catalog.find(s => s.ma_sach === document.getElementById('phieu-sach')?.value);
    const mode = document.getElementById('phieu-loai')?.value || 'nhap';
    const amountRaw = document.getElementById('phieu-sl')?.value || '';
    const quantity = Number(amountRaw);
    const stock = book ? Number(book.so_luong_ton) || 0 : null;
    const validQty = amountRaw !== '' && Number.isSafeInteger(quantity) && quantity > 0;
    const future = stock === null ? null : (validQty ? stock + (mode === 'nhap' ? quantity : -quantity) : stock);
    const format = value => value === null ? '—' : value.toLocaleString('vi-VN');
    const current = document.getElementById('b3-stock-current');
    const after = document.getElementById('b3-stock-after');
    const title = document.getElementById('b3-stock-action');
    const warning = document.getElementById('b3-stock-warning');
    const total = document.getElementById('b3-import-total');
    if (current) current.textContent = format(stock);
    if (after) after.textContent = format(future);
    if (title) title.textContent = mode === 'nhap' ? 'Dự kiến sau nhập' : 'Dự kiến sau xuất';
    if (warning) {
        let error = '';
        if (amountRaw !== '' && !validQty) error = 'Số lượng phải là số nguyên dương.';
        else if (validQty && mode === 'xuat' && stock !== null && quantity > stock) error = `Không đủ tồn kho: còn ${format(stock)}, yêu cầu ${format(quantity)}.`;
        warning.textContent = error;
        warning.hidden = !error;
    }
    if (total) {
        const priceRaw = document.getElementById('phieu-gia')?.value || '';
        const price = Number(priceRaw);
        const show = mode === 'nhap' && validQty && priceRaw !== '' && Number.isFinite(price) && price >= 0;
        total.hidden = !show;
        total.textContent = show ? 'Thành tiền dự kiến: ' + (price * quantity).toLocaleString('vi-VN') + ' đ' : '';
    }
}

async function loadSachNhanVien() {
    const currentRequest = ++b3LookupRequest;
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
    if (currentRequest !== b3LookupRequest) return;
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



async function loadSachSelect() {
    const res = await fetch('/api/sach');
    if(!res.ok) return;
    const data = await res.json();
    if (!Array.isArray(data)) return;
    b3Catalog = data;
    const select = document.getElementById('phieu-sach');
    const selectedMaSach = select.value;
    select.replaceChildren();
    for (const s of data) {
        select.add(new Option(`${s.ten_sach} (Tồn: ${s.so_luong_ton})`, s.ma_sach));
    }
    if (Array.from(select.options).some(option => option.value === selectedMaSach)) {
        select.value = selectedMaSach;
    }
    updateB3StockPreview();
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
    updateB3StockPreview();
}

function todayLocalISO() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

async function submitPhieu() {
    const loai = document.getElementById('phieu-loai').value;
    const maSach = document.getElementById('phieu-sach').value;
    const soLuong = Number(document.getElementById('phieu-sl').value);
    
    if (!maSach || !Number.isSafeInteger(soLuong) || soLuong <= 0) { alert('Chọn sách và nhập số lượng nguyên dương!'); return; }
    
    const selected = b3Catalog.find(book => book.ma_sach === maSach);
    if (loai === 'xuat' && selected && soLuong > Number(selected.so_luong_ton)) {
        alert(`Sách không đủ tồn: còn ${selected.so_luong_ton}, cần ${soLuong}.`);
        return;
    }
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
        if(res.ok) { alert(result.message); loadSachNhanVien(); loadSachSelect(); window.warehouseTheme?.refreshMetrics(); window.warehouseTheme?.closeDrawer(); }
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
        if(res.ok) { alert(result.message); loadSachNhanVien(); loadSachSelect(); window.warehouseTheme?.refreshMetrics(); window.warehouseTheme?.closeDrawer(); }
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
        if (window.warehouseTheme) {
            window.warehouseTheme.openDrawer('nhap');
            return;
        }
        traCuuSec.style.display = 'none';
        lapPhieuSec.style.display = 'block';
        loadSachSelect();
    }
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
