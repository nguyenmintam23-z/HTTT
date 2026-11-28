"""Tests extracted handler bodies against a real in-memory SQLAlchemy SQLite session.
Does not import Flask; verifies core route logic, NOT Flask integration or JS UI.
"""
import ast
import json
from datetime import date
from decimal import Decimal, DecimalException
from math import isfinite
from pathlib import Path
from types import SimpleNamespace
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()
class NhaCungCap(Base):
  __tablename__='nha_cung_cap'
  ma_ncc=Column(String,primary_key=True)
class Sach(Base):
  __tablename__='sach'
  ma_sach=Column(String,primary_key=True)
  ten_sach=Column(String)
  the_loai=Column(String)
  gia_ban=Column(Float)
  ma_ncc=Column(String)
  so_luong_ton=Column(Integer)
  def to_dict(self):return {'ma_sach':self.ma_sach,'ten_sach':self.ten_sach,'gia_ban':self.gia_ban,'so_luong_ton':self.so_luong_ton}
class PhieuNhap(Base):
  __tablename__='phieu_nhap'
  ma_phieu_nhap=Column(String,primary_key=True)
  ngay_nhap=Column(String)
  ma_ncc=Column(String)
  nguoi_lap=Column(String)
  tong_tien=Column(Float)
  chi_tiet=relationship('ChiTietPhieuNhap',cascade='all,delete-orphan')
class ChiTietPhieuNhap(Base):
  __tablename__='chi_tiet_phieu_nhap'
  id=Column(Integer,primary_key=True,autoincrement=True)
  ma_phieu_nhap=Column(String,ForeignKey('phieu_nhap.ma_phieu_nhap'))
  ma_sach=Column(String)
  so_luong_nhap=Column(Integer)
  don_gia_nhap=Column(Float)
  thanh_tien=Column(Float)
class PhieuXuat(Base):
  __tablename__='phieu_xuat'
  ma_phieu_xuat=Column(String,primary_key=True)
  ngay_xuat=Column(String)
  nguoi_nhan=Column(String)
  ly_do=Column(String)
  nguoi_lap=Column(String)
  chi_tiet=relationship('ChiTietPhieuXuat',cascade='all,delete-orphan')
class ChiTietPhieuXuat(Base):
  __tablename__='chi_tiet_phieu_xuat'
  id=Column(Integer,primary_key=True,autoincrement=True)
  ma_phieu_xuat=Column(String,ForeignKey('phieu_xuat.ma_phieu_xuat'))
  ma_sach=Column(String)
  so_luong_xuat=Column(Integer)

engine=create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
sess=Session(engine)
sess.add_all([NhaCungCap(ma_ncc='NCC02'),Sach(ma_sach='S002',ten_sach='Python',the_loai='IT',gia_ban=90000,ma_ncc='NCC02',so_luong_ton=15),Sach(ma_sach='S001',ten_sach='Toán',the_loai='Tài liệu',gia_ban=75000,ma_ncc='NCC02',so_luong_ton=25)]);sess.commit()
Sach.query=sess.query(Sach)
role={'user':'staff','role':'staff','ho_ten':'Tester'}
req=SimpleNamespace(args={},body={},is_json=True)
req.get_json=lambda silent=False: req.body
req.get_data=lambda as_text=True: json.dumps(req.body)
ctx={'db':SimpleNamespace(session=sess), 'Sach':Sach, 'NhaCungCap':NhaCungCap,'PhieuNhap':PhieuNhap,'PhieuXuat':PhieuXuat,'ChiTietPhieuNhap':ChiTietPhieuNhap,'ChiTietPhieuXuat':ChiTietPhieuXuat,'request':req,'session':role,'date':date,'Decimal':Decimal,'DecimalException':DecimalException,'json':json,'isfinite':isfinite,'jsonify':lambda x:x,'SQLAlchemyError':SQLAlchemyError}
root = Path(__file__).resolve().parents[1]
source = chr(10).join((root / name).read_text(encoding='utf8') for name in ('app.py', 'b3.py', 'b4.py'))
for node in ast.parse(source).body:
  if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in ('MAX_STOCK', 'MAX_MONEY') for target in node.targets):
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'b3.py', 'exec'), ctx)
  if isinstance(node,ast.FunctionDef) and node.name in ('get_sach','create_phieu_nhap','create_phieu_xuat'):
    node.decorator_list=[]
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'app.py','exec'),ctx)

def call(name,body,code):
  req.body=body
  res=ctx[name]()
  if isinstance(res,tuple): message,status=res
  else: message,status=res,200
  assert status==code,(name,status,code,message)
  return message

def stock(code='S002'):
  return sess.get(Sach,code).so_luong_ton

def imp(pid,lines,**kw):
  return {'ma_phieu_nhap':pid,'ngay_nhap':'2026-11-18','ma_ncc':'NCC02','chi_tiet':lines,**kw}
def iml(code='S002',qty=5,price=60000):
  return {'ma_sach':code,'so_luong_nhap':qty,'don_gia_nhap':price}
def exp(pid,lines,**kw):
  return {'ma_phieu_xuat':pid,'ngay_xuat':'2026-11-18','nguoi_nhan':'KT','ly_do':'Demo','chi_tiet':lines,**kw}
def exl(code='S002',qty=3):
  return {'ma_sach':code,'so_luong_xuat':qty}

checks=0
def check(condition, explanation):
  global checks
  assert condition,explanation
  checks+=1

req.args={'min_price':'80000','max_price':'100000'}
lst=ctx['get_sach']();check(len(lst)==1 and lst[0]['ma_sach']=='S002','price filter')
req.args={'min_price':'100000','max_price':'80000'};check(ctx['get_sach']()[1]==400,'reverse price filter')
req.args={'min_price':'nan'};check(ctx['get_sach']()[1]==400,'nonfinite price')
req.args={'min_price':'-100'};check(ctx['get_sach']()[1]==400,'negative price')
req.args={}
call('create_phieu_nhap',None,400);check(stock()==15,'missing JSON')
call('create_phieu_nhap',imp('PN1',[]),400);check(stock()==15,'empty details')
call('create_phieu_nhap',imp('PN1',[iml(qty=-5)]),400);check(stock()==15,'negative import')
call('create_phieu_nhap',imp('PN1',[iml(qty=0)]),400);check(stock()==15,'zero import')
call('create_phieu_nhap',imp('PN1',[iml(price=-3)]),400);check(stock()==15,'negative cost')
call('create_phieu_nhap',imp('PN1',[iml(price=12.345)]),400);check(stock()==15,'reject more than two decimals')
call('create_phieu_nhap',imp('PN1',[iml(price=float('inf'))]),400);check(stock()==15,'inf cost')
call('create_phieu_nhap',imp('PN1',[iml(code='NOT_EXIST')]),400);check(stock()==15,'missing book')
call('create_phieu_nhap',{**imp('PN1',[iml()]),'ma_ncc':'FAKE'},400);check(stock()==15,'missing supplier')
call('create_phieu_nhap', {**imp('PN1',[iml()]),'ngay_nhap':'2026-2-3'},400);check(stock()==15,'invalid date format')
call('create_phieu_nhap',imp('PN1',[iml(),iml(qty=0)]),400);check(stock()==15,'no partial commit for invalid line')
call('create_phieu_nhap',imp('PN1',[iml(qty=5)]),201);check(stock()==20,'valid import 15 to 20')
check(sess.query(PhieuNhap).count()==1,'saved import')
call('create_phieu_nhap',imp('PN1',[iml(qty=3)]),400);check(stock()==20,'duplicate import')
call('create_phieu_xuat',exp('PX1',[exl(qty=3)]),201);check(stock()==17,'valid export 20 to 17')
call('create_phieu_xuat',exp('PX2',[exl(qty=18)]),400);check(stock()==17,'oversell')
call('create_phieu_xuat',exp('PX2',[exl(qty=9),exl(qty=9)]),400);check(stock()==17,'oversell duplicate lines')
call('create_phieu_xuat',exp('PX2',[exl(qty=-2)]),400);check(stock()==17,'negative export')
call('create_phieu_xuat',exp('PX2',[exl(qty=0)]),400);check(stock()==17,'zero export')
call('create_phieu_xuat',exp('PX2',[exl(qty=1),exl('INVALID',qty=1)]),400);check(stock()==17,'no partial export when invalid row')
call('create_phieu_xuat',exp('PX2',[exl(qty=3),exl(qty=2)]),201);check(stock()==12,'valid duplicate lines')
check(sess.query(ChiTietPhieuXuat).count()==3,'saved details')
call('create_phieu_xuat',exp('PX2',[exl(qty=1)]),400);check(stock()==12,'duplicate export')
role['role']='manager';call('create_phieu_nhap',imp('PN3',[iml()]),403);call('create_phieu_xuat',exp('PX3',[exl()]),403);check(stock()==12,'role authorization')
print('PASS',checks,'checks with real SQLite session + SQLAlchemy mapped test models, routes extracted; Flask UI not covered.')
