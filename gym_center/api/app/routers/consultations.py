"""Consultations endpoints for Iron Việt Fitness."""
from fastapi import APIRouter
from ..core import *  # shared models, database and knowledge-base helpers

router = APIRouter()

@router.get('/consultations/availability',tags=['Lịch tập'],summary='Kiểm tra lịch lớp nhóm hoặc PT')
def consultation_availability(date_:date=Query(...,alias='date'),branch:str|None=None,activity_type:str='class'):
    if activity_type not in ('class', 'pt'):
        raise HTTPException(400, 'activity_type phải là class hoặc pt')
    with conn() as c:
        rows = c.execute(
            'SELECT activity_id, coach_id, branch, start_at, status '
            'FROM bookings WHERE substr(start_at,1,10)=? '
            'AND (? IS NULL OR branch=?) AND activity_type=? '
            'AND status="confirmed" ORDER BY start_at',
            (date_.isoformat(), branch, branch, activity_type),
        ).fetchall()
    return {'date': date_.isoformat(), 'count': len(rows), 'slots': [dict(row) for row in rows]}


@router.post('/consultations',status_code=201,tags=['Lịch tập'],summary='Đặt lịch tập lớp nhóm hoặc PT')
def create_consultation(body:BookingIn):
    with conn() as c:
        m=c.execute('SELECT * FROM members WHERE member_id=?',(body.member_id,)).fetchone()
        if not m: raise HTTPException(404,'Không tìm thấy hội viên')
        if body.start_at <= datetime.now(): raise HTTPException(422,'Thời gian đặt lịch phải ở tương lai')
        if body.activity_type=='class':
            classes=read_csv('class_schedule.csv'); cl=next((x for x in classes if x['class_id']==body.activity_id),None)
            if not cl: raise HTTPException(404,'Không tìm thấy lớp học')
            cap=int(cl['capacity']); booked=c.execute('SELECT COUNT(*) FROM bookings WHERE activity_id=? AND substr(start_at,1,10)=? AND status="confirmed"',(body.activity_id,body.start_at.date().isoformat())).fetchone()[0]
            if booked>=cap: raise HTTPException(409,'Lớp đã hết chỗ; vui lòng chọn khung giờ khác')
            coach=body.coach_id or next((x['coach_id'] for x in read_csv('pt_coaches.csv') if x['full_name']==cl['coach_name']),None)
        else:
            coach=body.coach_id
            if not coach: raise HTTPException(422,'Đặt PT cần coach_id')
        code='BK'+uuid.uuid4().hex[:8].upper(); fee=400000 if body.activity_type=='pt' else 0
        c.execute('INSERT INTO bookings VALUES(?,?,?,?,?,?,?,?,?)',(code,body.member_id,body.activity_type,body.activity_id,coach,body.branch,body.start_at.isoformat(),'confirmed',fee))
    return {'booking_code':code,'status':'confirmed','fee_vnd':fee,'booking':body.model_dump(mode='json')}


@router.get('/consultations/{code}',tags=['Lịch tập'],summary='Tra lịch đặt lớp/PT')
def lookup_consultation(code:str,member_id:str|None=None):
    with conn() as c: r=c.execute('SELECT * FROM bookings WHERE code=?',(code,)).fetchone()
    if not r or (member_id and r['member_id']!=member_id): raise HTTPException(404,'Không tìm thấy lịch đặt')
    return dict(r)


@router.post('/consultations/{code}/reschedule',tags=['Lịch tập'],summary='Đổi lịch lớp/PT')
def reschedule_consultation(code:str,member_id:str,start_at:datetime):
    with conn() as c:
        r=c.execute('SELECT * FROM bookings WHERE code=? AND member_id=?',(code,member_id)).fetchone()
        if not r: raise HTTPException(404,'Không tìm thấy lịch đặt')
        if r['status']!='confirmed': raise HTTPException(409,'Chỉ lịch confirmed mới được đổi')
        if start_at<=datetime.now(): raise HTTPException(422,'Thời gian mới phải ở tương lai')
        c.execute('UPDATE bookings SET start_at=? WHERE code=?',(start_at.isoformat(),code))
    return {'booking_code':code,'start_at':start_at,'status':'confirmed'}


@router.post('/consultations/{code}/cancel',tags=['Lịch tập'],summary='Hủy lịch lớp/PT theo chính sách')
def cancel_consultation(code:str,member_id:str,dry_run:bool=True):
    with conn() as c:
        r=c.execute('SELECT * FROM bookings WHERE code=? AND member_id=?',(code,member_id)).fetchone()
        if not r: raise HTTPException(404,'Không tìm thấy lịch đặt')
        if r['status']!='confirmed': raise HTTPException(409,'Lịch không còn ở trạng thái confirmed')
        hours=(datetime.fromisoformat(r['start_at'])-datetime.now()).total_seconds()/3600
        fee=0 if (hours>=12 if r['activity_type']=='pt' else hours>=4) else (int(r['fee_vnd']*.5) if r['activity_type']=='pt' else 50000)
        if not dry_run: c.execute('UPDATE bookings SET status="cancelled",fee_vnd=? WHERE code=?',(fee,code))
    return {'booking_code':code,'dry_run':dry_run,'cancellation_fee_vnd':fee,'status':'cancelled' if not dry_run else 'confirmed','policy_source':'policy_cancellation.md'}


