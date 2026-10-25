"""Requests endpoints for Iron Việt Fitness."""
from fastapi import APIRouter
from ..core import *  # shared models, database and knowledge-base helpers

router = APIRouter()

@router.post('/requests/refund',status_code=201,tags=['Yêu cầu'],summary='Ghi nhận yêu cầu hoàn tiền')
def refund_request(body:RequestIn): return create_request(body,'refund')


@router.post('/requests/exchange',status_code=201,tags=['Yêu cầu'],summary='Ghi nhận yêu cầu đổi gói/đổi lịch')
def exchange_request(body:RequestIn): return create_request(body,'exchange')


@router.post('/requests/discount',status_code=201,tags=['Yêu cầu'],summary='Ghi nhận đề xuất ưu đãi hội viên')
def discount_request(body:RequestIn): return create_request(body,'discount')


@router.post('/requests/escalate',status_code=201,tags=['Yêu cầu'],summary='Chuyển yêu cầu tới nhân viên/quản lý')
def escalate_request(body:RequestIn): return create_request(body,'escalation')


@router.get('/requests/{code}',tags=['Yêu cầu'],summary='Tra trạng thái yêu cầu')
def get_request(code:str,member_id:str|None=None):
    with conn() as c: r=c.execute('SELECT * FROM requests WHERE code=?',(code,)).fetchone()
    if not r or (member_id and r['member_id']!=member_id): raise HTTPException(404,'Không tìm thấy yêu cầu')
    return dict(r)


