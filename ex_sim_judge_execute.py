from datetime import datetime
import rx
from rx import of, operators as ops
from rx.subject import Subject
import time


#------纯函数 注入game-------------
def judge_zoc(game, message):
    '''
        "量" = check 构成要件 requirements
        "裁": 给出裁定结果
        judge过程要集中完成"量"+"裁", 但是剥离掉执行过程!. 
        if condition1: #量
            record1 = cal1(para): #裁
        elif condition2: #量
            record1 = cal1(para): #裁
        else:
            record1 = None
        return record1
        
        天梁="量+裁"
        天刑= "决" execute 执行

        位置改变 hp改变 都可能改变zoc, 产生zoc改变记录
        可能没有改变, 返回None
    '''
    #print(message_location)
    record_res1 = None
    if message['table'] == 'survival':
        if message['v_to'] <= 1:
            #裁决时间短
            time.sleep(1)
            #zoc改为空, 模拟残血不产生zoc
            record_res1 = {'tx_time': datetime.now().isoformat(),
                'kind': 'U',
                'table': 'zoc',
                'pk': 1,
                'attr': 'gids',
                'v_from': None,
                'v_to': [],
                'war_time': message['war_time'],
                }

    elif message['table'] == 'location':
        if message['v_to'] == '0717':
            #裁决时间长
            time.sleep(5)
            #模拟zoc更新 创建zoc U 记录
            record_res1 = {'tx_time': datetime.now().isoformat(),
                'kind': 'U',
                'table': 'zoc',
                'pk': 1,
                'attr': 'gids',
                'v_from': None,
                'v_to': ['0717', '0718', '0818'],
                'war_time': message['war_time'],
                }

    return record_res1


#模拟1个游戏整体对象
game= 1

#作为源的流, 改变的源头
location_changed_stream = Subject()
#作为源的流, 改变的源头
survival_changed_stream = Subject()

#zoc可能根据2种情况发生改变  位置改变, hp改变
obs_list = [location_changed_stream, survival_changed_stream]
update_zoc_stream = rx.merge(*obs_list)

# update_zoc -> zoc_changed  如果没更新,则不产生
# 不订阅subject, 而是用op 改变成其他stream, 过滤掉zoc没有改变的情况
zoc_changed_stream = update_zoc_stream.pipe(
    #装入game对象
    ops.map(lambda record1: judge_zoc(game, record1)),
    ops.filter(lambda record_zoc1: record_zoc1 is not None)
)




#后面再次统一处理(比如汇总到records)
obs_list = [location_changed_stream, survival_changed_stream, zoc_changed_stream]
records_stream = rx.merge(*obs_list)


def execute(game, message):
    '''天刑刽子手 只负责裁! 不产生新结果
        可能消耗时间
    '''
    if message['table'] == 'zoc':
        #假如执行时间长
        print('执行 game={game}, zoc指令', message)
        time.sleep(1)
        print('zoc执行完毕')
    else:
        print(f'执行 game={game}, 其他指令{message}')

#模拟执行
records_stream.subscribe(lambda x: execute(game, x))
#模拟汇总
records = []
records_stream.subscribe(lambda x: records.append(x))



#print(d)
#产生数据
#位置改变
message_location = {'tx_time': datetime.now().isoformat(),
            'kind': 'U',
            'table': 'location',
            'pk': 1,
            'attr': 'pos',
            'v_from': None,
            'v_to': '0717',
            'war_time': 'H+1',
            }

location_changed_stream.on_next(message_location)

print('第1次移动指令后')
print(records)

#改变生存状态
survival_changed_stream.on_next({'tx_time': datetime.now().isoformat(),
                                'kind': 'U',
                                'table': 'survival',
                                'pk': 1,
                                'attr': 'hp',
                                'v_from': 2,
                                'v_to': 1,
                                'war_time': 'H+2',
                                })


print('hp改变指令后')
print(records)


#产生另一个数据
message_location = {'tx_time': datetime.now().isoformat(),
            'kind': 'U',
            'table': 'location',
            'pk': 1,
            'attr': 'pos',
            'v_from': None,
            'v_to': '0912',
            'war_time': 'H+3',
            }

location_changed_stream.on_next(message_location)
print('第2次移动指令后')
print(records)

#

#d.dispose()
