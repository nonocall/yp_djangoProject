import cx_Oracle
import pandas as pd
from sklearn.ensemble import IsolationForest

def get_instance_data(connection_string):
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
        query = "select a.患者身份证号,to_date(SUBSTR(结算日期, 0,8),'yyyyMMdd') 结算日期,科室名称,医院项目名称,sum(金额) 金额 from 医院门诊结算主单 a left join 医院门诊结算明细 b on a.结算单据号=b.结算单据号 where (结算类别 like'%医保%' or 结算类别 like'%1%')  AND ROWNUM <100 and 费用类别 <> '化验费' group by a.患者身份证号,to_date(SUBSTR(结算日期, 0,8),'yyyyMMdd'),科室名称,医院项目名称"
        cursor.execute(query)

        # 获取查询结果
        rows  = cursor.fetchall()
        columns = ['患者身份证号','结算日期','科室名称','医院项目名称','金额']  # 提取列名

        instance_data = pd.DataFrame(rows, columns=columns)

        # 关闭连接
        cursor.close()
        connection.close()

        return instance_data

    except cx_Oracle.DatabaseError as e:
        print(f"数据库连接失败：{e}")
        return []

if __name__ == '__main__':
    user = 'WJW1202'
    connection_string = f"{user}/{user}@localhost:1521/orcl"
    instance_data = get_instance_data(connection_string)
    # 定义慢性病关键词列表
    chronic_keywords = ["降压", "降糖", "胰岛素", "二甲双胍", "硝苯地平"]
    # 标记慢性病药物
    instance_data["is_chronic"] = instance_data["医院项目名称"].apply(
        lambda x: 1 if any(kw in x for kw in chronic_keywords) else 0
    )
    # 假设当前日期为2023-12-31
    current_date = pd.to_datetime("2024-12-31")
    instance_data["结算日期"] = pd.to_datetime(instance_data["结算日期"])

    # 划分窗口
    historical_mask = (instance_data["结算日期"] >= "2023-01-01") & (instance_data["结算日期"] < "2024-10-01")
    detection_mask = instance_data["结算日期"] >= "2023-10-01"

    historical_df = instance_data[historical_mask]

    detection_df = instance_data[detection_mask]

    # 历史窗口特征
    historical_features = historical_df.groupby("患者身份证号").agg({
        "结算日期": "count",  # 历史总就诊次数
        "金额": ["mean", "sum"],  # 历史单次平均金额、总金额
        "is_chronic": "mean",  # 慢性病用药占比
        "科室名称": lambda x: (x == "口腔科").mean()  # 口腔科就诊占比
    })

    
    print(instance_data)

# # 示例数据（假设是就诊金额和开药次数）
# df = pd.DataFrame({'salary':[4,1,4,5,3,6,2,5,6,2,5,7,1,8,12,33,4,7,6,7,8,55]})
#
# # 训练模型
# model = IsolationForest(n_estimators=100, contamination=0.1)  # 100棵树，假设异常占比10%
# model.fit(df[['salary']])
#
# # 预测（-1表示异常，1表示正常）
# df['scores']  = model.decision_function(df[['salary']])
# df['true'] = model.predict(df[['salary']])
# print(df)  # 输出：[-1  1 -1  1 -1]，表示第0、2、4个点是异常

