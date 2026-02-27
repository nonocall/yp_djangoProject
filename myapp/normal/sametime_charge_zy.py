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
    conditions = [f"a.诊断拼接字段 not like '%{item}%'" for item in items]
    # 使用'or'连接所有的条件
    sql_conditions = '\nwhere ( '+'and '.join(conditions)+' ) '
    return sql_conditions

def this_main_zy_sametime(condition1,condition2,diag):
    condition1=generate_like_conditions(condition1)
    condition2=generate_like_conditions(condition2)
    condition_diag = generate_not_like_conditions(diag)
    input_string_head = """with A as (
    select a.医疗机构编码,a.医疗机构名称,a.医院级别,a.病案号,a.住院号,a.结算单据号,a.结算类别,a.本地异地结算类型,a.险种类型,a.退费标识,
    a.医保结算等级,a.结算日期,a.入院科别编码,a.入院科室名称,a.出院科室编码,a.出院科室名称,b.执行科室编码,b.执行科室名称,a.主诊医师编码,
    a.主诊医师姓名,a.个人编码,a.患者身份证号,a.患者姓名,a.患者性别,a.患者出生日期,a.患者年龄,a.患者社保卡号,a.人员类型,a.新生儿入院类型,a.住院医疗类型,a.异地标志,a.入院日期,
    a.出院日期,a.住院天数,a.离院方式,a.上一次出院日期,a.入院诊断名称||','||a.出院诊断名称 诊断拼接字段,项目使用时间,
    a.病组病种编码,a.病组病种名称,b.费用类别,b.医保项目编码,b.医保项目名称,b.医院项目编码,b.医院项目名称,b.规格,b.剂型,
    b.最小包装单位,b.单价,sum(b.数量)数量,sum(b.项目总发生金额)项目总金额, sum(b.医保申请支付金额) as 医保申请支付金额
    from 医院住院结算主单 a left join 医院住院结算明细 b on a.结算单据号=b.结算单据号
    where (结算类别 like'%医保%' or 结算类别 like'%1%')"""

    input_string_mid = """\ngroup by a.医疗机构编码,a.医疗机构名称,a.医院级别,a.病案号,a.住院号,a.结算单据号,a.结算类别,a.本地异地结算类型,a.险种类型,a.退费标识,
    a.医保结算等级,a.结算日期,a.入院科别编码,a.入院科室名称,a.出院科室编码,a.出院科室名称,b.执行科室编码,b.执行科室名称,a.主诊医师编码,
    a.主诊医师姓名,a.个人编码,a.患者身份证号,a.患者姓名,a.患者性别,a.患者出生日期,a.患者年龄,a.患者社保卡号,a.人员类型,a.新生儿入院类型,a.住院医疗类型,a.异地标志,a.入院日期,
    a.出院日期,a.住院天数,a.离院方式,a.上一次出院日期,a.入院诊断名称||','||a.出院诊断名称,项目使用时间,
    a.病组病种编码,a.病组病种名称,b.费用类别,b.医保项目编码,b.医保项目名称,b.医院项目编码,b.医院项目名称,b.规格,b.剂型,
    b.最小包装单位,b.单价)
    ,B as (
    select a.医疗机构编码,a.医疗机构名称,a.医院级别,a.病案号,a.住院号,a.结算单据号,a.结算类别,a.本地异地结算类型,a.险种类型,a.退费标识,
    a.医保结算等级,a.结算日期,a.入院科别编码,a.入院科室名称,a.出院科室编码,a.出院科室名称,b.执行科室编码,b.执行科室名称,a.主诊医师编码,
    a.主诊医师姓名,a.个人编码,a.患者姓名,a.患者性别,a.患者出生日期,a.患者年龄,a.患者社保卡号,a.人员类型,a.新生儿入院类型,a.住院医疗类型,a.异地标志,a.入院日期,
    a.出院日期,a.住院天数,a.离院方式,a.上一次出院日期,a.入院诊断名称||','||a.出院诊断名称 诊断拼接字段,项目使用时间,
    a.病组病种编码,a.病组病种名称,b.费用类别,b.医保项目编码,b.医保项目名称,b.医院项目编码,b.医院项目名称,b.规格,b.剂型,
    b.最小包装单位,b.单价,sum(b.数量)数量,sum(b.项目总发生金额)项目总金额, sum(b.医保申请支付金额) as 医保申请支付金额
    from 医院住院结算主单 a left join 医院住院结算明细 b on a.结算单据号=b.结算单据号
    where (结算类别 like'%医保%' or 结算类别 like'%1%')"""

    input_string_tail = """\ngroup by a.医疗机构编码,a.医疗机构名称,a.医院级别,a.病案号,a.住院号,a.结算单据号,a.结算类别,a.本地异地结算类型,a.险种类型,a.退费标识,
    a.医保结算等级,a.结算日期,a.入院科别编码,a.入院科室名称,a.出院科室编码,a.出院科室名称,b.执行科室编码,b.执行科室名称,a.主诊医师编码,
    a.主诊医师姓名,a.个人编码,a.患者姓名,a.患者性别,a.患者出生日期,a.患者年龄,a.患者社保卡号,a.人员类型,a.新生儿入院类型,a.住院医疗类型,a.异地标志,a.入院日期,
    a.出院日期,a.住院天数,a.离院方式,a.上一次出院日期,a.入院诊断名称||','||a.出院诊断名称,项目使用时间,
    a.病组病种编码,a.病组病种名称,b.费用类别,b.医保项目编码,b.医保项目名称,b.医院项目编码,b.医院项目名称,b.规格,b.剂型,
    b.最小包装单位,b.单价)
     select A.* ,B.医院项目编码 医院项目编码2,B.医院项目名称 医院项目名称2,B.医保项目编码 医保项目编码2,B.医保项目名称 医保项目名称2 
     ,B.数量 数量2,B.单价 单价2,B.项目总金额 项目2总金额,B.医保申请支付金额 项目2医保内金额,B.项目总金额 违规金额
    from A inner join B  on A.医疗机构编码=B.医疗机构编码  and A.结算单据号=B.结算单据号 and A.结算日期=B.结算日期 
    AND substr(REGEXP_REPLACE(a.项目使用时间, '[^0-9 ]+', ''),0,8)=substr(REGEXP_REPLACE(b.项目使用时间, '[^0-9 ]+', ''),0,8)"""
    # 打印结果
    if diag == '':
        return input_string_head+condition1+input_string_mid+condition2+input_string_tail
    else:
        return input_string_head+condition1+input_string_mid+condition2+input_string_tail+condition_diag