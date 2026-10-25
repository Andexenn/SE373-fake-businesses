"""Payments endpoints for Iron Việt Fitness."""
from fastapi import APIRouter
from ..core import *  # shared models, database and knowledge-base helpers

router = APIRouter()

@router.get('/payments',tags=['Thanh toán'],summary='Tra cứu lịch sử thanh toán')
def payments(member_id:str|None=None,status:str|None=None,limit:int=100):
    sql='SELECT * FROM payments WHERE 1=1'; args=[]
    if member_id: sql+=' AND member_id=?'; args.append(member_id)
    if status: sql+=' AND status=?'; args.append(status)
    with conn() as c: rows=c.execute(sql+' ORDER BY created_at DESC LIMIT ?',args+[max(1,min(limit,500))]).fetchall()
    return {'count':len(rows),'items':[dict(x) for x in rows]}


