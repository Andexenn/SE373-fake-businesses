"""Catalog endpoints for Iron Việt Fitness."""
from fastapi import APIRouter
from ..core import *  # shared models, database and knowledge-base helpers

router = APIRouter()

@router.get('/health',tags=['Hệ thống'])
def health():
    with conn() as c: return {'status':'ok','workspace':'iron-viet-fitness','members':c.execute('select count(*) from members').fetchone()[0],'bookings':c.execute('select count(*) from bookings').fetchone()[0],'mock_data':True}


@router.get('/branches',tags=['Danh mục'],summary='Danh sách chi nhánh và giờ mở cửa')
def branches():
    with conn() as c:
        rows = c.execute('SELECT branch_id, name, address, hours FROM branches WHERE is_active=1 ORDER BY branch_id').fetchall()
    return [dict(row) for row in rows]


@router.get('/products',tags=['Danh mục'],summary='Tìm gói tập hoặc lớp học theo từ khóa, giá và loại')
def products(keyword: str|None=None, product_type: str='plan', max_price: int|None=None):
    if product_type not in ('plan','class'): raise HTTPException(400,'product_type phải là plan hoặc class')
    rows=read_csv('membership_plans.csv' if product_type=='plan' else 'class_schedule.csv')
    out=[]
    for r in rows:
        label=r.get('plan_name',r.get('class_name',''))
        price=int(r.get('price_vnd',0))
        if keyword and keyword.lower() not in json.dumps(r,ensure_ascii=False).lower(): continue
        if max_price is not None and product_type=='plan' and price>max_price: continue
        out.append(r)
    return {'count':len(out),'items':out}


@router.get('/products/{sku}',tags=['Danh mục'],summary='Chi tiết gói tập hoặc lớp học')
def product_detail(sku: str):
    for filename,key in [('membership_plans.csv','plan_id'),('class_schedule.csv','class_id')]:
        for r in read_csv(filename):
            if r[key].lower()==sku.lower(): return r
    raise HTTPException(404,'Không tìm thấy gói tập/lớp học')


@router.get('/inventory',tags=['Hội viên'],summary='Tra cứu hội viên, thẻ tập hoặc số chỗ lớp')
def inventory(keyword: str|None=None, branch: str|None=None, kind: str='members', limit:int=100):
    limit=max(1,min(limit,500))
    with conn() as c:
        if kind=='members':
            sql='SELECT * FROM members WHERE 1=1'; args=[]
            if branch: sql+=' AND branch=?'; args.append(branch)
            if keyword: sql+=' AND (member_id LIKE ? OR full_name LIKE ? OR phone LIKE ?)'; args += [f'%{keyword}%']*3
            rows=[dict(x) for x in c.execute(sql+' LIMIT ?',args+[limit]).fetchall()]
        elif kind=='bookings':
            rows=[dict(x) for x in c.execute('SELECT * FROM bookings WHERE (? IS NULL OR branch=?) AND (? IS NULL OR code LIKE ? OR member_id LIKE ?) LIMIT ?', (branch,branch,keyword,None if keyword is None else f'%{keyword}%',None if keyword is None else f'%{keyword}%',limit)).fetchall()]
        else: raise HTTPException(400,'kind phải là members hoặc bookings')
    return {'count':len(rows),'items':rows}


@router.get('/delivery/zones',tags=['Danh mục'],summary='Danh sách chi nhánh và phạm vi dịch vụ')
def zones(): return {'service':'Tập luyện tại cơ sở','branches':[x['branch_id'] for x in branches()],'delivery_applicable':False}


@router.get('/delivery/slots',tags=['Lịch tập'],summary='Khung giờ lớp/PT theo ngày và chi nhánh')
def slots(date_: date=Query(...,alias='date'), branch: str|None=None, activity_type:str='class'):
    with conn() as c:
        rows=c.execute('SELECT activity_id,coach_id,branch,start_at,status FROM bookings WHERE substr(start_at,1,10)=? AND (? IS NULL OR branch=?) AND activity_type=? AND status="confirmed" ORDER BY start_at',(date_.isoformat(),branch,branch,activity_type)).fetchall()
    return {'date':date_.isoformat(),'count':len(rows),'slots':[dict(x) for x in rows]}


@router.get('/promotions',tags=['Danh mục'],summary='Chương trình ưu đãi hiện có')
def promotions():
    p=ROOT/'knowledge_base'/'promotions_current.pdf'
    src=ROOT/'tools'/'pdf_src'/'promotions_current.md'
    return {'source':'promotions_current.pdf','note':'Xem chi tiết chương trình tại knowledge_base/promotions_current.pdf','source_markdown_available':src.exists()}


@router.get('/discounts/{code}',tags=['Danh mục'],summary='Kiểm tra mã ưu đãi gói tập')
def discount(code:str):
    plans=read_csv('membership_plans.csv'); matched=[p for p in plans if p['plan_id'].lower()==code.lower()]
    if not matched: raise HTTPException(404,'Không tìm thấy mã gói/ưu đãi')
    return {'code':code,'valid':True,'plan':matched[0]}


@router.get('/policy',tags=['Chính sách'],summary='Thông tin policy.yaml')
def policy():
    try:
        import yaml
        return yaml.safe_load((ROOT/'policy.yaml').read_text(encoding='utf-8'))
    except Exception: return {'workspace':'iron-viet-fitness','policy_version':'3.1.0','source':'policy.yaml'}


