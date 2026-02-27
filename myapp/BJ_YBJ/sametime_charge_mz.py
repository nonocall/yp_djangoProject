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
    sql_conditions = '( '+'or '.join(conditions)+' ) '
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
    conditions = [f"诊断名称 not like '%{item}%'" for item in items]
    # 使用'or'连接所有的条件
    sql_conditions = '\nand ' + '\nand '.join(conditions)
    if (input_string == ''):
        return ''
    return sql_conditions

def this_main_mz_sametime(condition1,condition2,diag):
    condition1=generate_like_conditions(condition1)
    condition2=generate_like_conditions(condition2)
    part1 = """WITH tab1 AS(
  SELECT 结算单据号
  FROM  医保门诊结算明细
  WHERE """
    part2 = """GROUP BY 结算单据号 HAVING SUM(数量)>0
  INTERSECT
  SELECT 结算单据号
  FROM  医保门诊结算明细
  WHERE """
    part3 = """GROUP BY 结算单据号 HAVING SUM(数量)>0
)
SELECT
  A.结算单据号,
  A.医疗机构编码,
  A.医疗机构名称,
  A.结算日期,
  A.门诊号,
  A.个人编码,
  A.患者社会保障号码,
  A.险种类型,
  A.科室名称,
  A.医师名称,
  A.患者姓名,
  A.患者性别,
  A.患者出生日期,
  A.患者年龄,
  A.医疗类别,
  A.异地标志,
  A.诊断编码,
  A.诊断名称,
  A.医疗总费用,
  A.基本统筹支付,
  A.现金支付,
  A.个人账户支付,
  A.符合基本医疗保险的费用,
  B.开单科室名称,
  B.执行科室名称,
  B.开单医师姓名,
  B.项目使用日期,
  B.费用类别,
  B.医院项目编码,
  B.医院项目名称,
  B.医保项目编码,
  B.医保项目名称,
  B.拒付金额,
  B.支付类别,
  B.报销比例,
  B.自付比例,
  B.支付地点类别,
  B.记账流水号,
  B.规格,
  B.单价,
  B.数量,
  B.金额,
  B.医保范围内金额,\n"""
    part4 = f"CASE WHEN {condition2} THEN B.数量 ELSE 0 END AS 使用总数量,\n"
    part5 = f"CASE WHEN {condition2} THEN B.金额 ELSE 0 END AS 使用总金额,\n"
    part6 = f"CASE WHEN {condition2} THEN B.数量 ELSE 0 END AS 违规数量,\n"
    part7 = f"CASE WHEN {condition2} THEN B.医保范围内金额 ELSE 0 END AS 违规金额\n"
    part8 = """FROM
  医保门诊结算明细 B
  JOIN 医保门诊结算主单 A ON B.结算单据号 = A.结算单据号
  JOIN tab1 C ON B.结算单据号 = C.结算单据号
WHERE """
    #condition3 = """ and A."险种类型" not like '%自费%' AND A.险种类型 not like '%工伤%'"""
    # 打印结果
    if diag is None:
        return part1 + condition1 + part2 + condition2 + part3 + part4 + part5 + part6 + part7 + part8 +' ( ' + condition1 + ' or ' + condition2 + ' ) ' #+condition3
    else:
        diag = generate_diag_conditions(diag)
        return part1 + condition1 + part2 + condition2 + part3 + part4 + part5 + part6 + part7 + part8 + ' ( ' + condition1 + ' or ' + condition2 + ' ) ' + diag #+ condition3