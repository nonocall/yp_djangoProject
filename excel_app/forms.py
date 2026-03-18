from django import forms
from .models import ExcelFile


class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelFile
        fields = ('file',)

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # 验证文件扩展名
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError("只支持Excel文件 (.xlsx, .xls)")
        return file


class OracleRuleForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel文件',
        help_text='支持.xlsx和.xls格式'
    )
    sheet_name = forms.ChoiceField(
        label='Sheet名称',
        required=True,
        help_text='请先上传Excel文件'
    )
    rule_column = forms.ChoiceField(
        label='规则名称列',
        required=True,
        help_text='选择包含规则名称的列'
    )
    sql_column = forms.ChoiceField(
        label='执行SQL列',
        required=True,
        help_text='选择包含SQL语句的列'
    )
    host = forms.CharField(
        label='Host',
        max_length=100,
        initial='localhost'
    )
    port = forms.IntegerField(
        label='Port',
        initial=1521
    )
    service_name = forms.CharField(
        label='Service Name',
        max_length=100
    )
    schema = forms.CharField(
        label='Schema',
        max_length=100,
        required=False
    )
    user = forms.CharField(
        label='用户名',
        max_length=100
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput,
        max_length=100
    )