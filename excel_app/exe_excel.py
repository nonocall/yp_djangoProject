import pandas as pd

from myapp.BJ_YBJ.limit_diag_mz import this_main_mz_diag
from myapp.BJ_YBJ.limit_diag_zy import this_main_zy_diag
from myapp.BJ_YBJ.over_num_mz import this_main_mz_num
from myapp.BJ_YBJ.over_num_zy import this_main_zy_num
from myapp.BJ_YBJ.sametime_charge_mz import this_main_mz_sametime
from myapp.BJ_YBJ.sametime_charge_zy import this_main_zy_sametime

def exe_excel_main(file_path):
    df = pd.read_excel(file_path, engine='openpyxl')
    for index, row in df.iterrows():
        if pd.isna(row['类型']):
            continue
        diag = '' if pd.isna(row['诊断']) else row['诊断']
        if '重复收费' in row['类型']:
            if row['医疗类别'] == '门诊':
                df.at[index,'输出结果'] = this_main_mz_sametime(row['项目A'],row['项目B'],diag)
            if row['医疗类别'] == '住院':
                df.at[index,'输出结果'] = this_main_zy_sametime(row['项目A'],row['项目B'],diag)

        elif '限制诊断' in row['类型']:
            if row['医疗类别'] == '门诊':
                df.at[index,'输出结果'] =  this_main_mz_diag(row['项目A'], diag)
            if row['医疗类别'] == '住院':
                df.at[index,'输出结果'] =  this_main_zy_diag(row['项目A'], diag)

        elif '超标准收费' in row['类型']:
            if row['医疗类别'] == '门诊':
                df.at[index,'输出结果'] =  this_main_mz_num(row['项目A'],'') + '1'
            if row['医疗类别'] == '住院':
                df.at[index,'输出结果'] =  this_main_zy_num(row['项目A'],'') + '1'

    return df
