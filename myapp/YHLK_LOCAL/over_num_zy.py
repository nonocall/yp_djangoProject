def generate_like_conditions(input_string):
    if input_string=='':
        return ''
    else:
        # 将输入的字符串按照逗号分割成列表
        items = input_string.split('、')
        # 为每个项创建LIKE条件，并用'or'连接
        conditions = [f"a.入院诊断名称||','|| a.出院诊断名称 not like '%{item}%'" for item in items]
        # 使用'or'连接所有的条件
        sql_conditions = 'and ' + '\nand '.join(conditions)
        return sql_conditions


def generate_like_project(input_string):
    if input_string=='':
        return ''
    else:
        # 将输入的字符串按照逗号分割成列表
        items = input_string.split('、')
        # 为每个项创建LIKE条件，并用'or'连接
        conditions = [f"医院项目名称 like '%{item}%'" for item in items]
        # 使用'or'连接所有的条件
        sql_conditions = ' and ('+'\nor '.join(conditions)+')  '
        return sql_conditions

def this_main_zy_num(project,diag):
    diag = generate_like_conditions(diag)
    project = generate_like_project(project)

    input_string_head1 = """select
    a.医疗机构编码, a.医疗机构名称, a.医院级别,a.病案号, a.结算单据号, 
    a.住院号,  a.患者姓名, a.患者性别, a.患者出生日期, a.患者年龄, a.患者社保卡号,a.患者身份证号,
    a.结算类别,a.结算日期,a.险种类型,a.异地标志,a.退费标识,a.入院科室名称,a.出院科室编码, a.出院科室名称,
    a.主诊医师编码, a.主诊医师姓名,a.入院日期, a.出院日期, a.住院天数,a.医疗总发生费用,substr(REGEXP_REPLACE(项目使用时间, '[^0-9 ]+', ''),0,8) 项目使用时间,
    a.医保申请支付金额 as 医保申请总支付金额 , a.医保实际支付费用,a.入院诊断名称||','|| a.出院诊断名称 as 诊断拼接,人员类型,
    b.费用类别, b.执行科室名称, b.医保项目编码, b.医保项目名称, b.医院项目编码, b.医院项目名称, 规格,剂型,    
    b.单价,sum(b.数量) as 数量, sum(b.项目总发生金额) as 项目总发生金额, sum(b.医保申请支付金额) 医保申请支付金额,sum(cast(b.项目总发生金额 as decimal(18,2)))违规金额
    """
    input_string_join = """from 医院住院结算主单 a left join 医院住院结算明细 b on a.结算单据号 = b.结算单据号
    where (a.结算类别 like'%医保%' or a.结算类别='1')"""

    input_string_tail = """\ngroup by 
    a.医疗机构编码, a.医疗机构名称, a.医院级别,a.病案号, a.结算单据号, 
    a.住院号,  a.患者姓名, a.患者性别, a.患者出生日期, a.患者年龄, a.患者社保卡号,a.患者身份证号,
    a.结算类别,a.结算日期,a.险种类型,a.异地标志,a.退费标识,a.出院科室编码, a.出院科室名称,
    a.主诊医师编码, a.主诊医师姓名,a.入院日期, a.出院日期, a.住院天数,a.医疗总发生费用,substr(REGEXP_REPLACE(项目使用时间, '[^0-9 ]+', ''),0,8),
    a.医保申请支付金额, a.医保实际支付费用,a.入院科室名称,a.入院诊断名称||','|| a.出院诊断名称 ,人员类型,
    b.费用类别, b.执行科室名称,b.医保项目编码, b.医保项目名称, 规格,剂型, b.医院项目编码, b.医院项目名称,b.单价
    having sum(数量)>"""

    # 打印结果
    return input_string_head1+input_string_join+project+diag+input_string_tail