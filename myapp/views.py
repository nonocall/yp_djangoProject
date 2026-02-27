from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from myapp.normal.limit_diag_mz import this_main_mz_diag
from myapp.normal.limit_diag_zy import this_main_zy_diag
from myapp.normal.limit_room import limit_room_mz, limit_room_zy
from myapp.normal.map_name import get_oracle_table_names, this_main_map_name, get_ora_table_rows
from myapp.normal.over_level_mz import this_main_mz_level
from myapp.normal.over_level_zy import this_main_zy_level
from myapp.normal.over_num_mz import this_main_mz_num
from myapp.normal.over_num_zy import this_main_zy_num
from myapp.normal.sametime_charge_mz import this_main_mz_sametime
from myapp.normal.sametime_charge_zy import this_main_zy_sametime

@csrf_exempt
def limit_diag(request):
    if request.POST.get('rule_category', '') == 'zy':
        PA = request.POST.get('project', '')
        diag = request.POST.get('diag', '')
        reversed_string = this_main_zy_diag(PA, diag)
        # return render(request, 'charge_same_time.html', {'reversed_string': reversed_string})
        return JsonResponse({'reversed_string': reversed_string})
    elif request.POST.get('rule_category', '') == 'mz':
        PA = request.POST.get('project', '')
        diag = request.POST.get('diag', '')
        reversed_string = this_main_mz_diag(PA, diag)
        # return render(request, 'charge_same_time.html', {'reversed_string': reversed_string})
        return JsonResponse({'reversed_string': reversed_string})
    else:
        return render(request, 'limit_diag.html')

@csrf_exempt
def limit_room(request):
    if request.POST.get('rule_category', '') == 'mz':
        yes_or_no = request.POST.get('yes_or_no', '')
        room = request.POST.get('room', '')
        reversed_string = limit_room_mz(yes_or_no, room)
        return JsonResponse({'reversed_string': reversed_string})
    elif request.POST.get('rule_category', '') == 'zy':
        yes_or_no = request.POST.get('yes_or_no', '')
        room = request.POST.get('room', '')
        reversed_string = limit_room_zy(yes_or_no, room)
        return JsonResponse({'reversed_string': reversed_string})
    else:
        return render(request, 'limit_room.html')

def same_time(request):
    if request.POST.get('rule_category', '')== 'zy':
        PA = request.POST.get('projectA', '')
        PB = request.POST.get('projectB', '')
        diag = request.POST.get('diag', '')
        reversed_string = this_main_zy_sametime(PA,PB,diag)
        #return render(request, 'charge_same_time.html', {'reversed_string': reversed_string})
        return JsonResponse({'reversed_string': reversed_string})
    elif request.POST.get('rule_category', '')== 'mz':
        PA = request.POST.get('projectA', '')
        PB = request.POST.get('projectB', '')
        diag = request.POST.get('diag', '')
        reversed_string = this_main_mz_sametime(PA, PB,diag)
        # return render(request, 'charge_same_time.html', {'reversed_string': reversed_string})
        return JsonResponse({'reversed_string': reversed_string})
    else:
        return render(request, 'charge_same_time.html')
def over_num(request):
    if request.POST.get('rule_category', '')== 'zy':
        PA = request.POST.get('projectA', '')
        diag = request.POST.get('diagA', '')
        if request.POST.get('num', '') == '':
            reversed_string = this_main_zy_num(PA,diag)+"1"
        else:
            reversed_string = this_main_zy_num(PA, diag) + request.POST.get('num', '')
        return JsonResponse({'reversed_string': reversed_string})
    if request.POST.get('rule_category', '')== 'mz':
        PA = request.POST.get('projectA', '')
        diag = request.POST.get('diagA', '')
        if request.POST.get('num', '')== '':
            reversed_string = this_main_mz_num(PA, diag)+'1'
        else:
            reversed_string = this_main_mz_num(PA, diag) + request.POST.get('num', '')
        return JsonResponse({'reversed_string': reversed_string})
    return render(request, 'over_num.html')

def over_level(request):
    if request.POST.get('rule_category', '')== 'zy':
        PA = request.POST.get('projectA', '')
        diag = request.POST.get('diagA', '')
        reversed_string = this_main_zy_level(PA, diag)
        return JsonResponse({'reversed_string': reversed_string})
    if request.POST.get('rule_category', '')== 'mz':
        PA = request.POST.get('projectA', '')
        diag = request.POST.get('diagA', '')
        reversed_string = this_main_mz_level(PA, diag)
        return JsonResponse({'reversed_string': reversed_string})
    return render(request, 'over_level.html')

@csrf_exempt
def map_name_1(request):
    if request.method == 'POST':
        user = request.POST.get('user', '')
        # 判空
        if user== '' :
            return JsonResponse({'table_names': '暂无数据'})
        else:
            connection_string = f"{user}/{user}@192.168.28.10:1521/orcl"
            table_names = get_oracle_table_names(connection_string)
            return JsonResponse({'table_names':table_names})
    else:
        table_names = "暂无数据"

    context = {'table_names': table_names}
    return render(request, 'map_name.html',context)


@csrf_exempt
def map_name_2(request):
    if request.method == 'POST':
        user = request.POST.get('user', '')
        Table_O = request.POST.get('Table_O', '')
        # 判空
        if Table_O== '' :
            return JsonResponse({'cols': '暂无数据'})
        # 返回sql
        else :
            connection_string = f"{user}/{user}@192.168.28.10:1521/orcl"
            cols = get_ora_table_rows(connection_string,user,Table_O)
            return JsonResponse({'cols': cols})
    else:
        cols = "暂无数据"

    context = {'cols': cols}
    return render(request, 'map_name.html',context)

@csrf_exempt
def map_name_3(request):
    if request.method == 'POST':
        user = request.POST.get('user','')
        Table_D = request.POST.get('Table_D', '')
        Table_O = request.POST.get('Table_O', '')
        connection_string = f"{user}/{user}@192.168.28.10:1521/orcl"
        resultText = this_main_map_name(connection_string,user,Table_D,Table_O,request.POST)
        return JsonResponse({'resultText':resultText})

def map_name(request, tag):
    context = {
        'tag': tag,
    }
    return render(request, 'map_name.html',context)


def index(request):
    return render(request, 'base.html',context=None)

