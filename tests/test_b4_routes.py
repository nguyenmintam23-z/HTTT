"""B4 regression checks through actual Flask routes and a copy of the demo database."""
from contextlib import closing
import importlib.util
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class B4RoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        directory = Path(cls.folder.name)
        for name in ('app.py', 'b4.py', 'b3.py', 'admin.py', 'models.py'):
            shutil.copy(ROOT / name, directory / name)
        cls.database = directory / 'bookstore.db'
        # SQLite backup also includes committed WAL transactions.
        with closing(sqlite3.connect(ROOT / 'bookstore.db')) as source:
            with closing(sqlite3.connect(cls.database)) as target:
                source.backup(target)
        spec = importlib.util.spec_from_file_location('b4_test_app', directory / 'app.py')
        cls.module = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(directory))
        spec.loader.exec_module(cls.module)
        cls.app = cls.module.app
        cls.app.config['TESTING'] = True
        cls.module.init_db()
        from sqlalchemy import event
        with cls.app.app_context():
            cls.engine = cls.module.db.engine
            cls.engine.dispose()
            @event.listens_for(cls.engine, 'connect')
            def enable_fk(connection, _):
                connection.execute('PRAGMA foreign_keys=ON')
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            cls.module.db.session.remove()
            cls.engine.dispose()
        sys.path.remove(cls.folder.name)
        cls.folder.cleanup()

    def setUp(self):
        from werkzeug.security import generate_password_hash
        with self.app.app_context():
            for username in ('manager', 'staff'):
                user = self.module.db.session.get(self.module.NguoiDung, username)
                user.password = generate_password_hash('b4-test-password')
            self.module.db.session.commit()
        response = self.client.post('/api/login', json={
            'username': 'manager', 'password': 'b4-test-password'
        })
        self.assertEqual(response.status_code, 200)

    def test_01_registered_routes_and_search(self):
        matches = [r for r in self.app.url_map.iter_rules()
                   if r.rule == '/api/sach' and 'GET' in r.methods]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].endpoint, 'b4.get_sach')
        response = self.client.get('/api/sach?q=S001')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['ma_sach'], 'S001')
        rows = self.client.get('/api/sach?min_price=80000&max_price=100000').json
        self.assertTrue(rows)
        self.assertTrue(all(80000 <= row['gia_ban'] <= 100000 for row in rows))
        for query in ('min_price=-1', 'min_price=nan', 'min_price=10&max_price=1'):
            self.assertEqual(self.client.get('/api/sach?' + query).status_code, 400)

    def test_login_and_combined_filters(self):
        from werkzeug.security import generate_password_hash
        with self.app.app_context():
            user = self.module.db.session.get(self.module.NguoiDung, 'manager')
            user.password = generate_password_hash('b4-test-password')
            self.module.db.session.commit()
        with self.client.session_transaction() as session:
            session.clear()
        response = self.client.post('/api/login', json={
            'username':'manager', 'password':'b4-test-password'
        })
        self.assertEqual(response.status_code, 200)
        for order in ('ten', 'gia'):
            rows = self.client.get('/api/sach?q=S&ncc=NCC01&sort=' + order).json
            self.assertTrue(rows)
            self.assertTrue(all(row['ma_ncc']=='NCC01' for row in rows))
            if order == 'gia':
                self.assertEqual([r['gia_ban'] for r in rows],
                                 sorted(r['gia_ban'] for r in rows))

    def test_02_invalid_payloads(self):
        invalid_books = [
            [], {}, {'ma_sach':'X', 'ten_sach':'Test', 'ma_ncc':'MISSING'},
            {'ma_sach':'X', 'ten_sach':'Test', 'ma_ncc':'NCC01', 'so_luong_ton':-1},
            {'ma_sach':'X', 'ten_sach':'Test', 'ma_ncc':'NCC01', 'so_luong_ton':1.5},
            {'ma_sach':'X', 'ten_sach':'Test', 'ma_ncc':'NCC01', 'so_luong_ton':True},
            {'ma_sach':'X', 'ten_sach':'Test', 'ma_ncc':'NCC01', 'unexpected':1},
            {'ma_sach':'X', 'ten_sach':'Test', 'ma_ncc':'NCC01', 'gia_ban':-1},
        ]
        for payload in invalid_books:
            with self.subTest(payload=payload):
                response = self.client.post('/api/sach', json=payload)
                self.assertEqual(response.status_code, 400, response.json)
        for payload in ([], {'ma_ncc':'X', 'ten_ncc':' '},
                        {'ma_ncc':'X', 'ten_ncc':'Test', 'email':'bad'},
                        {'ma_ncc':'X', 'ten_ncc':'Test', 'so_dien_thoai':'bad'}):
            self.assertEqual(self.client.post('/api/ncc', json=payload).status_code, 400)

        for phone in ('------', '((((((', '1-----', '12345', '(123456'):
            response = self.client.post('/api/ncc', json={
                'ma_ncc':'BAD-PHONE', 'ten_ncc':'Test', 'so_dien_thoai':phone
            })
            self.assertEqual(response.status_code, 400, (phone, response.json))
        for payload in (
            {'ten_ncc':'x' * 101}, {'ma_ncc':'x' * 21},
            {'dia_chi':'x' * 201}, {'email':'x' * 101},
            {'so_dien_thoai':'------'}, {'unknown':'x'}
        ):
            self.assertEqual(self.client.put('/api/ncc/NCC01', json=payload).status_code, 400)
        for payload in (
            {'ten_sach':'x' * 151}, {'ma_sach':'x' * 21},
            {'gia_ban':float('nan')}, {'gia_nhap':float('inf')},
            {'gia_ban':float('-inf')}, {'so_luong_ton':1.5}, {'ma_ncc':'MISSING'}
        ):
            self.assertEqual(self.client.put('/api/sach/S001', json=payload).status_code, 400)
            create = {'ma_sach':'BAD', 'ten_sach':'Test', 'ma_ncc':'NCC01', **payload}
            self.assertEqual(self.client.post('/api/sach', json=create).status_code, 400)

    def test_price_precision_and_limits(self):
        c = self.client
        base = {'ma_sach':'PRICE-TEST', 'ten_sach':'Price test', 'ma_ncc':'NCC01'}
        self.assertEqual(c.post('/api/sach', json=base).status_code, 201)
        for field in ('gia_nhap', 'gia_ban'):
            for raw in ('10000000000000', '9999999999999.991', '9999999999999.999',
                        '1.001', '0.0001', 'NaN', 'Infinity', '-Infinity', '-0.01', 'true'):
                with self.subTest(field=field, raw=raw):
                    update = c.put('/api/sach/PRICE-TEST', data='{"' + field + '":' + raw + '}', content_type='application/json')
                    self.assertEqual(update.status_code, 400, update.json)
                    self.assertTrue(update.json['error'])
                    create = '{"ma_sach":"BAD-PRICE","ten_sach":"Test","ma_ncc":"NCC01","' + field + '":' + raw + '}'
                    self.assertEqual(c.post('/api/sach', data=create, content_type='application/json').status_code, 400)
            for raw in ('0', '0.01', '12.34', '12.340', '9999999999999.99'):
                with self.subTest(field=field, valid=raw):
                    response = c.put('/api/sach/PRICE-TEST', data='{"' + field + '":' + raw + '}', content_type='application/json')
                    self.assertEqual(response.status_code, 200, response.json)
        self.assertEqual(c.delete('/api/sach/PRICE-TEST').status_code, 200)

    def test_03_crud_and_referenced_deletion(self):
        c = self.client
        supplier = {'ma_ncc':'TEST-NCC', 'ten_ncc':'Test supplier'}
        self.assertEqual(c.post('/api/ncc', json=supplier).status_code, 201)
        self.assertEqual(c.put('/api/ncc/TEST-NCC', json={'dia_chi':'Updated'}).status_code, 200)
        book = {'ma_sach':'TEST-BOOK', 'ten_sach':'Test book', 'ma_ncc':'TEST-NCC', 'so_luong_ton':2}
        self.assertEqual(c.post('/api/sach', json=book).status_code, 201)
        self.assertEqual(c.post('/api/sach', json=book).status_code, 409)
        self.assertEqual(c.delete('/api/ncc/TEST-NCC').status_code, 409)
        self.assertEqual(c.delete('/api/sach/TEST-BOOK').status_code, 200)
        self.assertEqual(c.delete('/api/ncc/TEST-NCC').status_code, 200)
        receipt = c.get('/api/phieu-nhap').json[0]
        code = receipt['chi_tiet'][0]['ma_sach']
        self.assertEqual(c.delete('/api/sach/' + code).status_code, 409)
        self.assertEqual(c.delete('/api/ncc/' + receipt['ma_ncc']).status_code, 409)

        export_book = {'ma_sach':'EXPORT-ONLY', 'ten_sach':'Export only', 'ma_ncc':'NCC01'}
        self.assertEqual(c.post('/api/sach', json=export_book).status_code, 201)
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute('PRAGMA foreign_keys=ON')
            connection.execute("INSERT INTO phieu_xuat(ma_phieu_xuat,ngay_xuat) VALUES('B4-EXPORT-ONLY','2026-09-20')")
            connection.execute("INSERT INTO chi_tiet_phieu_xuat(ma_phieu_xuat,ma_sach,so_luong_xuat) VALUES('B4-EXPORT-ONLY','EXPORT-ONLY',1)")
            connection.commit()
        self.assertEqual(c.delete('/api/sach/EXPORT-ONLY').status_code, 409)

    def test_04_rename_references(self):
        c = self.client
        receipt = c.get('/api/phieu-nhap').json[0]
        old = receipt['chi_tiet'][0]['ma_sach']
        before = next(b for b in c.get('/api/sach').json if b['ma_sach'] == old)
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute('PRAGMA foreign_keys=ON')
            connection.execute("INSERT INTO phieu_xuat(ma_phieu_xuat,ngay_xuat) VALUES('B4-TEST-EXPORT','2026-09-20')")
            connection.execute("INSERT INTO chi_tiet_phieu_xuat(ma_phieu_xuat,ma_sach,so_luong_xuat) VALUES('B4-TEST-EXPORT',?,1)", (old,))
            connection.commit()
        response = c.put('/api/sach/' + old, json={'ma_sach':' TEST-RENAMED '})
        self.assertEqual(response.status_code, 200, response.json)
        after = c.get('/api/phieu-nhap').json
        self.assertTrue(any(i['ma_sach']=='TEST-RENAMED' for p in after for i in p['chi_tiet']))
        with closing(sqlite3.connect(self.database)) as db:
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(db.execute("SELECT ma_sach FROM chi_tiet_phieu_xuat WHERE ma_phieu_xuat='B4-TEST-EXPORT'").fetchone()[0], 'TEST-RENAMED')
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        renamed = next(b for b in c.get('/api/sach').json if b['ma_sach']=='TEST-RENAMED')
        self.assertEqual(renamed['so_luong_ton'], before['so_luong_ton'])
        other = next(b['ma_sach'] for b in c.get('/api/sach').json if b['ma_sach']!='TEST-RENAMED')
        self.assertEqual(c.put('/api/sach/TEST-RENAMED', json={'ma_sach':other}).status_code, 409)
        self.assertEqual(c.put('/api/sach/TEST-RENAMED', json={'ma_sach':old}).status_code, 200)

    def test_05_history_and_permissions(self):
        c = self.client
        response = c.get('/api/phieu-nhap?thang=09&nam=2026')
        self.assertEqual(response.status_code, 200)
        receipt = next(p for p in response.json if p['ma_phieu_nhap']=='PN-DEMO-02')
        self.assertEqual(len(receipt['chi_tiet']), 2)
        self.assertEqual(receipt['tong_tien'], 473000)
        self.assertEqual(c.get('/api/phieu-nhap?thang=13').status_code, 400)
        for year in ('1', '20', '202', '0000', '0202', '10000', '202a'):
            self.assertEqual(c.get('/api/phieu-nhap?nam=' + year).status_code, 400)
        for year in ('1000', '2026', '9999', ''):
            self.assertEqual(c.get('/api/phieu-nhap?nam=' + year).status_code, 200)
        self.assertEqual(c.get('/api/phieu-nhap?nam=9999').json, [])
        self.assertEqual(c.post('/api/login', json={
            'username':'staff', 'password':'b4-test-password'
        }).status_code, 200)
        self.assertEqual(c.post('/api/sach', json={}).status_code, 403)
        self.assertEqual(c.get('/api/phieu-nhap').status_code, 200)


if __name__ == '__main__':
    unittest.main()
