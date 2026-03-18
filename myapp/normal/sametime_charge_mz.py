def generate_like_conditions(input_string):
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
    conditions = [f"b.医院项目名称 like '%{item}%'" for item in items]
    # 使用'or'连接所有的条件
    sql_conditions = '\nand ( '+'or '.join(conditions)+' ) '
    return sql_conditions

def generate_not_like_conditions(input_string):
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
    conditions = [f"a.诊断名称 not like '%{item}%'" for item in items]
    # 使用'or'连接所有的条件
    sql_conditions = '\nwhere ( '+'and '.join(conditions)+' ) '
    return sql_conditions

def this_main_mz_sametime(condition1,condition2,diag):
    condition1=generate_like_conditions(condition1)
    condition2=generate_like_conditions(condition2)
    condition_diag = generate_not_like_conditions(diag)
    input_string_head = """WITH A AS (
		SELECT a.医疗机构编码, a.医疗机构名称, a.医院级别, a.结算单据号, a.结算类别
			, a.结算日期, a.险种类型, a.就医类型, a.异地标志, a.人员类别
			, b.退费标识, a.个人编码或患者社保卡号, a.患者姓名, a.患者身份证号, a.患者性别
			, a.患者出生日期, a.患者年龄, a.主诊医师编码, a.主诊医师名称, a.科室编码
			, a.科室名称, a.诊断编码, a.诊断名称, b.医保项目编码
			, b.医保项目名称, b.医院项目编码, b.医院项目名称, b.费用类别, b.规格
			, b.剂型, b.最小包装单位, b.用药天数, b.单价
			, sum(b.数量) AS 数量, sum(b.金额) AS 项目总金额
			, sum(b.医保申请支付金额) AS 项目医保内金额
		FROM 医院门诊结算主单 a
			LEFT JOIN 医院门诊结算明细 b ON a.结算单据号 = b.结算单据号 
		WHERE (a.结算类别 like'%医保%' or a.结算类别='1')"""

    input_string_mid = """\nGROUP BY a.医疗机构编码, a.医疗机构名称, a.医院级别, a.结算单据号, a.结算类别, a.结算日期, a.险种类型, a.就医类型, a.异地标志, a.人员类别, b.退费标识, a.个人编码或患者社保卡号, a.患者姓名, a.患者身份证号, a.患者性别, a.患者出生日期, a.患者年龄, a.主诊医师编码, a.主诊医师名称, a.科室编码, a.科室名称, a.诊断编码, a.诊断名称, b.医保项目编码, b.医保项目名称, b.医院项目编码, b.医院项目名称, b.费用类别, b.规格, b.剂型, b.最小包装单位, b.用药天数, b.单价
	), B AS (
		SELECT a.医疗机构编码, a.医疗机构名称, a.医院级别, a.结算单据号, a.结算类别
			, a.结算日期, a.险种类型, a.就医类型, a.异地标志, a.人员类别
			, b.退费标识, a.个人编码或患者社保卡号, a.患者姓名, a.患者身份证号, a.患者性别
			, a.患者出生日期, a.患者年龄, a.主诊医师编码, a.主诊医师名称, a.科室编码
			, a.科室名称, a.诊断编码, a.诊断名称, b.医保项目编码
			, b.医保项目名称, b.医院项目编码, b.医院项目名称, b.费用类别, b.规格
			, b.剂型, b.最小包装单位, b.用药天数, b.单价
			, sum(b.数量) AS 数量, sum(b.金额) AS 项目总金额
			, sum(b.医保申请支付金额) AS 项目医保内金额
		FROM 医院门诊结算主单 a
			LEFT JOIN 医院门诊结算明细 b ON a.结算单据号 = b.结算单据号 
		WHERE (a.结算类别 like'%医保%' or a.结算类别='1')"""

    input_string_tail = """\nGROUP BY a.医疗机构编码, a.医疗机构名称, a.医院级别, a.结算单据号
    , a.结算类别, a.结算日期, a.险种类型, a.就医类型, a.异地标志, a.人员类别, b.退费标识, a.个人编码或患者社保卡号, a.患者姓名
    , a.患者身份证号, a.患者性别, a.患者出生日期, a.患者年龄, a.主诊医师编码, a.主诊医师名称, a.科室编码, a.科室名称, a.诊断编码, a.诊断名称
    , b.医保项目编码, b.医保项目名称, b.医院项目编码, b.医院项目名称, b.费用类别, b.规格, b.剂型, b.最小包装单位, b.用药天数, b.单价
	)
SELECT A.*, B.医院项目编码 AS 医院项目编码2, B.医院项目名称 AS 医院项目名称2, B.医保项目编码 AS 医保项目编码2, B.医保项目名称 AS 医保项目名称2
	, B.数量 AS 数量2, B.单价 AS 单价2, B.项目总金额 AS 项目2总金额, B.项目医保内金额 AS 项目2医保内金额, B.项目总金额 AS 违规金额
FROM A
	INNER JOIN B ON A.医疗机构编码 = B.医疗机构编码
	AND A.结算单据号 = B.结算单据号
	AND A.结算日期 = B.结算日期"""
    # 打印结果
    if diag == '':
        return input_string_head+condition1+input_string_mid+condition2+input_string_tail
    else:
        return input_string_head+condition1+input_string_mid+condition2+input_string_tail +condition_diag