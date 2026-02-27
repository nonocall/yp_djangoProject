def generate_like_conditions(input_string):
    # 将输入的字符串按照逗号分割成列表
    items = ''
    if '、' in input_string:
        items = input_string.split('、')
    elif ',' in input_string:
        items = input_string.split(',')
    elif '，' in input_string:
        items = input_string.split(',')
    else:
        items = [input_string]
    # 为每个项创建LIKE条件，并用'or'连接
    conditions = [f"医保项目名称 like '%{item}%'" for item in items]
    # 使用'or'连接所有的条件
    sql_conditions = ' ( '+'or '.join(conditions)+' ) '
    return sql_conditions

def generate_diag_conditions(input_string):
    # 将输入的字符串按照逗号分割成列表
    items = ''
    if '、' in input_string:
        items = input_string.split('、')
    elif ',' in input_string:
        items = input_string.split(',')
    elif '，' in input_string:
        items = input_string.split(',')
    else:
        items = [input_string]
    # 为每个项创建LIKE条件，并用'or'连接
    conditions = [f"COALESCE(tab1.入院诊断名称, '') || ',' || COALESCE(tab1.出院诊断名称, '') not like '%{item}%'" for item in items]
    # 使用'or'连接所有的条件
    sql_conditions = '\nwhere '+'\nand '.join(conditions)
    if (input_string == ''):
        return ''
    return sql_conditions

def this_main_zy_diag(p1,p2,diag):
    condition1=generate_like_conditions(p1)
    condition2=generate_like_conditions(p2)
    part1 = """WITH tab1 AS (
SELECT
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
B.项目使用日期::DATE 项目使用日期,
string_agg(distinct B.开单科室名称,'@') 开单科室名称,
string_agg(distinct B.执行科室名称,'@') 执行科室名称,
string_agg(distinct B.开单医师姓名,'@') 开单医师姓名,
string_agg(distinct B.费用类别,'@') 费用类别,
string_agg(distinct B.医院项目编码,'@') 医院项目编码,
string_agg(distinct B.医院项目名称,'@') 医院项目名称,
string_agg(distinct B.医保项目编码,'@') 医保项目编码,
string_agg(distinct B.医保项目名称,'@') 医保项目名称,
string_agg(distinct B.拒付金额,'@') 拒付金额,
string_agg(distinct B.支付类别,'@') 支付类别,
string_agg(distinct B.报销比例,'@') 报销比例,
string_agg(distinct B.自付比例,'@') 自付比例,
string_agg(distinct B.支付地点类别,'@') 支付地点类别,
string_agg(distinct B.记账流水号,'@') 记账流水号,
string_agg(distinct B.规格,'@') 规格,
string_agg(distinct B.单价::varchar,'@') 单价,
sum(B.数量) 数量,
sum(B.金额) 金额,
sum(B.医保范围内金额) 医保范围内金额
FROM
医保住院结算明细 B
JOIN 医保住院结算主单 A ON A.结算单据号 = B.结算单据号
WHERE """
    part2 = """ group by
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
(A.出院日期 :: DATE) - (A.入院日期 :: DATE),
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
B.项目使用日期::DATE
),tab2 AS (
SELECT
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
B.项目使用日期::DATE 项目使用日期,
string_agg(distinct B.开单科室名称,'@') 开单科室名称,
string_agg(distinct B.执行科室名称,'@') 执行科室名称,
string_agg(distinct B.开单医师姓名,'@') 开单医师姓名,
string_agg(distinct B.费用类别,'@') 费用类别,
string_agg(distinct B.医院项目编码,'@') 医院项目编码,
string_agg(distinct B.医院项目名称,'@') 医院项目名称,
string_agg(distinct B.医保项目编码,'@') 医保项目编码,
string_agg(distinct B.医保项目名称,'@') 医保项目名称,
string_agg(distinct B.支付类别,'@') 支付类别,
string_agg(distinct B.报销比例,'@') 报销比例,
string_agg(distinct B.自付比例,'@') 自付比例,
string_agg(distinct B.支付地点类别,'@') 支付地点类别,
string_agg(distinct B.记账流水号,'@') 记账流水号,
string_agg(distinct B.规格,'@') 规格,
string_agg(distinct B.单价::varchar,'@') 单价,
sum(B.数量) 数量,
sum(B.金额) 金额,
sum(B.医保范围内金额) 医保范围内金额
FROM
医保住院结算明细 B
JOIN 医保住院结算主单 A ON A.结算单据号 = B.结算单据号
WHERE """
    part3 = """group by
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
(A.出院日期 :: DATE) - (A.入院日期 :: DATE) + 1 ,
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
B.项目使用日期::DATE
)
SELECT tab1.*,tab2.医院项目编码 医院项目编码2,tab2.医院项目名称 医院项目名称2,tab2.医保项目编码 医保项目编码2,tab2.医保项目名称 医保项目名称2
,tab2.单价 单价2,tab2.数量 数量2,tab2.金额 金额2,tab2.数量 违规数量,tab2.金额 违规金额
from tab1 join tab2 on tab2.结算单据号 = tab1.结算单据号 and tab2.项目使用日期 = tab1.项目使用日期 """

    condition3 = """ and (A.医保结算与非医保结算标志 like '%医保%' or A.医保结算与非医保结算标志 = '1' )\n"""
    if diag is None:
        return part1 + condition1 + condition3 + part2 + condition2 + condition3 + part3
    else:
        diag = generate_diag_conditions(diag)
        return part1 + condition1 + condition3 + part2 + condition2 + condition3 + part3 + diag