import os
import pandas as pd

# 1. 只需改这里：把 Excel 所在目录填进去
EXCEL_DIR = r"G:\药品住院"  # 可以是绝对路径，也可以是相对路径，如 r"./data"

# 2. 校验目录
if not os.path.isdir(EXCEL_DIR):
    raise FileNotFoundError(f"目录不存在：{EXCEL_DIR}")

# 3. 扫描目录下所有 .xlsx 文件
excel_files = [f for f in os.listdir(EXCEL_DIR) if f.lower().endswith('.xlsx')]

if not excel_files:
    print("⚠️ 指定目录下未找到 .xlsx 文件，程序退出。")
    exit()

# 4. 逐个文件拆分
for file in excel_files:
    full_path = os.path.join(EXCEL_DIR, file)
    try:
        df = pd.read_excel(full_path)
        if '医保项目名称' not in df.columns:
            print(f"⚠️ 文件 {file} 中未找到‘医保项目名称’列，已跳过。")
            continue

        for project_name, group in df.groupby('医保项目名称'):
            safe_name = "".join(c for c in str(project_name) if c not in r'\/:*?"<>|')
            out_file = os.path.join(EXCEL_DIR, f"{safe_name}_住院.xlsx")
            group.to_excel(out_file, index=False)
            print(f"✅ 已生成：{out_file}")

    except Exception as e:
        print(f"❌ 处理文件 {file} 时出错：{e}")