from django.shortcuts import render

# Create your views here.
import os
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings

from .exe_excel import exe_excel_main
from .forms import ExcelUploadForm
from .models import ExcelFile
from django.core.files.storage import FileSystemStorage


def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # 保存文件到数据库
            excel_file = form.save(commit=False)
            excel_file.original_filename = request.FILES['file'].name
            excel_file.save()

            # 处理Excel文件
            file_path = os.path.join(settings.MEDIA_ROOT, excel_file.file.name)

            # 使用pandas读取Excel文件
            try:
                # 读取Excel文件
                df = pd.read_excel(file_path)

                # 获取表头
                headers = list(df.columns)
                if '项目A' not in headers or '项目B' not in headers or '类型' not in headers or '医疗类别' not in headers or '诊断' not in headers or '输出结果' not in headers:
                    os.remove(file_path)
                    raise ValueError('缺失必要字段')

                # 生成结果
                df = exe_excel_main(file_path)

                # 保存
                df.to_excel(file_path, index=False)

                # 获取前10行数据
                preview_data = df.head(10).values.tolist()

                # 保存处理结果到session
                request.session['excel_data'] = {
                    'headers': headers,
                    'preview_data': preview_data,
                    'file_id': excel_file.id,
                    'original_filename': excel_file.original_filename
                }

                return redirect('excel_preview')

            except Exception as e:
                # 处理Excel读取错误
                form.add_error('file', f"处理Excel文件时出错: {str(e)}")
    else:
        form = ExcelUploadForm()

    return render(request, 'upload_excel.html', {'form': form})


def excel_preview(request):
    # 从session获取数据
    excel_data = request.session.get('excel_data')
    if not excel_data:
        return redirect('upload_excel')

    context = {
        'headers': excel_data['headers'],
        'preview_data': excel_data['preview_data'],
        'file_id': excel_data['file_id'],
        'original_filename': excel_data['original_filename']
    }

    return render(request, 'excel_preview.html', context)


def download_excel(request, file_id):
    try:
        excel_file = ExcelFile.objects.get(id=file_id)
        file_path = os.path.join(settings.MEDIA_ROOT, excel_file.file.name)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'attachment; filename="{excel_file.original_filename}"'
                return response

    except ExcelFile.DoesNotExist:
        pass

    return HttpResponse("文件不存在", status=404)