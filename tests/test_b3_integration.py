"""HTTP integration tests for the actual Flask routes, on a temporary DB copy."""
from contextlib import closing
import importlib.util
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec('flask') and importlib.util.find_spec('flask_sqlalchemy'),
                     'Cần cài requirements.txt để kiểm thử HTTP Flask.')
class B3IntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.path = Path(cls.temp.name) / 'bookstore.db'
        shutil.copy2(ROOT / 'bookstore.db', cls.path)
        old = os.environ.get('BOOKSTORE_DB_PATH')
        os.environ['BOOKSTORE_DB_PATH'] = str(cls.path)
        sys.path.insert(0, str(ROOT))
        try:
            from app import app, db, init_db
        finally:
            sys.path.pop(0)
            if old is None:
                os.environ.pop('BOOKSTORE_DB_PATH', None)
            else:
                os.environ['BOOKSTORE_DB_PATH'] = old
        cls.app = app
        cls.db = db
        with app.app_context():
            assert Path(db.engine.url.database).resolve() == cls.path.resolve(), 'Không được kiểm thử trên DB gốc!'
        cls.addClassCleanup(cls.dispose_db)
        app.config['TESTING'] = True
        init_db()

    @classmethod
    def dispose_db(cls):
        with cls.app.app_context():
            cls.db.session.remove()
            cls.db.engine.dispose()

    def setUp(self):
        self.client = self.app.test_client()
        self.role('staff')

    def role(self, role):
        with self.client.session_transaction() as sess:
            sess.clear()
            if role:
                sess.update(user=role, role=role, ho_ten='Test')

    def stock(self):
        with closing(sqlite3.connect(self.path)) as con:
            return con.execute("SELECT so_luong_ton FROM sach WHERE ma_sach='S001'").fetchone()[0]

    def receipt_count(self, table, column, code):
        with closing(sqlite3.connect(self.path)) as con:
            return con.execute(f'SELECT COUNT(*) FROM {table} WHERE {column}=?', (code,)).fetchone()[0]

    def imp(self, code='TEST-B3-PN', qty=2, price=100, **extra):
        return dict(ma_phieu_nhap=code, ngay_nhap='2026-11-26', ma_ncc='NCC01',
                    chi_tiet=[dict(ma_sach='S001', so_luong_nhap=qty, don_gia_nhap=price)], **extra)

    def exp(self, code='TEST-B3-PX', quantities=(2,)):
        return dict(ma_phieu_xuat=code, ngay_xuat='2026-11-26', nguoi_nhan='Test', ly_do='Test',
                    chi_tiet=[dict(ma_sach='S001', so_luong_xuat=q) for q in quantities])

    def test_route_registration(self):
        expected = {('/api/sach', 'GET'): 'b4.get_sach',
                    ('/api/phieu-nhap', 'POST'): 'b3.create_phieu_nhap',
                    ('/api/phieu-xuat', 'POST'): 'b3.create_phieu_xuat',
                    ('/api/phieu-xuat', 'GET'): 'b3.get_phieu_xuat',
                    ('/api/phieu-nhap', 'GET'): 'b4.get_phieu_nhap'}
        for (path, method), endpoint in expected.items():
            rules = [r.endpoint for r in self.app.url_map.iter_rules() if r.rule == path and method in r.methods]
            self.assertEqual(rules, [endpoint])
        self.assertEqual(self.client.get('/').status_code, 200)

    def test_lookup(self):
        r = self.client.get('/api/sach?min_price=80000&max_price=100000')
        self.assertEqual(r.status_code, 200)
        self.assertEqual({s['ma_sach'] for s in r.json}, {'S001','S002','S011','S012','S013','S014','S015'})
        self.assertEqual([s['ma_sach'] for s in self.client.get('/api/sach?q=S001').json], ['S001'])
        for query in ['min_price=nan','max_price=-1','min_price=100000&max_price=80000','min_price=abc']:
            self.assertEqual(self.client.get('/api/sach?' + query).status_code, 400)
        r = self.client.get('/api/sach?ncc=NCC01&sort=gia')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(all(s['ma_ncc']=='NCC01' for s in r.json))
        self.assertEqual([s['gia_ban'] for s in r.json], sorted(s['gia_ban'] for s in r.json))

    def test_invalid_import(self):
        before = self.stock()
        cases = [self.imp(qty=q) for q in (0,-1,1.5,True)] + [self.imp(price=p) for p in (-1,1e100)]
        cases += [[], {**self.imp(), 'chi_tiet': []}, {**self.imp(), 'ngay_nhap': 'bad'},
                  {**self.imp(), 'ma_ncc': 'INVALID'}, self.imp(code='A'*21),
                  {**self.imp(), 'chi_tiet': [self.imp()['chi_tiet'][0], dict(ma_sach='INVALID',so_luong_nhap=1,don_gia_nhap=1)]}]
        for payload in cases:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post('/api/phieu-nhap',json=payload).status_code,400)
                self.assertEqual(self.stock(),before)
        self.assertEqual(self.receipt_count('phieu_nhap','ma_phieu_nhap','TEST-B3-PN'),0)

    def test_invalid_export(self):
        before = self.stock()
        cases = [self.exp(quantities=q) for q in [(0,),(-1,),(1.5,),(True,),(),(before+1,), (before,before)]]
        cases += [{**self.exp(), 'ngay_xuat':'bad'}, {**self.exp(), 'nguoi_nhan': 'A'*101}]
        for payload in cases:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post('/api/phieu-xuat',json=payload).status_code,400)
                self.assertEqual(self.stock(),before)
        self.assertEqual(self.receipt_count('phieu_xuat','ma_phieu_xuat','TEST-B3-PX'),0)

    def test_permissions(self):
        for role in (None,'manager','admin'):
            self.role(role)
            self.assertEqual(self.client.post('/api/phieu-nhap',json=self.imp()).status_code,403)
            self.assertEqual(self.client.post('/api/phieu-xuat',json=self.exp()).status_code,403)
        self.role(None)
        self.assertEqual(self.client.get('/api/sach').status_code,401)
        self.role('manager')
        self.assertEqual(self.client.get('/api/phieu-nhap').status_code,200)
        self.role('admin')
        self.assertEqual(self.client.get('/api/admin/users').status_code,200)

    def test_import_history(self):
        code = 'TEST-B3-HISTORY-PN'
        before = self.stock()
        self.assertEqual(self.client.post('/api/phieu-nhap', json=self.imp(code=code)).status_code, 201)
        try:
            r = self.client.get('/api/phieu-nhap?thang=11&nam=2026')
            self.assertEqual(r.status_code, 200)
            self.assertTrue(all(p['nguoi_lap'] == 'staff' for p in r.json))
            receipt = next(p for p in r.json if p['ma_phieu_nhap'] == code)
            self.assertEqual(receipt['chi_tiet'][0]['so_luong_nhap'], 2)
            self.assertEqual(receipt['tong_tien'], 200)
            self.assertTrue(receipt['chi_tiet'][0]['ten_sach'])
            self.assertTrue(receipt['ten_ncc'])
            self.assertNotIn(code, [p['ma_phieu_nhap'] for p in self.client.get('/api/phieu-nhap?thang=1&nam=2026').json])
            for query in ['thang=13', 'nam=0', 'thang=abc']:
                self.assertEqual(self.client.get('/api/phieu-nhap?' + query).status_code, 400)
            with self.client.session_transaction() as sess:
                sess.update(user='other-staff', role='staff')
            self.assertNotIn(code, [p['ma_phieu_nhap'] for p in self.client.get('/api/phieu-nhap').json])
            self.role('manager')
            self.assertIn(code, [p['ma_phieu_nhap'] for p in self.client.get('/api/phieu-nhap').json])
            self.role('admin')
            self.assertEqual(self.client.get('/api/phieu-nhap').status_code, 403)
            self.role(None)
            self.assertEqual(self.client.get('/api/phieu-nhap').status_code, 401)
            self.assertEqual(self.stock(), before + 2)
        finally:
            with self.app.app_context():
                from models import PhieuNhap, Sach
                receipt = self.db.session.get(PhieuNhap, code)
                if receipt is not None:
                    self.db.session.delete(receipt)
                    self.db.session.get(Sach, 'S001').so_luong_ton = before
                    self.db.session.commit()

    def test_export_history(self):
        before = self.stock()
        code = 'TEST-B3-HISTORY-PX'
        self.assertEqual(self.client.post('/api/phieu-xuat', json=self.exp(code=code)).status_code, 201)
        try:
            r = self.client.get('/api/phieu-xuat?thang=11&nam=2026')
            self.assertEqual(r.status_code, 200)
            self.assertTrue(all(p['nguoi_lap'] == 'staff' for p in r.json))
            receipt = next(p for p in r.json if p['ma_phieu_xuat'] == code)
            self.assertEqual(receipt['chi_tiet'][0]['so_luong_xuat'], 2)
            self.assertTrue(receipt['chi_tiet'][0]['ten_sach'])
            self.assertNotIn(code, [p['ma_phieu_xuat'] for p in self.client.get('/api/phieu-xuat?thang=1&nam=2026').json])
            for query in ['thang=13', 'nam=0', 'thang=abc']:
                self.assertEqual(self.client.get('/api/phieu-xuat?' + query).status_code, 400)
            with self.client.session_transaction() as sess:
                sess.update(user='other-staff', role='staff')
            self.assertNotIn(code, [p['ma_phieu_xuat'] for p in self.client.get('/api/phieu-xuat').json])
            self.role('manager')
            self.assertIn(code, [p['ma_phieu_xuat'] for p in self.client.get('/api/phieu-xuat').json])
            self.role('admin')
            self.assertEqual(self.client.get('/api/phieu-xuat').status_code, 403)
            self.role(None)
            self.assertEqual(self.client.get('/api/phieu-xuat').status_code, 401)
            self.assertEqual(self.stock(), before - 2)
        finally:
            # Hoàn tác giao dịch thử nghiệm trên bản sao để các test khác độc lập.
            with self.app.app_context():
                from models import PhieuXuat, Sach
                receipt = self.db.session.get(PhieuXuat, code)
                if receipt is not None:
                    self.db.session.delete(receipt)
                    self.db.session.get(Sach, 'S001').so_luong_ton = before
                    self.db.session.commit()

    def test_valid_transactions(self):
        before = self.stock()
        payload = self.imp(code='TEST-B3-OK-PN')
        self.assertEqual(self.client.post('/api/phieu-nhap',json=payload).status_code,201)
        self.assertEqual(self.stock(),before+2)
        self.assertEqual(self.client.post('/api/phieu-nhap',json=payload).status_code,400)
        self.assertEqual(self.stock(),before+2)
        payload = self.exp(code='TEST-B3-OK-PX',quantities=(1,1))
        self.assertEqual(self.client.post('/api/phieu-xuat',json=payload).status_code,201)
        self.assertEqual(self.stock(),before)
        self.assertEqual(self.client.post('/api/phieu-xuat',json=payload).status_code,400)
        self.assertEqual(self.stock(),before)
        self.assertEqual(self.receipt_count('phieu_nhap','ma_phieu_nhap','TEST-B3-OK-PN'),1)
        self.assertEqual(self.receipt_count('phieu_xuat','ma_phieu_xuat','TEST-B3-OK-PX'),1)
        with closing(sqlite3.connect(self.path)) as con:
            self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(),[])


if __name__ == '__main__':
    unittest.main(verbosity=2)
