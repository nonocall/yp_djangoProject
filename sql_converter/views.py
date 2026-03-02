import os
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings

from .sql_parser import convert_sql_file, convert_wm_concat_to_listagg
from .forms import SQLConverterUploadForm
from .models import SQLConverterFile


def upload_sql_excel(request):
    """上传Excel文件并转换SQL"""
    if request.method == 'POST':
        form = SQLConverterUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # 保存文件到数据库
            sql_file = form.save(commit=False)
            sql_file.original_filename = request.FILES['file'].name
            sql_file.save()

            # 处理Excel文件
            file_path = os.path.join(settings.MEDIA_ROOT, sql_file.file.name)

            try:
                # 读取并转换Excel文件
                df, conversion_count = convert_sql_file(file_path)

                # 保存转换后的文件
                converted_filename = f"converted_{sql_file.original_filename}"
                converted_path = os.path.join(settings.MEDIA_ROOT, 'sql_converter_files', converted_filename)
                
                # 确保目录存在
                os.makedirs(os.path.dirname(converted_path), exist_ok=True)
                
                # 保存转换后的Excel
                df.to_excel(converted_path, index=False)
                
                # 更新数据库记录
                sql_file.converted_filename = converted_filename
                sql_file.conversion_count = conversion_count
                sql_file.save()

                # 获取表头和预览数据
                headers = list(df.columns)
                preview_data = df.head(10).values.tolist()

                # 保存处理结果到session
                request.session['sql_converter_data'] = {
                    'headers': headers,
                    'preview_data': preview_data,
                    'file_id': sql_file.id,
                    'original_filename': sql_file.original_filename,
                    'converted_filename': converted_filename,
                    'conversion_count': conversion_count
                }

                return redirect('sql_converter_preview')

            except Exception as e:
                # 处理Excel读取错误
                form.add_error('file', f"处理Excel文件时出错: {str(e)}")
    else:
        form = SQLConverterUploadForm()

    return render(request, 'upload_sql_converter.html', {'form': form})


def sql_converter_preview(request):
    """预览转换结果"""
    # 从session获取数据
    converter_data = request.session.get('sql_converter_data')
    if not converter_data:
        return redirect('upload_sql_converter')

    context = {
        'headers': converter_data['headers'],
        'preview_data': converter_data['preview_data'],
        'file_id': converter_data['file_id'],
        'original_filename': converter_data['original_filename'],
        'converted_filename': converter_data['converted_filename'],
        'conversion_count': converter_data['conversion_count']
    }

    return render(request, 'sql_converter_preview.html', context)


def download_converted_excel(request, file_id):
    """下载转换后的Excel文件"""
    try:
        sql_file = SQLConverterFile.objects.get(id=file_id)
        converted_path = os.path.join(settings.MEDIA_ROOT, 'sql_converter_files', sql_file.converted_filename)

        if os.path.exists(converted_path):
            with open(converted_path, 'rb') as file:
                response = HttpResponse(
                    file.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{sql_file.converted_filename}"'
                return response

    except SQLConverterFile.DoesNotExist:
        pass

    return HttpResponse("文件不存在", status=404)


def download_original_excel(request, file_id):
    """下载原始Excel文件"""
    try:
        sql_file = SQLConverterFile.objects.get(id=file_id)
        file_path = os.path.join(settings.MEDIA_ROOT, sql_file.file.name)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                response = HttpResponse(
                    file.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{sql_file.original_filename}"'
                return response

    except SQLConverterFile.DoesNotExist:
        pass

    return HttpResponse("文件不存在", status=404)
