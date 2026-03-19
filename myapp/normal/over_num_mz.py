def generate_like_conditions(input_string):
    if input_string=='':
        return ''
    else:
        # 将输入的字符串按照逗号分割成列表
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
        return sql_conditions

def generate_like_project(input_string):
    # 将输入的字符串按照逗号分割成列表
    if '、' in input_string:
        items = input_string.split('、')
    elif ',' in input_string:
        items = input_string.split(',')
    elif '，' in input_string:
        items = input_string.split(',')
    else:
        items = [input_string]
    # 为每个项创建LIKE条件，并用'or'连接
    conditions = [f"医院项目名称 like '%{item}%'" for item in items]
    # 使用'or'连接所有的条件
    sql_conditions = 'WHERE( ' + 'or '.join(conditions) + ' )'
    return sql_conditions

def this_main_mz_num(project,diag,num):
    project = generate_like_project(project)
    diag = generate_like_conditions(diag)
    input_head1 = """WITH A AS (
    SELECT a.医疗机构编码, a.医疗机构名称, a.医院级别, a.结算单据号, a.结算类别
    , a.结算日期, a.险种类型, a.就医类型, a.异地标志, a.人员类别
    , b.退费标识, a.个人编码或患者社保卡号, a.患者姓名, a.患者身份证号, a.患者性别
    , a.患者出生日期, a.患者年龄, a.主诊医师编码, a.主诊医师名称, a.科室编码,substr(REGEXP_REPLACE(项目使用时间, '[^0-9 ]+', ''),0,8) 项目使用时间 
    , a.科室名称, a.诊断编码, a.诊断名称, b.医保项目编码
    , b.医保项目名称, b.医院项目编码, b.医院项目名称, b.费用类别, b.规格
    , b.剂型, b.最小包装单位, b.用药天数, b.单价
    , sum(b.数量) AS 数量, sum(b.金额) AS 项目总金额
    , sum(b.医保申请支付金额) AS 项目医保内金额"""

    wg = f", 单价*(sum(b.数量)-{num}) AS 项目医保内金额\n"

    input_head2 = """
    FROM 医院门诊结算主单 a
    LEFT JOIN 医院门诊结算明细 b ON a.结算单据号 = b.结算单据号
    WHERE (a.结算类别 like'%医保%' or a.结算类别='1')
    GROUP BY a.医疗机构编码, a.医疗机构名称, a.医院级别, a.结算单据号, a.结算类别, a.结算日期, a.险种类型, a.就医类型, a.异地标志
    , a.人员类别, b.退费标识, a.个人编码或患者社保卡号, a.患者姓名, a.患者身份证号, a.患者性别, a.患者出生日期, a.患者年龄, a.主诊医师编码
    , substr(REGEXP_REPLACE(项目使用时间, '[^0-9 ]+', ''),0,8), a.主诊医师名称, a.科室编码, a.科室名称, a.诊断编码, a.诊断名称
    , b.医保项目编码, b.医保项目名称, b.医院项目编码, b.医院项目名称, b.费用类别, b.规格, b.剂型, b.最小包装单位, b.用药天数, b.单价)
    SELECT A.*,项目总金额 违规金额 FROM A
    """
    # 打印结果
    if diag == '':
        return input_head1 + wg + input_head2 +project+"and 数量 >"
    else:
        return input_head1 + wg + input_head2 + project + diag + "and 数量 >"