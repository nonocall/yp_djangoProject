from django.views.decorators.http import condition


def generate_like_conditions(input_string):
    # 将输入的字符串按照逗号分割成列表
    items = ''
    if '、' in input_string:
        items = input_string.split('、')
    elif ',' in input_string:
        items = input_string.split(',')
    elif '，' in input_string:
        items = input_string.split('，')
    else:
        items = [input_string]
    # 为每个项创建LIKE条件，并用'or'连接
    conditions = [f"COALESCE(入院诊断名称, '') || ',' || COALESCE(出院诊断名称, '')  not like '%{item}%'" for item in items]
    # 使用'or'连接所有的条件
    sql_conditions = 'and '+'\nand '.join(conditions)
    if (input_string == ''):
        return ''
    return sql_conditions

def generate_like_project(input_string):
    # 将输入的字符串按照逗号分割成列表
    items = input_string.split('、')
    # 为每个项创建LIKE条件，并用'or'连接
    conditions = [f"医保项目名称 like '%{item}%'" for item in items]
    # 使用'or'连接所有的条件
    sql_conditions = ' ('+'\nor '.join(conditions)+') \n'
    return sql_conditions

def this_main_zy_diag(project,diag):
    diag = generate_like_conditions(diag)
    project = generate_like_project(project)

    input_string_head1 = """SELECT
A.病案号,
A.结算单据号,
A.医疗机构编码,
A.医疗机构名称,
A.结算日期,
A.住院号,
A.个人编码,
A.患者社会保障号码,
A.身份证号,
A.险种类型,
A.入院科室,
A.出院科室,
A.主诊医师姓名,
A.患者姓名,
A.患者年龄,
A.患者性别,
A.异地标志,
A.入院日期,
A.出院日期,
(A.出院日期 :: DATE) - (A.入院日期 :: DATE) + 1 AS 住院天数,
A.医疗总费用,
A.基本统筹支付,
A.个人自付,
A.个人自费,
A.符合基本医疗保险的费用,
A.入院诊断编码,
A.入院诊断名称,
A.出院诊断编码,
A.出院诊断名称,
A.主手术及操作编码,
A.主手术及操作名称,
A.其他手术及操作编码,
A.其他手术及操作名称,
B.开单科室名称,
B.执行科室名称,
B.开单医师姓名,
B.费用类别,
B.项目使用日期,
B.医院项目编码,
B.医院项目名称,
B.医保项目编码,
B.医保项目名称,
B.支付类别,
B.报销比例,
B.自付比例,
B.支付地点类别,
B.记账流水号,
B.规格,
B.单价,
B.数量,
B.金额,
B.医保范围内金额,
B.数量 AS 使用总数量,
B.金额 AS 使用总金额,
B.数量 AS 违规数量,
B.医保范围内金额 AS 违规金额
FROM
医保住院结算明细 B
JOIN 医保住院结算主单 A ON A.结算单据号 = B.结算单据号 
WHERE """

    # condition3 = """ and A."险种类型" not like '%自费%' AND A.险种类型 not like '%工伤%'"""

    # 打印结果
    return input_string_head1+project+diag# +condition3