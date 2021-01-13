'''
裁决发生在"作战时间暂停"的时候
1 停表
2 冻结state，裁
3 修改state  决
4 走表

天梁 = "判" "量(罪名) + 裁(刑名)"
天刑 = "决" execute 执行

"判"：
    1 "量(罪名)" = if else cond switch... check各构成要件 requirements
    2 "裁(刑名)": 给出裁定结果
"决"：
    1 执行   修改状态
    2 保存   持久化
    3 通告   通信，发送结果

judge过程要集中完成"量"+"裁", 但是剥离掉执行过程!. 
if condition1: #量
    record1 = cal1(para): #裁
elif condition2: #量
    record1 = cal1(para): #裁
else:
    record1 = None
return record1

rx  用纯函数实现：从不可变数据流1->不可变数据流2
"XX改变"的事件，要落实到事件上：CUD记录！
问题是：副作用：在何时执行？

1. side effects 副作用？

如何保证 决 和 量 之间的时序？
s0->(量1-裁1)-sA->(决1)->sA
s0->(量2-裁2)-sB->(决2)->sB

(量3-裁3)-(决3)->sC

触发条件：merge(s1, s2)
本级"判"  ops(fn3)
裁决结果： s3

[量3]需要进行查询，必须 在[决1 决2]之后再进行!

用 ops.do 显式 进行 [决] 的执行！

2. 

裁决的组织：
按operation： 过程式？但也可以用ops pipe串起来！
    移动：
        位置改变 #无条件
        uid zoc改变 #因为位置改变
        指挥范围改变
        ownership 改变
        ……
    攻击：
        hp减血 #hp可能改变
        撤退。#位置可能改变
        uid zoc改变 #因为[血量, hp]都可能改变
        adm改变
        ……

    游戏中的裁决。往往只需要对齐时序后执行一次! 

最适合的还是按这种方式设计？

而不是以zoc为中心？
  s0  导致 sA sB 产生时，必须对齐sA sB 时序。
    时间不定，产生结果不定（不改变，本身也是结果！）
    但是只需裁决C 执行1次！而不是两次！

    类似 
        s0 触发裁决
        并行[s血量, s位置]
        同步等待并行结束 join
        (量3) 执行1次！

需要“XX不变” 产生这个信号！ 保证 stream的zip

“XX不变” 不需要产生记录，不需要发送

'''


from datetime import datetime
import rx
from rx import of, operators as ops
from rx.subject import Subject
import time
import random

#------纯函数 注入game-------------

#外部状态，量的时候需要查询，决的时候需要修改
states = {'A': 0, 'B': 0, 'C': 0, 'D': 0}


def 天梁A(para):
    '''
        s_in  某一上级裁决结果？或者初始触发，无条件裁决。（每回合裁决补给）
        查XX改A
    '''
    #print(message_location)
    print(f'{datetime.now()} A量裁 开始')
    #裁决时间短
    time.sleep(1)
    print(f'{datetime.now()} A量裁 结束')
    #简化版的量裁结果
    if random.randint(1, 6) <= 0:
        #不变
        return {'kind': 'N',
                'attr': 'A'}
    else:
        return {'tx': datetime.now(),
                'kind': 'U',
                'attr': 'A',
                'from': 0,   #量的结果。保证执行时不再查询！
                'to': 1,  
                }

def 天梁B(para):
    '''
        查XX改B
    '''
    #print(message_location)
    print(f'{datetime.now()} B量裁 开始')
    #裁决时间长
    time.sleep(2)
    print(f'{datetime.now()} B量裁 结束')
    if random.randint(1, 6) <= 0:
        #不变
        return {'kind': 'N',
                'attr': 'B'}
    else:
        #简化版的量裁结果
        return {'tx': datetime.now(),
                'kind': 'U',
                'attr': 'B',
                'from': 0,
                'to': 2,
                }


def 天梁C(args):
    '''
        各改变条件
        查A B 改 C
        如果 A B 的记录是U 改变，则用 res['to']代替去states中查询
        如果不变，则需要去states['A']中实际查询
    '''
    print(f'{datetime.now()} C量裁 开始')
    res_A, res_B = args
    print('天梁C res_A', res_A)
    print('天梁C res_B', res_B)
    #print(message_location)


    for res1 in args:
        attr = res1['attr']
        kind = res1['kind']
        #print(res1, attr, kind)
        if kind == 'U':
            #此时，states已经改变
            assert states[attr] == res1['to']
            value_new = res1['to']
        else:
            value_new = states[attr]

        if attr == 'A':
            value_A = value_new
        if attr == 'B':
            value_B = value_new

    #裁决时间立决
    time.sleep(1)
    value_new = value_A + value_B
    print(f'{datetime.now()} C量裁 结束')
    #简化版的量裁结果
    return {'tx': datetime.now(),
            'kind': 'U',
            'attr': 'C',
            'from': 0,
            'to': value_new,
            }


def 天梁D(para):
    '''
        在C之后
    '''
    #print(message_location)
    print(f'{datetime.now()} D量裁 开始')
    #裁决时间长
    time.sleep(1)
    print(f'{datetime.now()} D量裁 结束')
    return {'tx': datetime.now(),
            'kind': 'U',
            'attr': 'D',
            'from': states['D'],
            'to': para['to']*2,
            }


def 决(res1):
    '''副作用！修改状态'''
    if res1['kind'] == 'U':
        print(f'{datetime.now()} 执行 指令 {res1}')
        states[res1['attr']] = res1['to']


# #作为源的流, 改变的源头
# location_changed_stream = Subject()
# #作为源的流, 改变的源头
# survival_changed_stream = Subject()

# #zoc可能根据2种情况发生改变  位置改变, hp改变
# obs_list = [location_changed_stream, survival_changed_stream]
# update_zoc_stream = rx.merge(*obs_list)

operation_maneuver = Subject()
# update_zoc -> zoc_changed  如果没更新,则不产生
# 不订阅subject, 而是用op 改变成其他stream, 过滤掉zoc没有改变的情况

#结果作为subject 作为hot source
subject_dict = {name: Subject() for name in ['A', 'B', 'C', 'D']}


#临时的流仅供subject订阅，不需要命名
temp_stream = operation_maneuver.pipe(
#A_check_stream = operation_maneuver.pipe(
    ops.map(天梁A),
    ops.do_action(决)
).subscribe(subject_dict['A'])


operation_maneuver.pipe(
    ops.map(天梁B),
    ops.do_action(决)
).subscribe(subject_dict['B'])


#C_trigger_stream.subscribe(rx.zip(*[A_check_stream, B_check_stream]))
#临时的流不需要保存
rx.zip(*[subject_dict['A'], subject_dict['B']]).pipe(
    ops.map(天梁C),
    ops.do_action(决)
).subscribe(subject_dict['C'])

#C之后增加D
subject_dict['C'].pipe(
    ops.map(天梁D),
    ops.do_action(决)
).subscribe(subject_dict['D'])


records_stream = Subject()

#后面再次统一处理 过滤掉不变N的记录
rx.merge(*(subject_dict.values())).pipe(
    ops.filter(lambda x: x['kind'] != 'N'),
).subscribe(records_stream)


#模拟汇总
records = []
def handle_records(record1):
    records.append(record1)

records_stream.subscribe(handle_records)

#print(d)
#产生数据 可以没有数据！一样触发裁决（回合开始结束时的XX鉴定！）
# message_location = {'tx_time': datetime.now().isoformat(),
#             'kind': 'U',
#             'table': 'location',
#             'pk': 1,
#             'attr': 'pos',
#             'v_from': None,
#             'v_to': '0717',
#             'war_time': 'H+1',
#             }
message_location = {}

#A_check_stream.subscribe(print)
#C_check_stream.subscribe(print)
print('触发1次operation_maneuver裁决')
operation_maneuver.on_next(message_location)
print('1次operation_maneuver裁决后')

#后处理：
#record需要排序，转格式
def post_process(records):
    print('后处理')
    #需要排序
    print('排序前', records)
    records = sorted(records, key=lambda x: x['tx'])
    print('排序后', records)
    #保存
    #发送走


post_process(records)

# #改变生存状态
# survival_changed_stream.on_next({'tx_time': datetime.now().isoformat(),
#                                 'kind': 'U',
#                                 'table': 'survival',
#                                 'pk': 1,
#                                 'attr': 'hp',
#                                 'v_from': 2,
#                                 'v_to': 1,
#                                 'war_time': 'H+2',
#                                 })


# print('hp改变指令后')
# print(records)


# #产生另一个数据
# message_location = {'tx_time': datetime.now().isoformat(),
#             'kind': 'U',
#             'table': 'location',
#             'pk': 1,
#             'attr': 'pos',
#             'v_from': None,
#             'v_to': '0912',
#             'war_time': 'H+3',
#             }

# location_changed_stream.on_next(message_location)
# print('第2次移动指令后')
# print(records)

#

#d.dispose()
