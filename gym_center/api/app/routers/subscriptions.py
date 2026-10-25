"""Subscriptions endpoints for Iron Việt Fitness."""
from fastapi import APIRouter
from ..core import *  # shared models, database and knowledge-base helpers
from .orders import lookup_order, reschedule_order, cancel_order

router = APIRouter()

@router.get('/subscriptions/plans',tags=['Gói hội viên'],summary='Danh sách gói tập')
def subscription_plans(): return {'count':len(read_csv('membership_plans.csv')),'items':read_csv('membership_plans.csv')}


@router.get('/subscriptions/{code}',tags=['Gói hội viên'],summary='Tra gói hội viên theo mã đăng ký')
def subscription_lookup(code:str,member_id:str|None=None): return lookup_order(code,member_id)


@router.post('/subscriptions/{code}/pause',tags=['Gói hội viên'],summary='Gửi yêu cầu bảo lưu thẻ tập')
def pause_subscription(code:str,member_id:str,days:int=Query(...,ge=1,le=90),reason:str='travel'):
    with conn() as c:
        r=c.execute('SELECT * FROM memberships WHERE code=? AND member_id=?',(code,member_id)).fetchone()
        if not r: raise HTTPException(404,'Không tìm thấy gói hội viên')
        if r['status']!='active': raise HTTPException(409,'Chỉ gói đang hoạt động mới được yêu cầu bảo lưu')
        req='RQ'+uuid.uuid4().hex[:8].upper(); c.execute('INSERT INTO requests VALUES(?,?,?,?,?,?,?)',(req,member_id,'freeze',reason,'pending_review',datetime.now().isoformat(),json.dumps({'membership_code':code,'days':days})))
    return {'request_code':req,'status':'pending_review','message':'Yêu cầu bảo lưu cần nhân viên xác nhận theo policy_membership_terms.md.'}


@router.post('/subscriptions/{code}/resume',tags=['Gói hội viên'],summary='Gửi yêu cầu tiếp tục thẻ đang bảo lưu')
def resume_subscription(code:str,member_id:str):
    with conn() as c:
        r=c.execute('SELECT * FROM memberships WHERE code=? AND member_id=?',(code,member_id)).fetchone()
        if not r: raise HTTPException(404,'Không tìm thấy gói hội viên')
        if r['status']!='paused': raise HTTPException(409,'Gói tập không ở trạng thái paused')
        c.execute('UPDATE memberships SET status="active" WHERE code=?',(code,))
    return {'code':code,'status':'active'}


@router.post('/subscriptions/{code}/reschedule',tags=['Gói hội viên'],summary='Đổi ngày bắt đầu gói chưa kích hoạt')
def subscription_reschedule(code:str,start_date:date,member_id:str): return reschedule_order(code,start_date,member_id)


@router.post('/subscriptions/{code}/cancel',tags=['Gói hội viên'],summary='Yêu cầu hủy gói và xem trước khoản hoàn')
def subscription_cancel(code:str,member_id:str,dry_run:bool=True): return cancel_order(code,member_id,dry_run)


