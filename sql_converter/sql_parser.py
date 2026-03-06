"""
Oracle SQL转换器：将wm_concat函数转换为listagg函数，并消除占位符条件

wm_concat (Oracle 10g/11g) 是自定义聚合函数，在Oracle 12c+中被listagg取代

转换规则：
- wm_concat(column) -> listagg(column, ',') within group (order by column)
- wm_concat(distinct column) -> listagg(distinct column, ',') within group (order by column)

占位符消除规则：
- 消除包含 '{#yljgmc#}' 的条件表达式
- 处理 '=' 和 'in' 操作符（允许中间有空格）
- 智能处理 WHERE 和 AND 关键字
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


def remove_placeholder_conditions(sql, placeholder='{#yljgmc#}'):
    """
    消除SQL中包含指定占位符的条件表达式

    处理逻辑：
    1. 匹配包含占位符的条件（支持 = 和 in 操作符，允许空格）
    2. 如果是唯一条件，同步消除 WHERE 关键字
    3. 如果不是唯一条件，消除前/后的 AND 关键字

    Args:
        sql: SQL语句
        placeholder: 占位符字符串，默认为 '{#yljgmc#}'

    Returns:
        处理后的SQL语句
    """
    if not sql or not isinstance(sql, str):
        return sql

    if placeholder not in sql:
        return sql

    result = sql

    # 构建匹配模式：列名 操作符 占位符
    # 支持以下格式：
    # A.医疗机构名称 ={#yljgmc#}
    # A.医疗机构名称 = {#yljgmc#}
    # A.医疗机构名称 in({#yljgmc#})
    # A.医疗机构名称 in ({#yljgmc#})
    # A.医疗机构名称 IN({#yljgmc#}) 等大小写不敏感

    # 匹配列名（支持字母、数字、下划线、点号）
    column_pattern = r'[\w\.]+'
    # 匹配操作符（= 或 in，允许前后空格）
    operator_pattern = r'(?:\s*=\s*|\s+in\s*\(?\s*)'
    # 匹配占位符（转义特殊字符）
    escaped_placeholder = re.escape(placeholder)

    # 完整条件模式：列名 操作符 占位符（可能后跟右括号）
    condition_pattern = (
        rf'({column_pattern})'  # 列名 (捕获组1)
        rf'({operator_pattern})'  # 操作符 (捕获组2)
        rf'({escaped_placeholder})'  # 占位符 (捕获组3)
        rf'(\s*\)?)?'  # 可选的右括号 (捕获组4)
    )

    # 使用正则查找所有匹配的条件
    matches = list(re.finditer(condition_pattern, result, re.IGNORECASE))

    if not matches:
        return result

    # 从后向前处理，避免位置偏移问题
    for match in reversed(matches):
        full_condition = match.group(0)
        start_pos = match.start()
        end_pos = match.end()

        # 获取条件周围的上下文
        before_text = result[:start_pos]
        after_text = result[end_pos:]

        # 检查前面是否有 WHERE 或 AND
        # 向前查找 WHERE 或 AND（忽略空格）
        before_trimmed = before_text.rstrip()

        # 检查是否是 WHERE 开头的唯一条件
        where_pattern = re.compile(r'\bwhere\s*$', re.IGNORECASE)
        and_pattern = re.compile(r'\band\s*$', re.IGNORECASE)

        is_where = where_pattern.search(before_trimmed)
        is_and = and_pattern.search(before_trimmed)

        # 检查后一个条件是否存在（用于判断是否是唯一条件）
        # 查找后面是否有 AND 或其他条件
        after_trimmed = after_text.lstrip()
        has_following_condition = bool(re.match(r'\band\b', after_trimmed, re.IGNORECASE))

        if is_where and not has_following_condition:
            # 情况1：这是 WHERE 后的唯一条件，需要消除整个 WHERE 条件
            # 找到 WHERE 的位置
            where_match = where_pattern.search(before_trimmed)
            where_start = where_match.start()

            # 构建新结果：保留 WHERE 之前的部分 + WHERE 之后的部分（去掉当前条件）
            # 需要检查 WHERE 后面是否只有这一个条件
            between_where_and_condition = before_trimmed[where_match.end():start_pos].strip()

            if not between_where_and_condition:
                # WHERE 后面直接跟着这个条件，没有其他条件
                # 消除 WHERE 和当前条件
                result = before_trimmed[:where_match.start()] + after_text
            else:
                # WHERE 后面还有其他内容（如括号等），只消除当前条件
                result = before_text + after_text

        elif is_and:
            # 情况2：前面有 AND，消除 AND 和当前条件
            and_match = and_pattern.search(before_trimmed)
            result = before_trimmed[:and_match.start()] + ' ' + after_text.lstrip()

        elif re.match(r'\s*\band\b', after_text, re.IGNORECASE):
            # 情况3：后面有 AND，消除当前条件和后面的 AND
            following_and_match = re.match(r'\s*\band\b', after_text, re.IGNORECASE)
            result = before_text + after_text[following_and_match.end():]

        else:
            # 情况4：独立条件，直接消除
            result = before_text + after_text

    # 清理多余空格
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\s*,\s*', ', ', result)  # 保留逗号后的一个空格
    result = re.sub(r'\s*\(\s*', ' (', result)  # 括号前空格
    result = re.sub(r'\s*\)', ')', result)  # 括号前无多余空格

    return result.strip()


def process_excel_sql_column(df, column_name='RULE_SQL_VALUE', remove_placeholders=True):
    """
    处理DataFrame中指定列的SQL转换

    Args:
        df: pandas DataFrame
        column_name: 需要转换的列名，默认为'RULE_SQL_VALUE'
        remove_placeholders: 是否消除占位符条件，默认为True

    Returns:
        转换后的DataFrame和转换统计信息字典
    """
    import pandas as pd

    if column_name not in df.columns:
        raise ValueError(f'Excel文件中缺少必要字段: {column_name}')

    # 创建新列存储转换后的SQL
    converted_column = f'{column_name}_CONVERTED'

    wm_concat_count = 0
    placeholder_count = 0

    def convert_cell(sql):
        nonlocal wm_concat_count, placeholder_count
        if pd.isna(sql):
            return sql

        original_sql = str(sql)
        converted = original_sql

        # 步骤1：转换 wm_concat
        converted = convert_wm_concat_to_listagg(converted)
        if converted != original_sql:
            wm_concat_count += 1

        # 步骤2：消除占位符条件
        if remove_placeholders:
            placeholder_converted = remove_placeholder_conditions(converted)
            if placeholder_converted != converted:
                placeholder_count += 1
                converted = placeholder_converted

        return converted

    df[converted_column] = df[column_name].apply(convert_cell)

    # 编码为单一数值：wm_concat_count * 10000 + placeholder_count
    # 支持最大9999次占位符消除，可调整倍数
    conversion_count = wm_concat_count * 10000 + placeholder_count

    # 返回字典格式的统计信息
    return df, conversion_count


def convert_sql_file(file_path, remove_placeholders=True):
    """
    读取Excel文件并转换SQL

    Args:
        file_path: Excel文件路径
        remove_placeholders: 是否消除占位符条件，默认为True

    Returns:
        转换后的DataFrame和转换统计信息字典
    """
    import pandas as pd

    # 读取Excel文件
    df = pd.read_excel(file_path, engine='openpyxl')

    # 检查必要的列
    if 'RULE_SQL_VALUE' not in df.columns:
        raise ValueError('Excel文件中缺少必要字段: RULE_SQL_VALUE')

    # 处理转换
    df, conversion_count = process_excel_sql_column(df, 'RULE_SQL_VALUE', remove_placeholders)

    # 直接返回统计字典
    return df, conversion_count
