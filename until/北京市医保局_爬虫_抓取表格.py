import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 替换成实际的 URL
base_url = "https://fw.ybj.beijing.gov.cn/ddyy/phoneddyy/list"
# 替换成实际的请求头，防止被反爬
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    "Connection": "keep-alive"
}

# 假设总页数是 268
TOTAL_PAGES = 268
# 存储所有数据的列表
all_data = []


# 定义一个函数来解析单页数据
def parse_page_data(html_content):
    """
    解析 HTML 内容，提取 <tr> 元素中的数据。
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    # 找到包含数据的表格（可能需要更精确的 CSS 选择器）
    # 假设所有 <tr> 都在一个 id/class 为 table_container 的表格内
    # 您可能需要根据实际网页调整这个选择器
    table_rows = soup.find_all('tr')

    # 定义一个列表来存储当前页的数据
    page_data = []

    for row in table_rows:
        # 尝试查找您提供的结构中的 <td> 元素
        # 排除表格的头部 (<th>) 或不包含数据的 <tr>
        # 假设有效的 <tr> 至少有 5 个 <td>
        tds = row.find_all('td')
        if len(tds) >= 5:
            try:
                # 提取第一个 <td> 的文本 (代码)
                col1 = tds[0].text.strip()

                # 提取第二个 <td> 内 <a> 标签的文本 (名称)
                col2 = tds[1].find('a').text.strip() if tds[1].find('a') else tds[1].text.strip()

                # 提取第三个 <td> 的文本 (区域)
                col3 = tds[2].text.strip()

                # 提取第四个 <td> 的文本 (类型)
                col4 = tds[3].text.strip()

                # 提取第五个 <td> 的文本 (等级)
                col5 = tds[4].text.strip()

                page_data.append([col1, col2, col3, col4, col5])
            except Exception as e:
                # 遇到解析错误时跳过该行
                # print(f"解析行数据时发生错误: {e}")
                continue

    return page_data


# 主爬虫循环
print(f"--- 开始爬取，目标页数: {TOTAL_PAGES} ---")

for page_num in range(1, TOTAL_PAGES + 1):
    try:
        # --- 关键：模拟翻页请求 ---
        # 绝大多数网站的翻页是通过 POST 提交表单数据，或者 GET 请求携带参数

        # 方案 A: 假设是 GET 请求，页码在 URL 参数中 (最常见)
        # 例如: http://www.example.com/data?page=1
        params = {'page': page_num}
        response = requests.get(base_url, headers=headers, params=params, timeout=5)

        # 方案 B: 如果是 POST 请求，页码在表单数据中
        # data = {'nextpage': page_num, 'other_param': 'value'}
        # response = requests.post(base_url, headers=headers, data=data, timeout=10)

        # 请您根据实际网页，使用开发者工具检查网络请求，确定是 GET 还是 POST，以及页码参数的名称。

        response.raise_for_status()  # 检查请求是否成功

        # 解析数据
        current_page_data = parse_page_data(response.text)
        all_data.extend(current_page_data)

        print(f"成功爬取第 {page_num}/{TOTAL_PAGES} 页，提取 {len(current_page_data)} 条数据。")

        # 设置延迟，防止给服务器带来太大压力，并降低被封 IP 的风险
        time.sleep(1)

    except requests.exceptions.RequestException as e:
        print(f"请求第 {page_num} 页失败: {e}")
        # 失败后等待更长时间再尝试，或者直接跳过
        time.sleep(3)
        continue

print("--- 爬取完成 ---")

# 转换为 DataFrame
columns = ['代码', '名称', '区域', '类型', '等级']
df = pd.DataFrame(all_data, columns=columns)

# 最终输出为表格
print("\n--- 爬取结果 DataFrame ---")
print(df)

# 如果需要保存到 CSV 文件
df.to_csv('crawled_data.csv', index=False, encoding='utf-8-sig')
print("\n数据已保存到 crawled_data.csv")