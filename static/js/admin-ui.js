/* Admin UI: dữ liệu thực từ /api/admin/users và /api/admin/positions.
   API và phân quyền phía server giữ nguyên. */
(() => {
  'use strict';
  let state = {users: [], positions: []};
  let returnFocus = null;
  let toastTimeout = null;
  const get = id => document.getElementById(id);

  function showSection(section = 'overview') {
    if (get('main-app')?.dataset.role !== 'admin') return;
    const sections = ['overview', 'users', 'positions'];
    if (!sections.includes(section)) section = 'overview';
    sections.forEach(name => {
      const el = get(`admin-${name}-section`);
      if (el) el.hidden = name !== section;

    });
    window.warehouseTheme.setNav('side-admin-' + section);
    const titles = {overview: 'Tổng quan quản trị', users: 'Quản lý tài khoản', positions: 'Chức vụ và phân quyền'};
    const title = get('page-title');
    if (title) title.textContent = titles[section];
    closeDrawer();
  }

  function openMetric(metric) {
    if (get('main-app')?.dataset.role !== 'admin') return;
    if (metric === 'positions') {
      get('admin-position-search').value = ''; filterPositions(); showSection('positions');
      get('admin-positions-section').scrollIntoView({block:'start',behavior:'smooth'});
    } else {
      get('admin-user-search').value = '';
      get('admin-user-filter-role').value = metric === 'all' ? '' : metric;
      filterUsers(); showSection('users'); get('admin-users-section').scrollIntoView({block:'start',behavior:'smooth'});
    }
  }
  function updateStats(users, positions) {
    const managerCount = users.filter(u => u.role === 'manager').length;
    const staffCount = users.filter(u => u.role === 'staff').length;
    const total = managerCount + staffCount;
    const count = (id, value) => { const el = get(id); if (el) el.textContent = value.toLocaleString('vi-VN'); };
    count('admin-kpi-total', total);
    count('admin-kpi-managers', managerCount);
    count('admin-kpi-staff', staffCount);
    count('admin-kpi-positions', positions.length);
    count('admin-role-manager-count', managerCount);
    count('admin-role-staff-count', staffCount);
    const managerBar = get('admin-role-manager-bar');
    const staffBar = get('admin-role-staff-bar');
    if (managerBar) managerBar.style.width = `${total ? managerCount / total * 100 : 0}%`;
    if (staffBar) staffBar.style.width = `${total ? staffCount / total * 100 : 0}%`;
    const posCount = get('admin-position-count');
    if (posCount) posCount.textContent = `${positions.length} chức vụ`;
  }

  function prettifyTable() {
    const body = document.querySelector('#table-admin-users tbody');
    if (body) {
      [...body.rows].forEach(row => {
        if (row.cells.length < 5) return;
        const cell = row.cells[2];
        if (!cell.querySelector('.admin-role-badge')) {
          const value = cell.textContent.trim();
          cell.replaceChildren();
          const label = document.createElement('span');
          label.className = `admin-role-badge ${value === 'Quản lý kho' ? 'manager' : 'staff'}`;
          label.textContent = value;
          cell.append(label);
        }
        row.cells[4]?.classList.add('admin-row-actions');
      });
    }
    const posBody = document.querySelector('#table-admin-positions tbody');
    if (posBody) [...posBody.rows].forEach(row => row.cells[2]?.classList.add('admin-row-actions'));
  }

  function filterUsers() {
    const search = (get('admin-user-search')?.value || '').trim().toLocaleLowerCase('vi');
    const selectedRole = get('admin-user-filter-role')?.value || '';
    const body = document.querySelector('#table-admin-users tbody');
    if (!body) return;
    let shown = 0;
    [...body.rows].forEach(row => {
      if (row.cells.length < 5) return;
      const text = [...row.cells].slice(0, 4).map(cell => cell.textContent).join(' ').toLocaleLowerCase('vi');
      const role = row.cells[2].textContent.includes('Quản lý kho') ? 'manager' : 'staff';
      const visible = (!search || text.includes(search)) && (!selectedRole || role === selectedRole);
      row.hidden = !visible;
      if (visible) shown++;
    });
    const el = get('admin-user-filter-count');
    if (el) el.textContent = `Hiển thị ${shown} / ${state.users.length} tài khoản`;
  }

  function filterPositions() {
    const search = (get('admin-position-search')?.value || '').trim().toLocaleLowerCase('vi');
    const body = document.querySelector('#table-admin-positions tbody');
    if (!body) return;
    [...body.rows].forEach(row => {
      if (row.cells.length < 3) return;
      row.hidden = !row.cells[0].textContent.toLocaleLowerCase('vi').includes(search);
    });
  }

  function resetFilters() {
    if (get('admin-user-search')) get('admin-user-search').value = '';
    if (get('admin-user-filter-role')) get('admin-user-filter-role').value = '';
    filterUsers();
  }

  function render(data) {
    if (!data || !Array.isArray(data.users) || !Array.isArray(data.positions)) return;
    state = {users: data.users, positions: data.positions};
    updateStats(state.users, state.positions);
    prettifyTable();
    filterUsers();
    filterPositions();
  }

  function openDrawer(type, editing = false) {
    if (get('main-app')?.dataset.role !== 'admin') return;
    if (!['user', 'position'].includes(type)) return;
    const drawer = get('admin-drawer');
    if (!drawer) return;
    returnFocus = document.activeElement;
    get('admin-user-form-wrap').hidden = type !== 'user';
    get('admin-position-form-wrap').hidden = type !== 'position';
    get('admin-drawer-title').textContent = type === 'user'
      ? (editing ? 'Chỉnh sửa tài khoản' : 'Thêm tài khoản nhân viên')
      : (editing ? 'Chỉnh sửa chức vụ' : 'Thêm chức vụ');
    get('admin-drawer-desc').textContent = type === 'user'
      ? 'Thông tin tài khoản được lưu vào cơ sở dữ liệu của hệ thống.'
      : 'Cập nhật danh mục chức vụ sử dụng trong tài khoản nhân viên.';
    get('admin-password-hint').textContent = editing
      ? 'Để trống nếu không muốn thay đổi mật khẩu.'
      : 'Mật khẩu mới phải có ít nhất 6 ký tự.';
    get('admin-password-star').hidden = editing;
    drawer.hidden = false;
    document.body.classList.add('admin-drawer-open');
    const focus = type === 'user' ? get('admin-user-name') : get('admin-position-name');
    focus?.focus();
  }

  function openUserDrawer() {
    get('form-admin-user')?.reset();
    openDrawer('user', false);
  }
  function openPositionDrawer() {
    get('form-admin-position')?.reset();
    openDrawer('position', false);
  }
  function closeDrawer() {
    const el = get('admin-drawer');
    if (el?.hidden) return;
    if (el) el.hidden = true;
    document.body.classList.remove('admin-drawer-open');
    if (returnFocus?.isConnected) returnFocus.focus();
    returnFocus = null;
  }

  function toast(message, variant = 'success') {
    const el = get('admin-toast');
    if (!el) return;
    el.textContent = message;
    el.className = `admin-toast ${variant}`;
    el.hidden = false;
    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => { el.hidden = true; }, 4400);
  }

  document.addEventListener('DOMContentLoaded', () => {
    get('admin-user-search')?.addEventListener('input', filterUsers);
    get('admin-user-filter-role')?.addEventListener('change', filterUsers);
    get('admin-position-search')?.addEventListener('input', filterPositions);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !get('admin-drawer')?.hidden) closeDrawer();
    });
  });

  window.adminUI = {openMetric, showSection, render, openDrawer, openUserDrawer, openPositionDrawer,
    closeDrawer, toast, resetFilters};
})();
