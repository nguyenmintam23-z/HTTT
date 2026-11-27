"""Test ORM and actual admin/auth function bodies with real SQLite; not HTTP tests."""
import ast
import hmac
import re
import secrets
from functools import wraps
from pathlib import Path
from types import SimpleNamespace
import unittest

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship, Session

ROOT = Path(__file__).resolve().parents[1]


def source_nodes(filename, predicate, env):
    tree = ast.parse((ROOT / filename).read_text(encoding='utf-8'))
    nodes = [n for n in tree.body if predicate(n)]
    for n in nodes:
        if isinstance(n, ast.FunctionDef): n.decorator_list = []
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec'), env)


class AdminLogicTest(unittest.TestCase):
    def setUp(self):
        Base = declarative_base()
        engine = sa.create_engine('sqlite:///:memory:')
        @sa.event.listens_for(engine, 'connect')
        def fk(conn, record): conn.execute('PRAGMA foreign_keys=ON')
        self.addCleanup(engine.dispose)
        db = SimpleNamespace(Model=Base, relationship=relationship,
                             **{n:getattr(sa,n) for n in ('Column','String','Integer','Numeric','Date','ForeignKey','CheckConstraint','Index','text')})
        env = {'db':db}
        source_nodes('models.py', lambda n: isinstance(n, ast.ClassDef) or (isinstance(n,ast.ImportFrom) and n.module in ('datetime','secrets')), env)
        Base.metadata.create_all(engine)
        self.db = db
        db.session = Session(engine)
        self.addCleanup(db.session.close)
        self.User, self.Position = env['NguoiDung'],env['ChucVu']
        self.User.query = db.session.query(self.User)
        self.Position.query = db.session.query(self.Position)
        db.session.add_all([self.Position(ten_chuc_vu='Quản lý kho'), self.Position(ten_chuc_vu='Nhân viên kho')]); db.session.flush()
        self.user = self.User(username='manager',role='manager',password='hash-test',chuc_vu='Quản lý kho',ho_ten='Test')
        db.session.add(self.user); db.session.commit()
        self.req = SimpleNamespace(path='/api/sach',endpoint='b4.add_sach',body={})
        self.req.get_json=lambda silent=True:self.req.body
        self.session = {}
        self.routes={}
        class BP:
            def __init__(bp,*args): pass
            def route(bp,*args,**kwargs):
                def deco(f): self.routes[f.__name__]=f; return f
                return deco
        self.env = dict(env,app=SimpleNamespace(secret_key='test-only'), hmac=hmac, session=self.session,
                        request=self.req,jsonify=lambda data:data,Blueprint=BP,wraps=wraps,re=re,
                        token_hex=secrets.token_hex,generate_password_hash=lambda x:'test-hash-'+x,
                        check_password_hash=lambda h,p:h=='test-hash-'+p)
        source_nodes('app.py',lambda n:isinstance(n,ast.FunctionDef) and n.name in ('auth_stamp','validate_session','login'),self.env)
        source_nodes('admin.py',lambda n:isinstance(n,ast.FunctionDef) and n.name=='create_admin_blueprint',self.env)
        self.env['create_admin_blueprint'](db,self.User,self.Position)

    def test_revocation_on_role_change_and_delete(self):
        self.session.update(user='manager',role='manager',auth_stamp=self.env['auth_stamp'](self.user))
        self.assertIsNone(self.env['validate_session']())
        self.user.role='staff'; self.user.session_version=secrets.token_hex(16); self.db.session.commit()
        self.assertEqual(self.env['validate_session']()[1],401)
        self.assertEqual(self.session,{})
        self.session.update(user='manager',role='staff',auth_stamp=self.env['auth_stamp'](self.user))
        self.db.session.delete(self.user); self.db.session.commit()
        self.assertEqual(self.env['validate_session']()[1],401)
        self.assertEqual(self.session,{})

    def test_rename_used_position(self):
        self.session.update(role='admin')
        self.req.body={'ten_chuc_vu':'Điều phối kho'}
        self.assertIn('message',self.routes['update_admin_position']('Quản lý kho'))
        self.assertEqual(self.db.session.get(self.User,'manager').chuc_vu,'Điều phối kho')
        self.assertIsNone(self.db.session.get(self.Position,'Quản lý kho'))
        self.assertEqual(self.db.session.execute(sa.text('PRAGMA foreign_key_check')).fetchall(),[])

    def test_login_invalid_payload(self):
        for body in ([],{}, {'username': 'manager', 'password': None}, {'username':4,'password':'123456'}):
            self.req.body=body
            self.assertEqual(self.env['login']()[1],400)

    def test_model_indexes_and_integer_constraint(self):
        indexes=self.db.session.execute(sa.text("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'" )).fetchall()
        self.assertEqual(len(indexes),8)
        self.db.session.add(self.env['NhaCungCap'](ma_ncc='N1',ten_ncc='Test')); self.db.session.flush()
        self.db.session.add(self.env['Sach'](ma_sach='S1',ten_sach='Test',ma_ncc='N1',so_luong_ton=1.5))
        with self.assertRaises(sa.exc.IntegrityError): self.db.session.commit()
        self.db.session.rollback()
