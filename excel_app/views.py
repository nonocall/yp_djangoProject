from django.shortcuts import render

# Create your views here.
import os
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import zipfile
import io

from .exe_excel import exe_excel_main
from .forms import ExcelUploadForm, OracleRuleForm
from .models import ExcelFile, OracleRuleExecution, OracleRuleResult
from django.core.files.storage import default_storage


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


# ============ Oracle规则执行相关视图 ============

def oracle_rule_upload(request):
    """Oracle规则执行主页面"""
    if request.method == 'POST':
        # 处理执行请求
        excel_file = request.FILES.get('excel_file')
        sheet_name = request.POST.get('sheet_name')
        rule_column = request.POST.get('rule_column')
        sql_column = request.POST.get('sql_column')
        host = request.POST.get('host')
        port = request.POST.get('port')
        service_name = request.POST.get('service_name')
        schema = request.POST.get('schema')
        user = request.POST.get('user')
        password = request.POST.get('password')

        if not excel_file:
            return JsonResponse({'error': '请上传Excel文件'}, status=400)

        # 保存上传的Excel文件
        file_path = default_storage.save(f'oracle_rule_uploads/{excel_file.name}', excel_file)
        full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        try:
            # 读取Excel获取规则数据
            df = pd.read_excel(full_file_path, sheet_name=sheet_name)

            # 验证列存在
            if rule_column not in df.columns or sql_column not in df.columns:
                return JsonResponse({'error': f'指定的列不存在，可用列: {list(df.columns)}'}, status=400)

            # 创建执行记录
            execution = OracleRuleExecution.objects.create(
                file_name=excel_file.name,
                sheet_name=sheet_name,
                rule_column=rule_column,
                sql_column=sql_column,
                host=host,
                port=int(port),
                service_name=service_name,
                schema=schema or '',
                user=user,
                password=password,
                status='pending',
                total_rules=len(df),
                temp_file=file_path
            )
            execution.save()

            # 返回执行ID，让前端开始轮询
            return JsonResponse({
                'success': True,
                'execution_id': execution.id
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'oracle_rule_upload.html')


def get_excel_sheets(request):
    """获取Excel的sheet列表"""
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'}, status=405)

    excel_file = request.FILES.get('file')
    if not excel_file:
        return JsonResponse({'error': '请上传文件'}, status=400)

    try:
        # 保存临时文件
        file_path = default_storage.save(f'temp/{excel_file.name}', excel_file)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # 读取sheet列表
        xls = pd.ExcelFile(full_path)
        sheets = xls.sheet_names

        # 返回sheets和文件路径（用于后续获取列）
        return JsonResponse({
            'sheets': sheets,
            'file_path': file_path
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_excel_columns(request):
    """获取指定sheet的列名"""
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'}, status=405)

    data = json.loads(request.body)
    file_path = data.get('file_path')
    sheet_name = data.get('sheet_name')

    if not file_path or not sheet_name:
        return JsonResponse({'error': '缺少必要参数'}, status=400)

    try:
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        df = pd.read_excel(full_path, sheet_name=sheet_name)
        columns = list(df.columns)

        return JsonResponse({
            'columns': columns
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def execute_oracle_rules(request):
    """执行Oracle规则"""
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'}, status=405)

    execution_id = request.POST.get('execution_id')
    if not execution_id:
        return JsonResponse({'error': '缺少执行ID'}, status=400)

    try:
        execution = OracleRuleExecution.objects.get(id=execution_id)
    except OracleRuleExecution.DoesNotExist:
        return JsonResponse({'error': '执行记录不存在'}, status=404)

    # 开始执行
    execution.status = 'running'
    execution.save()

    file_path = os.path.join(settings.MEDIA_ROOT, execution.temp_file)

    try:
        # 读取Excel数据
        df = pd.read_excel(file_path, sheet_name=execution.sheet_name)

        # 获取规则名称和SQL列
        rule_names = df[execution.rule_column].tolist()
        sqls = df[execution.sql_column].tolist()

        # 尝试连接Oracle
        try:
            import oracledb
            dsn = oracledb.makedsn(
                execution.host,
                execution.port,
                service_name=execution.service_name
            )
            connection = oracledb.connect(
                user=execution.user,
                password=execution.password,
                dsn=dsn
            )
            conn = connection

            # 如果指定了Schema，切换到该Schema
            if execution.schema:
                cursor = conn.cursor()
                # Schema名需要大写，并用引号包裹
                schema_name = execution.schema.upper()
                cursor.execute(f'ALTER SESSION SET CURRENT_SCHEMA = "{schema_name}"')
                cursor.close()
        except Exception as conn_error:
            execution.status = 'error'
            execution.save()
            return JsonResponse({
                'error': f'数据库连接失败: {str(conn_error)}',
                'status': 'error'
            })

        # 创建zip文件
        zip_buffer = io.BytesIO()
        success_count = 0
        error_count = 0
        no_result_count = 0

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, (rule_name, sql) in enumerate(zip(rule_names, sqls)):
                sql = str(sql).strip()

                if not sql:
                    OracleRuleResult.objects.create(
                        execution=execution,
                        rule_name=str(rule_name),
                        sql_text='',
                        status='no_result',
                        error_message='SQL为空'
                    )
                    no_result_count += 1
                    continue

                try:
                    # 执行SQL
                    cursor = conn.cursor()
                    cursor.execute(sql)

                    # 获取列名
                    columns = [col[0] for col in cursor.description] if cursor.description else []

                    # 获取结果
                    results = cursor.fetchall()
                    cursor.close()

                    if results:
                        # 创建结果DataFrame
                        result_df = pd.DataFrame(results, columns=columns)

                        # 保存Excel到内存
                        excel_buffer = io.BytesIO()
                        result_df.to_excel(excel_buffer, index=False)
                        excel_buffer.seek(0)

                        # 添加到zip
                        safe_name = str(rule_name).replace('/', '_').replace('\\', '_')
                        zip_file.writestr(f'{safe_name}.xlsx', excel_buffer.read())

                        # 保存结果记录
                        OracleRuleResult.objects.create(
                            execution=execution,
                            rule_name=str(rule_name),
                            sql_text=sql,
                            status='success',
                            row_count=len(results)
                        )
                        success_count += 1
                    else:
                        # 无结果
                        OracleRuleResult.objects.create(
                            execution=execution,
                            rule_name=str(rule_name),
                            sql_text=sql,
                            status='no_result'
                        )
                        no_result_count += 1

                except Exception as sql_error:
                    OracleRuleResult.objects.create(
                        execution=execution,
                        rule_name=str(rule_name),
                        sql_text=sql,
                        status='error',
                        error_message=str(sql_error)
                    )
                    error_count += 1

                # 更新进度
                execution.completed_rules = i + 1
                execution.save()

        # 关闭连接
        conn.close()

        # 保存zip文件
        zip_buffer.seek(0)
        from django.core.files.base import ContentFile
        execution.zip_file.save(f'results_{execution.id}.zip', ContentFile(zip_buffer.read()))

        # 更新状态
        execution.status = 'completed'
        execution.save()

        return JsonResponse({
            'success': True,
            'status': 'completed',
            'total': execution.total_rules,
            'success_count': success_count,
            'error_count': error_count,
            'no_result_count': no_result_count
        })

    except Exception as e:
        execution.status = 'error'
        execution.error_message = str(e)
        execution.save()
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        })


def get_execution_progress(request, execution_id):
    """获取执行进度"""
    try:
        execution = OracleRuleExecution.objects.get(id=execution_id)

        response = {
            'status': execution.status,
            'total': execution.total_rules,
            'completed': execution.completed_rules,
            'progress': round(execution.completed_rules / execution.total_rules * 100, 2) if execution.total_rules > 0 else 0
        }

        # 如果有错误，添加错误信息
        if hasattr(execution, 'error_message') and execution.error_message:
            response['error_message'] = execution.error_message

        return JsonResponse(response)

    except OracleRuleExecution.DoesNotExist:
        return JsonResponse({'error': '执行记录不存在'}, status=404)


def download_zip(request, execution_id):
    """下载结果zip"""
    try:
        execution = OracleRuleExecution.objects.get(id=execution_id)

        if not execution.zip_file:
            return HttpResponse("结果文件不存在", status=404)

        file_path = execution.zip_file.path

        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="oracle_rule_results_{execution_id}.zip"'
                return response

    except OracleRuleExecution.DoesNotExist:
        pass

    return HttpResponse("文件不存在", status=404)


def execution_history(request):
    """执行历史记录"""
    from django.db.models import Count, Q

    executions = OracleRuleExecution.objects.annotate(
        success_count=Count('results', filter=Q(results__status='success')),
        no_result_count=Count('results', filter=Q(results__status='no_result')),
        error_count=Count('results', filter=Q(results__status='error'))
    ).order_by('-created_at')

    return render(request, 'oracle_rule_history.html', {
        'executions': executions
    })