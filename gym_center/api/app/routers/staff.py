"""Staff endpoints for Iron Việt Fitness."""
from fastapi import APIRouter
from ..core import *  # shared models, database and knowledge-base helpers

router = APIRouter()

@router.get('/staff/requests',tags=['Nội bộ nhân viên'],summary='Danh sách yêu cầu chờ xử lý')
def staff_requests(status:str|None='pending_review',request_type:str|None=None,limit:int=100):
    sql='SELECT * FROM requests WHERE 1=1'; args=[]
    if status: sql+=' AND status=?'; args.append(status)
    if request_type: sql+=' AND request_type=?'; args.append(request_type)
    with conn() as c: rows=c.execute(sql+' ORDER BY created_at DESC LIMIT ?',args+[max(1,min(limit,500))]).fetchall()
    return {'count':len(rows),'items':[dict(x) for x in rows]}


@router.post('/staff/requests/{code}/decision',tags=['Nội bộ nhân viên'],summary='Duyệt/từ chối yêu cầu hội viên')
def staff_decision(code:str,decision:str=Query(...,pattern='^(approved|rejected|completed)$'),note:str|None=None):
    with conn() as c:
        r=c.execute('SELECT * FROM requests WHERE code=?',(code,)).fetchone()
        if not r: raise HTTPException(404,'Không tìm thấy yêu cầu')
        c.execute('UPDATE requests SET status=?,detail=COALESCE(detail,"") || ? WHERE code=?',(decision,(' | '+note) if note else '',code))
    return {'request_code':code,'status':decision,'note':note}


@router.post('/staff/orders/{code}/payment',tags=['Nội bộ nhân viên'],summary='Ghi nhận thanh toán đăng ký gói')
def record_payment(code:str,body:PaymentIn):
    with conn() as c:
        m=c.execute('SELECT 1 FROM members WHERE member_id=?',(body.member_id,)).fetchone()
        s=c.execute('SELECT * FROM memberships WHERE code=? AND member_id=?',(code,body.member_id)).fetchone()
        if not m or not s: raise HTTPException(404,'Không tìm thấy hội viên/đăng ký')
        pay='PAY'+uuid.uuid4().hex[:8].upper(); c.execute('INSERT INTO payments VALUES(?,?,?,?,?,?,?)',(pay,body.member_id,code,body.amount_vnd,body.method,'paid',datetime.now().isoformat()))
        c.execute('UPDATE memberships SET status="active" WHERE code=?',(code,))
    return {'payment_code':pay,'related_code':code,'amount_vnd':body.amount_vnd,'status':'paid','membership_status':'active'}


