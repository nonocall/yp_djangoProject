import os
import shutil

import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render, redirect

from yp_djangoProject import settings
from yp_djangoProject.settings import BASE_DIR
from zip_app.forms import ExcelUploadForm
import zipfile
import tempfile

from .models import ZipFile



# def zip_index(request):
#     return HttpResponse("Hello from myapp!")

def upload_zip(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            zip_file = form.save(commit=False)
            zip_file.original_filename = request.FILES['file'].name
            zip_file.save()

            uploaded_path = zip_file.file.path
            # 规则映射表的相对路径（相对于项目根目录或当前工作目录）
            MAPPING_FILE_PATH = './规则来源映射表.xlsx'

            try:
                headers = []
                preview_data = []
                updated_excel_bytes = None  # 用于存储更新后的Excel二进制数据

                # 读取规则映射表
                if not os.path.exists(MAPPING_FILE_PATH):
                    raise FileNotFoundError(f"找不到规则映射表: {MAPPING_FILE_PATH}")

                df_mapping = pd.read_excel(MAPPING_FILE_PATH)
                # 确保必要的列存在
                if '规则名称' not in df_mapping.columns or '规则来源' not in df_mapping.columns:
                    raise ValueError("规则映射表必须包含 '规则名称' 和 '规则来源' 列")

                if uploaded_path.lower().endswith('.zip'):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # 解压原压缩包
                        with zipfile.ZipFile(uploaded_path, 'r') as zf:
                            zf.extractall(tmpdir)

                        # 查找汇总表
                        excel_path = None
                        excel_relative_path = None  # 记录在压缩包内的相对路径
                        for root, dirs, files in os.walk(tmpdir):
                            for f in files:
                                if f.lower().endswith(('汇总.xlsx', '汇总.xls')):
                                    excel_path = os.path.join(root, f)
                                    # 计算相对路径（用于后续写回压缩包）
                                    excel_relative_path = os.path.relpath(excel_path, tmpdir)
                                    break
                            if excel_path:
                                break

                        if not excel_path:
                            raise FileNotFoundError("压缩包内未找到'汇总.xlsx'或'汇总.xls'文件")

                        # 读取汇总表
                        df_summary = pd.read_excel(excel_path)

                        # 合并数据：左连接，根据规则名称匹配规则来源
                        df_merged = df_summary.merge(
                            df_mapping[['规则名称', '规则来源']],
                            on='规则名称',
                            how='left'
                        )

                        # 调整列顺序：将规则来源放到规则名称后面（可选）
                        cols = list(df_merged.columns)
                        if '规则来源' in cols and '规则名称' in cols:
                            cols.remove('规则来源')
                            rule_name_idx = cols.index('规则名称')
                            cols.insert(rule_name_idx + 1, '规则来源')
                            df_merged = df_merged[cols]

                        # 删除旧文件
                        os.remove(excel_path)

                        # 保存更新后的Excel到临时文件
                        df_merged.to_excel(excel_path, index=False)



                        # 准备预览数据
                        headers = list(df_merged.columns)
                        preview_data = df_merged.head(10).values.tolist()

                        # 重新打包压缩包（替换原文件）
                        new_zip_path = uploaded_path + '.tmp'
                        with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf_new:
                            for root, dirs, files in os.walk(tmpdir):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, tmpdir)
                                    zf_new.write(file_path, arcname)

                        # 替换原压缩包
                        shutil.move(new_zip_path, uploaded_path)

                        # 同步更新数据库中的文件信息（可选）
                        # zip_file.file.size = os.path.getsize(uploaded_path)
                        zip_file.save()

                elif uploaded_path.lower().endswith(('.xlsx', '.xls')):
                    # 直接上传Excel文件的情况
                    df_summary = pd.read_excel(uploaded_path)

                    # 合并数据
                    df_merged = df_summary.merge(
                        df_mapping[['规则名称', '规则来源']],
                        on='规则名称',
                        how='left'
                    )

                    # 调整列顺序
                    cols = list(df_merged.columns)
                    if '规则来源' in cols and '规则名称' in cols:
                        cols.remove('规则来源')
                        rule_name_idx = cols.index('规则名称')
                        cols.insert(rule_name_idx + 1, '规则来源')
                        df_merged = df_merged[cols]

                    # 覆盖原文件
                    df_merged.to_excel(uploaded_path, index=False)

                    headers = list(df_merged.columns)
                    preview_data = df_merged.head(10).values.tolist()

                # 保存到session
                request.session['zip_data'] = {
                    'headers': headers,
                    'preview_data': preview_data,
                    'file_id': zip_file.id,
                    'original_filename': zip_file.original_filename
                }
                return redirect('zip_preview')

            except Exception as e:
                form.add_error('file', f"处理文件时出错: {str(e)}")
    else:
        form = ExcelUploadForm()

    return render(request, 'upload_excel.html', {'form': form})


def zip_preview(request):
    # 从session获取数据
    zip_data = request.session.get('zip_data')
    if not zip_data:
        return redirect('upload_zip')

    context = {
        'headers': zip_data['headers'],
        'preview_data': zip_data['preview_data'],
        'file_id': zip_data['file_id'],
        'original_filename': zip_data['original_filename']
    }

    return render(request, 'zip_preview.html', context)


import os
import urllib.parse
from django.http import HttpResponse, HttpResponseNotFound


def download_zip(request, file_id):
    try:
        zip_file = ZipFile.objects.get(id=file_id)
        file_path = zip_file.file.path  # 直接使用 model 的 path 属性，更可靠

        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                # 正确的 MIME 类型
                response = HttpResponse(f.read(), content_type='application/zip')

                # 处理中文文件名：RFC 5987 编码
                original_filename = zip_file.original_filename
                # ASCII 部分
                ascii_filename = original_filename.encode('ascii', 'ignore').decode()
                # UTF-8 编码部分（用于现代浏览器）
                utf8_filename = urllib.parse.quote(original_filename)

                # 组合 Content-Disposition，兼容各种浏览器
                response['Content-Disposition'] = (
                    f"attachment; "
                    f'filename="{ascii_filename}"; '  # 旧浏览器回退
                    f"filename*=UTF-8''{utf8_filename}"  # 现代浏览器
                )

                # 可选：添加文件大小，支持进度条
                response['Content-Length'] = os.path.getsize(file_path)

                return response

    except ZipFile.DoesNotExist:
        pass

    return HttpResponseNotFound("文件不存在")