import cx_Oracle
import os

os.environ["PATH"] = r"D:\Navicat Premium 17\instantclient_21_17" + os.pathsep + os.environ.get("PATH", "")

def get_oracle_table_names(connection_string):
    """
    连接到Oracle数据库并返回所有表名。
    :param connection_string: 数据库连接字符串，格式为 '用户名/密码@主机名:端口/服务名'
    :return: 表名列表
    """
    try:
        # 建立数据库连接
        connection = cx_Oracle.connect(connection_string)
        cursor = connection.cursor()

        # 查询所有表名（仅限当前用户的所有表）
        query = "SELECT table_name FROM user_tables"
        cursor.execute(query)

        # 获取查询结果
        table_names = [row[0] for row in cursor.fetchall()]

        # 关闭连接
        cursor.close()
        connection.close()

        return table_names

    except cx_Oracle.DatabaseError as e:
        print(f"数据库连接失败：{e}")
        return []


def get_ora_table_rows(connection_string, user, Table_O):
    try:
        # 建立数据库连接
        connection = cx_Oracle.connect(connection_string)
        cursor = connection.cursor()

        # 查询表字段
        query = f"""SELECT column_name, data_type, data_length, nullable
            FROM all_tab_columns
            WHERE owner = UPPER('{user}') AND table_name = '{Table_O}'
            ORDER BY column_id"""

        cursor.execute(query)
        columns = cursor.fetchall()

        list_column_name = []
        for column in columns:
            column_name, data_type, data_length, nullable = column
            list_column_name.append(column_name)
        return list_column_name
    except cx_Oracle.DatabaseError as e:
        print(f"数据库连接或查询失败: {e}")
    finally:
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


def supply_deficiency(table, list,tag):
    if tag == 1:
        list_mzzd = ["结算单据号","医疗机构编码","医疗机构名称","结算日期","个人编码或患者社保卡号","险种类型","人员类别","科室名称","患者姓名","主诊医师编码","主诊医师名称","患者性别","患者出生日期","患者年龄","就医类型","异地标志","诊断编码","诊断名称","医疗总发生费用","医保申请支付金额","科室编码","医院级别","结算类别","退费时间","拒付金额","医保支付费用","退费标识","患者身份证号"]
        list_mzmx = ["结算单据号","个人编码","医疗机构编码","项目使用时间","医院项目编码","医院项目名称","医保项目编码","医保项目名称","规格","剂型","最小包装单位","单价","数量","金额","医保申请支付金额","费用类别","退费时间","退费标识","拒付理由","拒付金额","用药天数","医疗机构名称","患者身份证号"]
        list_zyzd = ["病案号","结算单据号","医疗机构编码","医疗机构名称","医院级别","统筹区域编码","统筹区域名称","结算日期","住院号","个人编码","患者社保卡号","结算类别","险种类型","人员类型","新生儿入院类型","新生儿出生体重","新生儿入院体重","退费标识","退费时间","入院科别编码","入院科室名称","转科科室编码","转科科别名称","出院科室编码","出院科室名称","主诊医师编码","主诊医师姓名","患者姓名","患者性别","患者出生日期","患者年龄","住院医疗类型","异地标志","本地异地结算类型","入院日期","出院日期","住院天数","离院方式","上一次出院日期","是否有31天内再住院计划","医疗总发生费用","医保申请支付金额","医保实际支付费用","拒付金额","入院诊断编码","入院诊断名称","出院诊断编码","出院诊断名称","医保支付方式","病组病种编码","病组病种名称","医保结算等级","患者身份证号"]
        list_zymx = ["结算单据号","个人编码","住院号","医疗机构编码","执行科室编码","执行科室名称","费用类别","项目使用时间","医院项目编码","医院项目名称","医保项目编码","医保项目名称","规格","剂型","最小包装单位","单价","数量","项目总发生金额","医保申请支付金额","拒付金额","拒付理由","出院带药标识","退费标识","退费时间","医疗机构名称","患者身份证号"]
    else:
        list_mzzd = ["结算单据号","医疗机构编码","医疗机构名称","结算日期","个人编码或患者社保卡号","险种类型","人员类别","科室名称","患者姓名","主诊医师编码","主诊医师名称","患者性别","患者出生日期","患者年龄","就医类型","异地标志","诊断编码","诊断名称","医疗总发生费用","医保申请支付金额","科室编码","医院级别","结算类别","退费时间","拒付金额","医保支付费用","退费标识","患者身份证号"]
        list_mzmx = ["结算单据号","个人编码","医疗机构编码","项目使用时间","医院项目编码","医院项目名称","医保项目编码","医保项目名称","规格","剂型","最小包装单位","单价","数量","金额","医保申请支付金额","费用类别","退费时间","退费标识","拒付理由","拒付金额","用药天数","医疗机构名称","患者身份证号"]
        list_zyzd = ["病案号","结算单据号","医疗机构编码","医疗机构名称","医院级别","统筹区域编码","统筹区域名称","结算日期","住院号","个人编码","患者社保卡号","结算类别","险种类型","人员类型","新生儿入院类型","新生儿出生体重","新生儿入院体重","退费标识","退费时间","入院科别编码","入院科室名称","转科科室编码","转科科别名称","出院科室编码","出院科室名称","主诊医师编码","主诊医师姓名","患者姓名","患者性别","患者出生日期","患者年龄","住院医疗类型","异地标志","本地异地结算类型","入院日期","出院日期","住院天数","离院方式","上一次出院日期","是否有31天内再住院计划","医疗总发生费用","医保申请支付金额","医保实际支付费用","拒付金额","入院诊断编码","入院诊断名称","出院诊断编码","出院诊断名称","医保支付方式","病组病种编码","病组病种名称","医保结算等级","患者身份证号"]
        list_zymx = ["结算单据号","个人编码","住院号","医疗机构编码","执行科室编码","执行科室名称","费用类别","项目使用时间","医院项目编码","医院项目名称","医保项目编码","医保项目名称","规格","剂型","最小包装单位","单价","数量","项目总发生金额","医保申请支付金额","拒付金额","拒付理由","出院带药标识","退费标识","退费时间","医疗机构名称","患者身份证号"]
    if table == "mzzd":
        diff = [item for item in list_mzzd if item not in list]
    elif table == "mzmx":
        diff = [item for item in list_mzmx if item not in list]
    elif table == "zyzd":
        diff = [item for item in list_zyzd if item not in list]
    else:
        diff = [item for item in list_zymx if item not in list]
    if len(diff)!=0:
        str_sup = ' '
        for d in diff:
            str_sup = str_sup+"\n,' ' "+d+' '
        return str_sup
    else:
        return ""

def this_main_map_name(connection_string,user, table_D, table_O, POST):
    rows = get_ora_table_rows(connection_string, user, table_O)
    str = str_head = ""
    if table_D == 'mzzd':
        str_head = "create table 医院门诊结算主单 as "
    elif table_D == 'mzmx':
        str_head = "create table 医院门诊结算明细 as "
    elif table_D == 'zyzd':
        str_head = "create table 医院住院结算主单 as "
    elif table_D == 'zymx':
        str_head = "create table 医院住院结算明细 as "
    str_head = str_head+"select "
    str_tail = f"from {table_O}"
    list = []
    for row in rows:
        # 首个不加逗号
        if str == '':
            str = f"\"{row}\" {POST.get(row, '')}"
            list.append(POST.get(row, ''))
        else:
            str = ','.join([str, f"\"{row}\" {POST.get(row, '')}"])
            list.append(POST.get(row, ''))
    str_sup = supply_deficiency(table_D, list,1)
    return str_head + str + str_sup + str_tail
