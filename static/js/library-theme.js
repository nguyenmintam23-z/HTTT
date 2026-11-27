/* Giao diện tham khảo từ Figma Make; nghiệp vụ tiếp tục dùng API Flask hiện có. */
(function () {
  let drawer = null;
  let formSection = null;
  let managerDrawer = null;
  let managerForms = {};
  let stockSummaryBooks = [], stockSummaryRequest = 0;
  const stockEl = id => document.getElementById(id);
  const stockNumber = n => Number(n).toLocaleString('vi-VN');
  const stockRole = () => stockEl('main-app').dataset.role;
  const stockAllowed = () => ['staff', 'manager'].includes(stockRole());
  const stockGroup = (book, field) => String(book[field] ?? '').trim() || 'Chưa xác định';

  function hideStockDetail() {
    stockEl('stock-summary-detail').hidden = true;
    stockEl('stock-summary-detail-rows').replaceChildren();
    stockEl('stock-summary-detail-title').textContent = '';
    stockEl('stock-summary-rows').querySelectorAll('button').forEach(button => button.setAttribute('aria-expanded','false'));
  }
  function closeStockSummary() {
    ++stockSummaryRequest;
    stockSummaryBooks = [];
    const dialog = stockEl('stock-summary-dialog');
    if (dialog.open) dialog.close();
    stockEl('stock-summary-data').hidden = true;
    stockEl('stock-summary-rows').replaceChildren();
    hideStockDetail();
    stockEl('stock-summary-total').textContent = '—';
    stockEl('stock-summary-caption').textContent = '';
    stockEl('stock-summary-status').textContent = '';
    stockEl('stock-summary-refresh').disabled = false;
  }
  function openStockSummary() {
    if (!stockAllowed()) return;
    const dialog = stockEl('stock-summary-dialog');
    if (dialog.open) return;
    stockEl('stock-summary-group').value = 'the_loai';
    dialog.showModal();
    refreshStockSummary();
  }
  async function refreshStockSummary() {
    const dialog = stockEl('stock-summary-dialog');
    if (!dialog.open || !stockAllowed()) return;
    const request = ++stockSummaryRequest;
    const role = stockRole();
    const current = () => request === stockSummaryRequest && dialog.open && stockRole() === role;
    const status = stockEl('stock-summary-status');
    stockSummaryBooks = [];
    stockEl('stock-summary-data').hidden = true;
    stockEl('stock-summary-refresh').disabled = true;
    hideStockDetail();
    status.textContent = 'Đang tải dữ liệu tồn kho…';
    try {
      const res = await fetch('/api/sach', {cache:'no-store'});
      if (!res.ok) throw new Error('Không thể tải dữ liệu.');
      const books = await res.json();
      if (!Array.isArray(books) || books.some(book => !book || book.so_luong_ton == null || book.so_luong_ton === '' || !Number.isSafeInteger(Number(book.so_luong_ton)) || Number(book.so_luong_ton) < 0)) throw new Error('Dữ liệu tồn kho không hợp lệ.');
      if (!current()) return;
      stockSummaryBooks = books;
      updateBookMetrics(books);
      renderStockSummary();
      stockEl('stock-summary-data').hidden = false;
      status.textContent = 'Cập nhật lúc ' + new Date().toLocaleTimeString('vi-VN');
    } catch (error) {
      if (current()) status.textContent = 'Không thể tải tồn kho. Vui lòng bấm Làm mới để thử lại.';
    } finally {
      if (current()) stockEl('stock-summary-refresh').disabled = false;
    }
  }
  function renderStockSummary() {
    if (!stockAllowed() || !stockEl('stock-summary-dialog').open) return;
    hideStockDetail();
    const field = stockEl('stock-summary-group').value === 'vi_tri' ? 'vi_tri' : 'the_loai';
    const groups = new Map();
    let total = 0;
    for (const book of stockSummaryBooks) {
      const name = stockGroup(book, field), qty = Number(book.so_luong_ton);
      if (!groups.has(name)) groups.set(name, {name, books:[], qty:0});
      const group = groups.get(name);
      group.books.push(book); group.qty += qty; total += qty;
    }
    stockEl('stock-summary-total').textContent = stockNumber(total);
    stockEl('stock-summary-caption').textContent = stockNumber(stockSummaryBooks.length) + ' đầu sách · ' + stockNumber(groups.size) + (field === 'vi_tri' ? ' vị trí' : ' thể loại');
    stockEl('stock-summary-group-heading').textContent = field === 'vi_tri' ? 'Vị trí lưu trữ' : 'Thể loại';
    const body = stockEl('stock-summary-rows');
    body.replaceChildren();
    if (!groups.size) {
      const cell = body.insertRow().insertCell(); cell.colSpan = 4; cell.textContent = 'Chưa có dữ liệu sách.';
      return;
    }
    for (const group of [...groups.values()].sort((a,b) => b.qty - a.qty || a.name.localeCompare(b.name,'vi'))) {
      const row = body.insertRow();
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'stock-summary-group-link'; button.textContent = group.name;
      button.setAttribute('aria-controls','stock-summary-detail'); button.setAttribute('aria-expanded','false');
      button.onclick = () => {
        const wasOpen = button.getAttribute('aria-expanded') === 'true';
        hideStockDetail();
        if (wasOpen) return;
        button.setAttribute('aria-expanded','true');
        stockEl('stock-summary-detail-title').textContent = group.name + ' · ' + stockNumber(group.qty) + ' cuốn';
        const detail = stockEl('stock-summary-detail-rows');
        for (const book of [...group.books].sort((a,b) => Number(b.so_luong_ton) - Number(a.so_luong_ton) || String(a.ten_sach ?? '').localeCompare(String(b.ten_sach ?? ''),'vi'))) {
          const r = detail.insertRow();
          for (const value of [book.ma_sach, book.ten_sach, stockGroup(book,'vi_tri'), stockNumber(book.so_luong_ton)]) r.insertCell().textContent = value ?? '';
        }
        stockEl('stock-summary-detail').hidden = false;
        stockEl('stock-summary-detail').scrollIntoView({block:'nearest'});
      };
      row.insertCell().append(button);
      row.insertCell().textContent = stockNumber(group.books.length);
      row.insertCell().textContent = stockNumber(group.qty);
      const percent = total ? group.qty / total * 100 : 0;
      const cell = row.insertCell();
      const label = document.createElement('span'); label.textContent = percent.toLocaleString('vi-VN',{maximumFractionDigits:1}) + '%';
      const bar = document.createElement('div'); bar.className = 'stock-summary-bar'; bar.setAttribute('aria-hidden','true');
      const fill = document.createElement('span'); fill.style.width = percent + '%'; bar.append(fill);
      cell.append(label,bar);
    }
  }
  stockEl('stock-summary-dialog').addEventListener('cancel', event => { event.preventDefault(); closeStockSummary(); });


  function setNav(active) {
    document.querySelectorAll('.sidebar-nav .side-link').forEach(el => {
      el.classList.toggle('active', el.id === active);
      if (el.id === active) el.setAttribute('aria-current','page');
      else el.removeAttribute('aria-current');
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
    closeStockSummary();
    const manager = session.role === 'manager';
    const admin = session.role === 'admin';
    const staff = !manager && !admin;
    const setHidden = (id, hidden) => { const el = document.getElementById(id); if (el) el.hidden = hidden; };
    setHidden('staff-side-nav', !staff);
    setHidden('manager-side-nav', !manager);
    setHidden('admin-side-nav', !admin);
    document.getElementById('sidebar-workspace-label').textContent = admin ? 'QUẢN TRỊ · ADMIN' : manager ? 'QUẢN LÝ · B4' : 'NHÂN VIÊN · B3';
    document.getElementById('main-app').dataset.role = session.role;
    document.getElementById('main-app').dataset.username = session.username || session.user || '';
    if (typeof resetVoucherSession === 'function') resetVoucherSession();
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
    panel.className = 'b3-drawer-panel voucher-panel';
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
    document.getElementById('voucher-date').value = todayLocalISO();
    document.getElementById('voucher-creator').value = document.getElementById('sidebar-user-name').textContent;
    drawer.hidden = false;
    document.body.classList.add('drawer-open');
    setNav('side-staff-voucher');
    if (typeof window.loadSachSelect === 'function') window.loadSachSelect();
    if (typeof window.loadNCCSelect === 'function') window.loadNCCSelect();
    const first = document.getElementById(mode === 'nhap' ? 'pn-ma' : 'px-ma');
    if (first) first.focus({preventScroll:true});
    drawer.querySelector('.b3-drawer-panel').scrollTop = 0;
  }
  function closeDrawer(force = false) {
    if (typeof b3Submitting !== 'undefined' && b3Submitting && force !== true) return;
    if (drawer) drawer.hidden = true;
    document.body.classList.remove('drawer-open');
    if (document.getElementById('main-app').dataset.role === 'staff') {
      const activeTab = document.querySelector('.tab-content.active')?.id;
      setNav(activeTab === 'tab-export-history' ? 'side-staff-history' : activeTab === 'tab-import-history' ? 'side-staff-import' : 'side-staff-lookup');
    }
  }
  function setMode(mode) {
    const select = document.getElementById('phieu-loai');
    if (!select) return;
    if (typeof b3Submitting !== 'undefined' && b3Submitting) return;
    if (select.value !== mode && typeof clearVoucherEntry === 'function') clearVoucherEntry();
    select.value = mode;
    if (typeof window.togglePhieuForm === 'function') window.togglePhieuForm();
    document.getElementById('mode-nhap')?.classList.toggle('active', mode === 'nhap');
    document.getElementById('mode-xuat')?.classList.toggle('active', mode === 'xuat');
    const submit = document.querySelector('.drawer-submit');
    if (submit) submit.textContent = mode === 'nhap' ? 'Lưu phiếu nhập' : 'Lưu phiếu xuất';
    const heading = document.querySelector('#staff-lap-phieu-section .drawer-heading h3');
    if (heading) heading.textContent = mode === 'nhap' ? 'Thêm phiếu nhập kho' : 'Thêm phiếu xuất kho';
    document.querySelector('.voucher-card').dataset.mode = mode;
    document.getElementById('voucher-subtitle').textContent = mode === 'nhap' ? 'Ghi nhận hàng nhập và cập nhật tồn kho.' : 'Ghi nhận bàn giao sách và kiểm tra tồn kho.';
    if (typeof renderVoucherDraft === 'function') renderVoucherDraft();
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
    ['search-keyword', 'filter-ncc', 'sort-select', 'filter-min-price', 'filter-max-price', 'filter-stock'].forEach(id => {
      const el = document.getElementById(id); if (el) el.value = '';
    });
    if (typeof window.loadSachNhanVien === 'function') window.loadSachNhanVien();
  }
  function openMetric(metric) {
    const role = document.getElementById('main-app').dataset.role;
    if (!['staff', 'manager'].includes(role) || !['books', 'stock', 'low'].includes(metric)) return;
    const set = (id, value = '') => { document.getElementById(id).value = value; };
    if (metric === 'stock') return openStockSummary();
    const sort = metric === 'low' ? 'ton-asc' : '';
    const stock = metric === 'low' ? 'low' : '';
    if (role === 'staff') {
      ['search-keyword','filter-ncc','filter-min-price','filter-max-price'].forEach(id => set(id));
      set('sort-select', sort); set('filter-stock', stock); switchStaffSubTab('tra-cuu');
    } else {
      set('ql-sach-search'); set('ql-sach-sort', sort); set('ql-sach-stock', stock); bookPage = 1;
      switchManagerSubTab('sach');
    }
    const target = document.getElementById(role === 'staff' ? 'staff-tra-cuu-section' : 'mgr-sach-section');
    target?.scrollIntoView({block:'start', behavior:'smooth'});
  }
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && drawer && !drawer.hidden) closeDrawer();
    if (event.key === 'Escape' && managerDrawer && !managerDrawer.hidden) closeManagerDrawer();
  });
  window.warehouseTheme = { openMetric, closeStockSummary, refreshStockSummary, renderStockSummary, hideStockDetail, setNav, openDrawer, closeDrawer, closeManagerDrawer, setMode, clearFilters, setRole, updateBookMetrics, updateSupplierMetrics, refreshMetrics, openManagerDrawer };
})();
