"""SQLite tests: seed, integrity, schema constraints and existing-DB guards."""
from contextlib import closing
from pathlib import Path
import sqlite3
import unittest
import ast

ROOT = Path(__file__).resolve().parents[1]

class DatabaseSeedTest(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(':memory:')
        self.addCleanup(self.con.close)
        self.con.executescript((ROOT/'database.sql').read_text(encoding='utf-8'))

    def test_integrity_and_demo(self):
        self.assertEqual(self.con.execute('PRAGMA integrity_check').fetchone(), ('ok',))
        self.assertEqual(self.con.execute('PRAGMA foreign_key_check').fetchall(), [])
        for table, count in [('chuc_vu',3),('nguoi_dung',3),('nha_cung_cap',6),('sach',23),
                             ('phieu_nhap',3),('phieu_xuat',1),('chi_tiet_phieu_nhap',6),('chi_tiet_phieu_xuat',1)]:
            self.assertEqual(self.con.execute(f'SELECT count(*) FROM {table}').fetchone()[0],count)
        self.assertEqual(self.con.execute('SELECT sum(so_luong_ton) FROM sach').fetchone()[0],554)
        self.assertEqual(self.con.execute('SELECT count(*) FROM phieu_nhap WHERE nguoi_lap IS NULL').fetchone()[0],0)
        self.assertEqual(self.con.execute('SELECT count(*) FROM nguoi_dung WHERE length(session_version)<>32').fetchone()[0],0)
        self.assertEqual(self.con.execute("SELECT count(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'").fetchone()[0],8)

    def test_integer_constraints(self):
        for table,column,invalid in [('sach','so_luong_ton',1.5),('sach','so_luong_ton',-1),
                                      ('chi_tiet_phieu_nhap','so_luong_nhap',1.5),('chi_tiet_phieu_xuat','so_luong_xuat',0)]:
            with self.subTest(table=table,value=invalid), self.assertRaises(sqlite3.IntegrityError):
                self.con.execute(f'UPDATE {table} SET {column}=?',(invalid,))

    def test_existing_db_guards(self):
        # Run actual migration guard function independently of Flask using SQLite.
        tree = ast.parse((ROOT/'models.py').read_text(encoding='utf-8'))
        nodes = [node for node in tree.body if (isinstance(node,ast.FunctionDef) and node.name=='ensure_sqlite_guards') or
                 (isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('SQLITE_INDEXES','SQLITE_INTEGER_RULES') for t in node.targets))]
        ns={}; exec(compile(ast.Module(body=nodes,type_ignores=[]),'models.py','exec'),ns)
        class Connection:
            def __init__(self,con): self.con=con
            def exec_driver_sql(self,sql):
                class Result:
                    def __init__(self,cursor): self.cursor=cursor
                    def first(self): return self.cursor.fetchone()
                return Result(self.con.execute(sql))
        with closing(sqlite3.connect(':memory:')) as old, closing(sqlite3.connect(ROOT/'bookstore.db')) as src:
            src.backup(old)
            old.execute('PRAGMA foreign_keys=ON')
            before=old.execute('SELECT * FROM sach ORDER BY ma_sach').fetchall()
            ns['ensure_sqlite_guards'](Connection(old))
            ns['ensure_sqlite_guards'](Connection(old))
            self.assertEqual(old.execute('SELECT * FROM sach ORDER BY ma_sach').fetchall(),before)
            with self.assertRaises(sqlite3.IntegrityError): old.execute('UPDATE sach SET so_luong_ton=1.5')
            with self.assertRaises(sqlite3.IntegrityError): old.execute('UPDATE chi_tiet_phieu_nhap SET so_luong_nhap=1.5')
            self.assertEqual(old.execute('PRAGMA foreign_key_check').fetchall(),[])
