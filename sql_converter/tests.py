"""
SQL转换器测试文件
"""

from django.test import TestCase
from .sql_parser import convert_wm_concat_to_listagg, process_excel_sql_column
import pandas as pd


class SQLConverterTests(TestCase):
    """测试SQL转换功能"""

    def test_simple_wm_concat(self):
        """测试简单的wm_concat转换"""
        sql = "SELECT wm_concat(name) FROM users"
        result = convert_wm_concat_to_listagg(sql)
        expected = "SELECT listagg(name, ',') within group (order by name) FROM users"
        self.assertEqual(result, expected)

    def test_wm_concat_with_distinct(self):
        """测试带distinct的wm_concat转换"""
        sql = "SELECT wm_concat(distinct name) FROM users"
        result = convert_wm_concat_to_listagg(sql)
        expected = "SELECT listagg(distinct name, ',') within group (order by name) FROM users"
        self.assertEqual(result, expected)

    def test_wm_concat_with_unique(self):
        """测试带unique的wm_concat转换"""
        sql = "SELECT wm_concat(unique name) FROM users"
        result = convert_wm_concat_to_listagg(sql)
        expected = "SELECT listagg(unique name, ',') within group (order by name) FROM users"
        self.assertEqual(result, expected)

    def test_no_wm_concat(self):
        """测试没有wm_concat的SQL"""
        sql = "SELECT name FROM users"
        result = convert_wm_concat_to_listagg(sql)
        self.assertEqual(result, sql)

    def test_multiple_wm_concat(self):
        """测试多个wm_concat的转换"""
        sql = "SELECT wm_concat(name), wm_concat(distinct age) FROM users"
        result = convert_wm_concat_to_listagg(sql)
        self.assertIn("listagg(name, ',')", result)
        self.assertIn("listagg(distinct age, ',')", result)

    def test_case_insensitive(self):
        """测试大小写不敏感"""
        sql = "SELECT WM_CONCAT(name) FROM users"
        result = convert_wm_concat_to_listagg(sql)
        self.assertIn("listagg(name, ',')", result)

    def test_process_dataframe(self):
        """测试处理DataFrame"""
        data = {
            'RULE_SQL_VALUE': [
                'SELECT wm_concat(name) FROM users',
                'SELECT wm_concat(distinct age) FROM employees',
                'SELECT name FROM users'  # 没有wm_concat
            ]
        }
        df = pd.DataFrame(data)
        result_df, count = process_excel_sql_column(df, 'RULE_SQL_VALUE')
        
        # 检查转换列是否存在
        self.assertIn('RULE_SQL_VALUE_CONVERTED', result_df.columns)
        
        # 检查转换数量
        self.assertEqual(count, 2)
        
        # 检查转换结果
        self.assertIn("listagg(name, ',')", result_df['RULE_SQL_VALUE_CONVERTED'].iloc[0])
        self.assertIn("listagg(distinct age, ',')", result_df['RULE_SQL_VALUE_CONVERTED'].iloc[1])

    def test_empty_sql(self):
        """测试空SQL"""
        result = convert_wm_concat_to_listagg(None)
        self.assertIsNone(result)
        
        result = convert_wm_concat_to_listagg("")
        self.assertEqual(result, "")

    def test_nested_wm_concat(self):
        """测试嵌套的wm_concat"""
        sql = "SELECT wm_concat(wm_concat(name)) FROM users"
        result = convert_wm_concat_to_listagg(sql)
        # 应该转换两个wm_concat
        self.assertEqual(result.count("listagg"), 2)
