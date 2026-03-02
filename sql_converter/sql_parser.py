"""
Oracle SQL转换器：将wm_concat函数转换为listagg函数

wm_concat (Oracle 10g/11g) 是自定义聚合函数，在Oracle 12c+中被listagg取代

转换规则：
- wm_concat(column) -> listagg(column, ',') within group (order by column)
- wm_concat(distinct column) -> listagg(distinct column, ',') within group (order by column)
"""

import re


def convert_wm_concat_to_listagg(sql):
    """
    将SQL中的wm_concat函数转换为listagg函数
    
    Args:
        sql: 包含wm_concat的SQL语句
        
    Returns:
        转换后的SQL语句
    """
    if not sql or not isinstance(sql, str):
        return sql
    
    # 如果SQL中没有wm_concat，直接返回
    if 'wm_concat' not in sql.lower():
        return sql
    
    result = sql
    
    # 匹配wm_concat函数的各种形式
    # 模式1: wm_concat(column_name)
    # 模式2: wm_concat(distinct column_name)
    # 模式3: wm_concat(unique column_name)
    # 模式4: wm_concat(all column_name)
    
    # 使用正则表达式匹配wm_concat函数
    # 处理嵌套括号的情况
    result = convert_wm_concat_recursive(result)
    
    return result


def convert_wm_concat_recursive(sql):
    """
    递归处理SQL中的wm_concat函数
    处理嵌套和多个wm_concat的情况
    """
    pattern = re.compile(
        r'wm_concat\s*\(\s*(distinct\s+|unique\s+|all\s+)?([^)]+)\)',
        re.IGNORECASE
    )
    
    def replace_match(match):
        modifier = match.group(1) if match.group(1) else ''  # distinct/unique/all
        column_expr = match.group(2).strip()  # 列表达式
        
        # 构建listagg表达式
        # listagg(column, ',') within group (order by column)
        if modifier:
            # 保留修饰符 (distinct/unique/all)
            listagg_expr = f"listagg({modifier.strip()} {column_expr}, ',') within group (order by {column_expr})"
        else:
            listagg_expr = f"listagg({column_expr}, ',') within group (order by {column_expr})"
        
        return listagg_expr
    
    # 持续替换直到没有更多的wm_concat
    prev_sql = None
    current_sql = sql
    
    while prev_sql != current_sql:
        prev_sql = current_sql
        current_sql = pattern.sub(replace_match, current_sql)
    
    return current_sql


def process_excel_sql_column(df, column_name='RULE_SQL_VALUE'):
    """
    处理DataFrame中指定列的SQL转换
    
    Args:
        df: pandas DataFrame
        column_name: 需要转换的列名，默认为'RULE_SQL_VALUE'
        
    Returns:
        转换后的DataFrame和转换统计信息
    """
    import pandas as pd
    
    if column_name not in df.columns:
        raise ValueError(f'Excel文件中缺少必要字段: {column_name}')
    
    # 创建新列存储转换后的SQL
    converted_column = f'{column_name}_CONVERTED'
    
    conversion_count = 0
    
    def convert_cell(sql):
        nonlocal conversion_count
        if pd.isna(sql):
            return sql
        
        converted = convert_wm_concat_to_listagg(str(sql))
        if converted != str(sql):
            conversion_count += 1
        return converted
    
    df[converted_column] = df[column_name].apply(convert_cell)
    
    return df, conversion_count


def convert_sql_file(file_path):
    """
    读取Excel文件并转换SQL
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        转换后的DataFrame和转换统计信息
    """
    import pandas as pd
    
    # 读取Excel文件
    df = pd.read_excel(file_path, engine='openpyxl')
    
    # 检查必要的列
    if 'RULE_SQL_VALUE' not in df.columns:
        raise ValueError('Excel文件中缺少必要字段: RULE_SQL_VALUE')
    
    # 处理转换
    df, conversion_count = process_excel_sql_column(df, 'RULE_SQL_VALUE')
    
    return df, conversion_count
