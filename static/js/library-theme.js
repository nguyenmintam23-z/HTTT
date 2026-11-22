/* Giao diện tham khảo từ Figma Make; nghiệp vụ tiếp tục dùng API Flask hiện có. */
(function () {
  let drawer = null;
  let formSection = null;
  let managerDrawer = null;
  let managerForms = {};

  function setNav(active) {
    document.querySelectorAll('.sidebar-nav .side-link').forEach(el => {
      el.classList.toggle('active', el.id === active);
    });
  }
  function updateBookMetrics(items) {
    if (!Array.isArray(items)) return;
    const stock = items.reduce((sum, item) => sum + (Number(item.so_luong_ton) || 0), 0);
    const low = items.filter(item => Number(item.so_luong_ton) < 10).length;
    const set = (id, value) => { const el = document.getElementById(id); if (el) el.textContent = Number(value).toLocaleString('vi-VN'); };
    set('metric-books', items.length);
    set('metric-stock', stock);
    set('metric-low', low);
  }
  function updateSupplierMetrics(items) {
    if (!Array.isArray(items)) return;
    const el = document.getElementById('metric-suppliers');
    if (el) el.textContent = items.length.toLocaleString('vi-VN');
  }
  async function refreshMetrics() {
    try {
      const [a, b] = await Promise.all([fetch('/api/sach'), fetch('/api/ncc')]);
      if (a.ok) updateBookMetrics(await a.json());
      if (b.ok) updateSupplierMetrics(await b.json());
    } catch (err) { console.warn('Không tải được thống kê giao diện:', err); }
  }
  function setRole(session) {
    const manager = session.role === 'manager';
    const admin = session.role === 'admin';
    const staff = !manager && !admin;
    const setHidden = (id, hidden) => { const el = document.getElementById(id); if (el) el.hidden = hidden; };
    setHidden('staff-side-nav', !staff);
    setHidden('manager-side-nav', !manager);
    setHidden('admin-side-nav', !admin);
    document.getElementById('main-app').dataset.role = session.role;
    const name = session.ho_ten || session.username || 'Người dùng';
    document.getElementById('sidebar-user-name').textContent = name;
    document.getElementById('sidebar-user-role').textContent = admin ? 'Quản trị hệ thống' : manager ? 'Quản lý kho · B4' : 'Nhân viên kho · B3';
    document.getElementById('role-name').textContent = admin ? 'Quản trị hệ thống' : manager ? 'Quản lý kho (B4)' : 'Nhân viên kho (B3)';
    document.getElementById('page-title').textContent = admin ? 'Tổng quan quản trị' : manager ? 'Quản lý sách' : 'Tra cứu kho hàng';
    setNav(admin ? 'side-admin-overview' : manager ? 'side-manager-sach' : 'side-staff-lookup');
    if (manager) ensureManagerDrawer();
    else if (staff) ensureDrawer();
    if (!admin) refreshMetrics();
  }
  function ensureDrawer() {
    if (drawer) return;
    formSection = document.getElementById('staff-lap-phieu-section');
    if (!formSection) return;
    drawer = document.createElement('div');
    drawer.id = 'b3-drawer-overlay';
    drawer.className = 'b3-drawer-overlay';
    drawer.hidden = true;
    const backdrop = document.createElement('button');
    backdrop.type = 'button';
    backdrop.className = 'b3-drawer-backdrop';
    backdrop.setAttribute('aria-label', 'Đóng biểu mẫu');
    backdrop.addEventListener('click', closeDrawer);
    const panel = document.createElement('aside');
    panel.className = 'b3-drawer-panel';
    panel.setAttribute('aria-label', 'Lập phiếu nhập xuất kho');
    panel.append(formSection);
    drawer.append(backdrop, panel);
    document.body.append(drawer);
    formSection.style.display = 'block';
  }
  function openDrawer(mode = 'nhap') {
    if (document.getElementById('main-app').dataset.role !== 'staff') return;
    ensureDrawer();
    if (!drawer) return;
    setMode(mode);
    drawer.hidden = false;
    document.body.classList.add('drawer-open');
    setNav('side-staff-voucher');
    if (typeof window.loadSachSelect === 'function') window.loadSachSelect();
    const first = document.getElementById(mode === 'nhap' ? 'pn-ma' : 'px-ma');
    if (first) first.focus();
  }
  function closeDrawer() {
    if (drawer) drawer.hidden = true;
    document.body.classList.remove('drawer-open');
    const active = document.getElementById('main-app').dataset.role;
    if (active === 'staff') setNav('side-staff-lookup');
    const nv = document.getElementById('btn-sub-tra-cuu');
    const lp = document.getElementById('btn-sub-lap-phieu');
    nv?.classList.add('active'); lp?.classList.remove('active');
  }
  function setMode(mode) {
    const select = document.getElementById('phieu-loai');
    if (!select) return;
    select.value = mode;
    if (typeof window.togglePhieuForm === 'function') window.togglePhieuForm();
    document.getElementById('mode-nhap')?.classList.toggle('active', mode === 'nhap');
    document.getElementById('mode-xuat')?.classList.toggle('active', mode === 'xuat');
    const submit = document.querySelector('.drawer-submit');
    if (submit) submit.textContent = mode === 'nhap' ? 'Lưu phiếu nhập' : 'Lưu phiếu xuất';
    const heading = document.querySelector('#staff-lap-phieu-section .drawer-heading h3');
    if (heading) heading.textContent = mode === 'nhap' ? 'Thêm phiếu nhập kho' : 'Thêm phiếu xuất kho';
    if (typeof window.updateB3StockPreview === 'function') window.updateB3StockPreview();
  }
  function ensureManagerDrawer() {
    if (managerDrawer) return;
    managerDrawer = document.createElement('div');
    managerDrawer.id = 'manager-drawer-overlay';
    managerDrawer.className = 'b3-drawer-overlay manager-drawer-overlay';
    managerDrawer.hidden = true;
    const backdrop = document.createElement('button');
    backdrop.className = 'b3-drawer-backdrop';
    backdrop.setAttribute('aria-label', 'Đóng biểu mẫu quản lý');
    backdrop.onclick = closeManagerDrawer;
    const panel = document.createElement('aside');
    panel.className = 'b3-drawer-panel manager-drawer-panel';
    const heading = document.createElement('div');
    heading.className = 'manager-drawer-head';
    heading.innerHTML = '<div><small>QUẢN LÝ KHO · B4</small><h2 id="manager-drawer-title">Thêm dữ liệu</h2></div><button type="button" aria-label="Đóng">×</button>';
    heading.querySelector('button').onclick = closeManagerDrawer;
    panel.append(heading);
    for (const [key, formId] of [['sach', 'form-sach'], ['ncc', 'form-ncc']]) {
      const form = document.getElementById(formId);
      const card = form?.closest('.card');
      if (!card) continue;
      managerForms[key] = card;
      panel.append(card);
      card.hidden = true;
    }
    managerDrawer.append(backdrop, panel);
    document.body.append(managerDrawer);
  }
  function openManagerDrawer(type, fresh = false) {
    if (document.getElementById('main-app').dataset.role !== 'manager') return;
    ensureManagerDrawer();
    if (!managerDrawer || !managerForms[type]) return;
    if (fresh) {
      const form = managerForms[type].querySelector('form');
      if (form) {
        form.reset();
        if (typeof window.clearEdit === 'function') window.clearEdit(form);
      }
    }
    Object.entries(managerForms).forEach(([key, card]) => { card.hidden = key !== type; });
    document.getElementById('manager-drawer-title').textContent = (fresh ? 'Thêm ' : 'Sửa ') + (type === 'sach' ? 'sách' : 'nhà cung cấp');
    managerDrawer.hidden = false;
    document.body.classList.add('drawer-open');
  }
  function closeManagerDrawer() {
    if (managerDrawer) managerDrawer.hidden = true;
    document.body.classList.remove('drawer-open');
  }
  function clearFilters() {
    ['search-keyword', 'filter-ncc', 'sort-select', 'filter-min-price', 'filter-max-price'].forEach(id => {
      const el = document.getElementById(id); if (el) el.value = '';
    });
    if (typeof window.loadSachNhanVien === 'function') window.loadSachNhanVien();
  }
  // Keep existing B4 handlers while synchronizing left sidebar visual state.
  document.addEventListener('click', event => {
    const target = event.target.closest?.('.sidebar-nav button');
    if (!target) return;
    setNav(target.id);
    const title = document.getElementById('page-title');
    if (title && target.id.startsWith('side-manager-')) title.textContent = target.textContent.trim();
    if (title && target.id === 'side-staff-lookup') title.textContent = 'Tra cứu kho hàng';
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && drawer && !drawer.hidden) closeDrawer();
    if (event.key === 'Escape' && managerDrawer && !managerDrawer.hidden) closeManagerDrawer();
  });
  window.warehouseTheme = { openDrawer, closeDrawer, closeManagerDrawer, setMode, clearFilters, setRole, updateBookMetrics, updateSupplierMetrics, refreshMetrics, openManagerDrawer };
})();
