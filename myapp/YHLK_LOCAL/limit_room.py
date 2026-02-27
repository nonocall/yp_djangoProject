def generate_like_room_mz(input_string,yes_or_no):
    # 将输入的字符串按照逗号分割成列表
    items = input_string.split('、')
    # 为每个项创建LIKE条件，并用'or'连接
    if yes_or_no == 'yes':
        conditions = [f"科室名称 like '%{item}%'" for item in items]
        sql_conditions = ' and (' + '\nor '.join(conditions) + ') \n'
    else:
        conditions = [f"科室名称 not like '%{item}%'" for item in items]
        sql_conditions = ' and (' + '\nand '.join(conditions) + ') \n'
    # 使用'or'连接所有的条件

    return sql_conditions

def generate_like_room_zy(input_string,yes_or_no):
    # 将输入的字符串按照逗号分割成列表
    items = input_string.split('、')
    # 为每个项创建LIKE条件，并用'or'连接
    if yes_or_no == 'yes':
        conditions = [f"入院科室名称||出院科室名称||执行科室名称 like '%{item}%'" for item in items]
        sql_conditions = ' and (' + '\nor '.join(conditions) + ') \n'
    else:
        conditions = [f"入院科室名称||出院科室名称||执行科室名称 not like '%{item}%'" for item in items]
        sql_conditions = ' and (' + '\nand '.join(conditions) + ') \n'
    # 使用'or'连接所有的条件
    return sql_conditions

def limit_room_mz(yes_or_no, room):
    room = generate_like_room_mz(room,yes_or_no)
    return room
def limit_room_zy(yes_or_no, room):
    room = generate_like_room_zy(room, yes_or_no)
    return room
