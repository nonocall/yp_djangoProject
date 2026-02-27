import cx_Oracle

# 数据库连接信息
username = 'HDWJW'  # 替换为你的数据库用户名
password = 'HDWJW'  # 替换为你的数据库密码
dsn = 'localhost:1521/orcl'  # 替换为你的数据库DSN（如主机名/服务名或IP地址/端口/服务名）

# 目标表名
target_table = 'SETTLE_MZ_DETAIL' # 替换为你的目标表名

def convert_columns_to_uppercase(username, password, dsn, target_table):
    try:
        # 连接到数据库
        connection = cx_Oracle.connect(username, password, dsn)
        cursor = connection.cursor()

        # 获取目标表的列信息
        cursor.execute(f"SELECT column_name FROM user_tab_columns WHERE table_name = upper('{target_table}')")
        columns = cursor.fetchall()

        # 构造修改字段名的SQL语句
        alter_statements = []
        for column in columns:
            original_column_name = column[0]
            upper_column_name = original_column_name.upper()

            # 如果字段名已经是大写，则跳过
            if original_column_name == upper_column_name:
                continue

            # 构造ALTER TABLE语句
            alter_statement = f'ALTER TABLE {target_table} RENAME COLUMN "{original_column_name}" TO {upper_column_name}'
            alter_statements.append(alter_statement)

        # 执行修改字段名的SQL语句
        for statement in alter_statements:
            cursor.execute(statement)
            print(f"Executed: {statement}")

        # 提交事务
        connection.commit()
        print("字段名已成功转换为大写。")

    except cx_Oracle.DatabaseError as e:
        print(f"发生错误：{e}")
    finally:
        # 关闭数据库连接
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# 调用函数
convert_columns_to_uppercase(username, password, dsn, target_table)