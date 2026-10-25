"""Shared data access, models and business helpers for Iron Việt Fitness API."""
from __future__ import annotations


import csv, json, os, sqlite3, uuid


from datetime import date, datetime, timedelta


from pathlib import Path


from typing import Optional


from fastapi import FastAPI, HTTPException, Query


from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[2]


KB = ROOT / 'knowledge_base'


DB_PATH = Path(os.getenv('GYM_DB_PATH', str(ROOT / 'api' / 'gym_center.db')))


def read_csv(name):
    with (KB / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def conn():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    sql_dir = ROOT / 'api' / 'sql'
    schema_path = sql_dir / 'schema.sql'
    seed_path = sql_dir / 'seed.sql'
    with conn() as c:
        # Keep the SQL files as the canonical, inspectable database definition.
        c.executescript(schema_path.read_text(encoding='utf-8'))
        if seed_path.exists():
            c.executescript(seed_path.read_text(encoding='utf-8'))
        if c.execute('SELECT COUNT(*) FROM members').fetchone()[0] == 0:
            first=['An','Bình','Chi','Dũng','Giang','Hà','Hải','Hạnh','Hiếu','Hoàng','Hùng','Khánh','Lan','Linh','Long','Mai','Minh','Nam','Ngọc','Phúc','Quân','Thảo','Trang','Trung','Vy']
            last=['Nguyễn','Trần','Lê','Phạm','Hoàng','Huỳnh','Phan','Võ','Đặng','Bùi']
            goals=['Tăng cơ','Giảm cân','Cải thiện sức bền','Tăng độ linh hoạt','Duy trì sức khỏe']
            plans=read_csv('membership_plans.csv')
            for i in range(1,121):
                mid=f'MB{i:04d}'; full=f'{last[(i-1)%len(last)]} {first[(i*3)%len(first)]} {first[(i*7+2)%len(first)]}'
                phone=f'09{i:08d}'; email=f'member{i:03d}@example.com'; branch='quan-7' if i%2 else 'quan-4'; plan=plans[(i-1)%len(plans)]
                joined=(date(2025,1,1)+timedelta(days=i*3)).isoformat()
                c.execute('INSERT INTO members VALUES(?,?,?,?,?,?,?,?,?)',(mid,full,phone,email,branch,goals[i%len(goals)],'active' if i%13 else 'suspended',plan['plan_id'],joined))
                start=date(2026,1,1)+timedelta(days=i%250); end=start+timedelta(days=int(plan['duration_days']))
                c.execute('INSERT INTO memberships VALUES(?,?,?,?,?,?,?,?)',(f'MS{i:04d}',mid,plan['plan_id'],start.isoformat(),end.isoformat(),'active' if i%9 else 'expired',int(plan['price_vnd']),int(plan['auto_renew'].lower()=='yes')))
            schedules=read_csv('class_schedule.csv'); coaches=read_csv('pt_coaches.csv')
            for i in range(1,181):
                member=f'MB{((i*7)%120)+1:04d}'; dt=datetime(2026,10,21,6,0)+timedelta(hours=(i%14)*1.25,days=i%14)
                if i%3:
                    activity=schedules[(i-1)%len(schedules)]; typ='class'; aid=activity['class_id']; coach=next((x['coach_id'] for x in coaches if x['full_name']==activity['coach_name']),coaches[i%len(coaches)]['coach_id']); branch=activity['branch']
                else:
                    coachrow=coaches[i%len(coaches)]; typ='pt'; aid=f'PTSESSION{i:04d}'; coach=coachrow['coach_id']; branch=coachrow['branch']
                c.execute('INSERT INTO bookings VALUES(?,?,?,?,?,?,?,?,?)',(f'BK{i:04d}',member,typ,aid,coach,branch,dt.isoformat(),'confirmed' if i%11 else 'cancelled',0 if typ=='class' else 400000))
            for i in range(1,121):
                member=f'MB{i:04d}'; c.execute('INSERT INTO payments VALUES(?,?,?,?,?,?,?)',(f'PAY{i:04d}',member,f'MS{i:04d}',800000+(i%5)*100000,'bank_transfer' if i%2 else 'card','paid' if i%10 else 'pending',(date(2026,1,1)+timedelta(days=i)).isoformat()))


class MemberIn(BaseModel):
    full_name:str; phone:str; email:str|None=None; branch:str='quan-7'; goal:str='Duy trì sức khỏe'; plan_id:str='MON01'


class BookingIn(BaseModel):
    member_id:str; activity_type:str=Field(pattern='^(class|pt)$'); activity_id:str; coach_id:str|None=None; branch:str; start_at:datetime


class RequestIn(BaseModel):
    member_id:str; reason:str; detail:str|None=None


class PaymentIn(BaseModel):
    member_id:str; related_code:str; amount_vnd:int=Field(gt=0); method:str='bank_transfer'


def create_request(body:RequestIn,typ:str):
    with conn() as c:
        if not c.execute('SELECT 1 FROM members WHERE member_id=?',(body.member_id,)).fetchone(): raise HTTPException(404,'Không tìm thấy hội viên')
        code='RQ'+uuid.uuid4().hex[:8].upper(); c.execute('INSERT INTO requests VALUES(?,?,?,?,?,?,?)',(code,body.member_id,typ,body.reason,'pending_review',datetime.now().isoformat(),body.detail))
    return {'request_code':code,'request_type':typ,'status':'pending_review','message':'Đã ghi nhận; nhân viên sẽ xét duyệt theo chính sách liên quan.'}


