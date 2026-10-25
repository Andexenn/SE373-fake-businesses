"""Orders endpoints for Iron Việt Fitness."""
from fastapi import APIRouter
from ..core import *  # shared models, database and knowledge-base helpers

router = APIRouter()

@router.post('/orders/quote',tags=['Đăng ký gói'],summary='Báo giá gói tập mà không tạo đăng ký')
def quote(plan_id:str, student:bool=False):
    p=next((x for x in read_csv('membership_plans.csv') if x['plan_id']==plan_id),None)
    if not p: raise HTTPException(404,'Không tìm thấy gói tập')
    price=int(p['price_vnd']); return {'plan_id':plan_id,'plan_name':p['plan_name'],'list_price_vnd':price,'quoted_price_vnd':price,'student_verification_required':student and plan_id.startswith('STU'),'duration_days':int(p['duration_days']),'features':p['features']}


@router.post('/orders',status_code=201,tags=['Đăng ký gói'],summary='Tạo đăng ký gói tập')
def create_order(member_id:str,plan_id:str,start_date:date=Query(default_factory=date.today)):
    with conn() as c:
        m=c.execute('SELECT * FROM members WHERE member_id=?',(member_id,)).fetchone()
        p=next((x for x in read_csv('membership_plans.csv') if x['plan_id']==plan_id),None)
        if not m: raise HTTPException(404,'Không tìm thấy hội viên')
        if not p: raise HTTPException(404,'Không tìm thấy gói tập')
        code='MS'+uuid.uuid4().hex[:8].upper(); end=start_date+timedelta(days=int(p['duration_days']))
        c.execute('INSERT INTO memberships VALUES(?,?,?,?,?,?,?,?)',(code,member_id,plan_id,start_date.isoformat(),end.isoformat(),'pending_payment',int(p['price_vnd']),int(p['auto_renew'].lower()=='yes')))
    return {'code':code,'member_id':member_id,'plan_id':plan_id,'start_date':start_date,'end_date':end,'status':'pending_payment','amount_vnd':int(p['price_vnd'])}


@router.get('/orders/{code}',tags=['Đăng ký gói'],summary='Tra đăng ký gói tập')
def lookup_order(code:str,member_id:str|None=None):
    with conn() as c: r=c.execute('SELECT * FROM memberships WHERE code=?',(code,)).fetchone()
    if not r or (member_id and r['member_id']!=member_id): raise HTTPException(404,'Không tìm thấy đăng ký')
    return dict(r)


@router.post('/orders/{code}/reschedule',tags=['Đăng ký gói'],summary='Đổi ngày bắt đầu gói tập khi chưa kích hoạt')
def reschedule_order(code:str,start_date:date,member_id:str):
    with conn() as c:
        r=c.execute('SELECT * FROM memberships WHERE code=? AND member_id=?',(code,member_id)).fetchone()
        if not r: raise HTTPException(404,'Không tìm thấy đăng ký')
        if r['status']!='pending_payment': raise HTTPException(409,'Chỉ đổi ngày khi chưa thanh toán/kích hoạt')
        plan=next(x for x in read_csv('membership_plans.csv') if x['plan_id']==r['plan_id']); end=start_date+timedelta(days=int(plan['duration_days']))
        c.execute('UPDATE memberships SET start_date=?,end_date=? WHERE code=?',(start_date.isoformat(),end.isoformat(),code))
    return {'code':code,'start_date':start_date,'end_date':end,'status':'pending_payment'}


@router.post('/orders/{code}/cancel',tags=['Đăng ký gói'],summary='Hủy đăng ký gói chưa kích hoạt')
def cancel_order(code:str,member_id:str,dry_run:bool=True):
    with conn() as c:
        r=c.execute('SELECT * FROM memberships WHERE code=? AND member_id=?',(code,member_id)).fetchone()
        if not r: raise HTTPException(404,'Không tìm thấy đăng ký')
        if r['status'] not in ('pending_payment','active'): raise HTTPException(409,'Đăng ký không thể hủy ở trạng thái hiện tại')
        refund=int(r['paid_vnd']) if r['status']=='pending_payment' else 0
        if not dry_run: c.execute('UPDATE memberships SET status="cancelled" WHERE code=?',(code,))
    return {'code':code,'dry_run':dry_run,'refund_estimate_vnd':refund,'status':'cancelled' if not dry_run else r['status'],'policy_note':'Áp dụng policy_refund.md và policy_cancellation.md; trường hợp hoàn sau kích hoạt cần kiểm tra điều kiện.'}


