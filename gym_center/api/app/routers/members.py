"""Members endpoints for Iron Việt Fitness."""
from fastapi import APIRouter
from ..core import *  # shared models, database and knowledge-base helpers

router = APIRouter()

@router.get('/members',tags=['Hội viên'],summary='Danh sách hội viên, lọc theo chi nhánh/trạng thái')
def list_members(branch:str|None=None,status:str|None=None,keyword:str|None=None,limit:int=100,offset:int=0):
    sql='SELECT * FROM members WHERE 1=1'; args=[]
    for field,val in [('branch',branch),('status',status)]:
        if val: sql+=f' AND {field}=?'; args.append(val)
    if keyword: sql+=' AND (member_id LIKE ? OR full_name LIKE ? OR phone LIKE ?)'; args += [f'%{keyword}%']*3
    with conn() as c:
        total=c.execute('SELECT COUNT(*) FROM members').fetchone()[0]; rows=c.execute(sql+' ORDER BY member_id LIMIT ? OFFSET ?',args+[max(1,min(limit,500)),max(0,offset)]).fetchall()
    return {'total_in_database':total,'count':len(rows),'items':[dict(x) for x in rows]}


@router.post('/members',status_code=201,tags=['Hội viên'],summary='Tạo hồ sơ hội viên')
def create_member(body:MemberIn):
    mid='MB'+uuid.uuid4().hex[:8].upper()
    try:
        with conn() as c: c.execute('INSERT INTO members VALUES(?,?,?,?,?,?,?,?,?)',(mid,body.full_name,body.phone,body.email,body.branch,body.goal,'active',body.plan_id,date.today().isoformat()))
    except sqlite3.IntegrityError: raise HTTPException(409,'Số điện thoại đã được đăng ký')
    return {'member_id':mid,'status':'active','member':body.model_dump()}


@router.get('/members/{member_id}',tags=['Hội viên'],summary='Tra hồ sơ hội viên')
def get_member(member_id:str):
    with conn() as c: r=c.execute('SELECT * FROM members WHERE member_id=?',(member_id,)).fetchone()
    if not r: raise HTTPException(404,'Không tìm thấy hội viên')
    return dict(r)


