'''
    每个item带有时间戳 
    a v 处理时间不同。v有很大处理延迟
    最终仍然需要按源时间戳拼装
    其中，v需要处理成->i->t

    源         v1---a1---a2---v2---a3---a4---
    希望得到   i1-t1-a1---a2---i1-t2-a3--a4---

    结论：
    v的处理流程适合用rx， 但是根据ts排序，其实更适合的是优先队列！



'''

import rx
from rx import of, operators as op
from rx.subject import Subject
import time
from queue import PriorityQueue
import heapq


def v2i(item_v):
    #time.sleep(1)
    return {'ts':item_v['ts'], 'type': 'i', 'data': 'i'+item_v['data'][1:-1]}

def i2t(item_i):
    #time.sleep(2)
    return {'ts':item_i['ts'], 'type': 't', 'data': 't'+item_i['data'][1:-1]}

def demo1():
    '''先分流，再汇流？'''
    source = of(
    {'ts':0, 'type': 'v', 'data': 'v1'},
    {'ts':1, 'type': 'a', 'data': 'a1'},
    {'ts':2, 'type': 'a', 'data': 'a2'},
    {'ts':3, 'type': 'v', 'data': 'v2'},
    {'ts':4, 'type': 'a', 'data': 'a3'},
    {'ts':5, 'type': 'a', 'data': 'a4'},
    {'ts':6, 'type': 'v', 'data': 'v3'},
    )

    audio_stream = source.pipe(
        op.filter(lambda i: i['type'] == 'a') #过滤出a
    )

    img_stream = source.pipe(
        op.filter(lambda i: i['type'] == 'v'), #过滤出v
        op.map(v2i), 
    )

    target_stream = img_stream.pipe(
        op.map(i2t), 
    )

    #根据最慢的target_stream组装最终结果
    #全局变量
    ts_beg = -1

    composed_stream = Subject()

    push_to_composed = lambda item: composed_stream.on_next(item)

    def create_compose(item_t):
        '''把t前后时段的全部东西汇总，然后按timestamp排序，再输出
            但是不work
        '''
        ts_end = item_t['ts']

        items_in_time_seg = []
        #print(item_t)
        #添加到
        #push_to_composed(item_t)
        #composed_stream.on_next(item_t)
        target_before_stream = target_stream.pipe(
        op.filter(lambda i: i['ts'] == ts_end) #过滤出i
        )

        img_before_t1_stream = img_stream.pipe(
        op.filter(lambda i: i['ts'] == ts_end) #过滤出i
        )#.subscribe(push_to_composed)

        audio_before_t1_stream = audio_stream.pipe(
        op.filter(lambda i: ts_beg< i['ts'] <= ts_end) #过滤出i
        )#.subscribe(push_to_composed)
        #后面再次统一处理(比如汇总到records)
        obs_list = [img_before_t1_stream, target_before_stream, audio_before_t1_stream]
        records_stream = rx.merge(*obs_list)
        #records_stream.subscribe(lambda r: items_in_time_seg.append(r) )
        #print(items_in_time_seg)
        #records_stream.subscribe(lambda r: print(r) )
        records_stream.subscribe(lambda item: composed_stream.on_next(item))
        #按时间戳排序
        # result_list = sorted(items_in_time_seg, key=lambda x: x['ts'])
        # print(result_list)
        # for r in result_list:
        #     composed_stream.on_next(item)

        ts_beg = ts_end    



    composed_stream.subscribe(lambda value: print("Received {0}".format(value)))

    #必须最后才开始target推送
    target_stream.subscribe(create_compose)


# class PriorityQueue(object):
#     def __init__(self): 
#         self._queue = []  # 创建一个空列表用于存放队列
#         self._index = 0  # 指针用于记录push的次序

#     def put(self, item, priority):
#         """队列由（priority, index, item)形式的元祖构成"""
#         heapq.heappush(self._queue, (priority, self._index, item))
#         self._index += 1

#     def get(self):
#         return heapq.heappop(self._queue)[-1]  # 返回拥有最高优先级的项


def demo2_pq():
    samples = [('a1', 0),('v1', 0),('a2', 1),('a3', 2),('v2', 2)]
    pq = PriorityQueue()
    for data, p in samples:
        print(data, p)
        #如果是数组和tuple，以第一元素作为优先级
        pq.put((p, data))

    #print(pq._queue)
    for i in range(len(samples)):
        print(pq.get())


def demo3():
    '''先入优先队列，在t序列到达出队'''
    #数据源要是热的，保证每个队列
    source_stream = Subject()

    #优先队列
    pq = PriorityQueue()

    push_to_pq = lambda item: pq.put((item['ts'], item))


    audio_stream = source_stream.pipe(
        op.filter(lambda i: i['type'] == 'a') #过滤出a
    )
    audio_stream.subscribe(push_to_pq)

    img_stream = source_stream.pipe(
        op.filter(lambda i: i['type'] == 'v'), #过滤出v
        op.map(v2i), 
    )
    img_stream.subscribe(push_to_pq)

    target_stream = img_stream.pipe(
        op.map(i2t), 
    )

    #根据最慢的target_stream组装最终结果
    #全局变量

    composed_stream = Subject()

    def create_compose(item_t):
        '''把t前后时段的全部东西汇总，然后按timestamp排序，再输出
            但是不work
        '''
        ts_end = item_t['ts']
        #从优先队列中取出全部优先级小于等于ts_end的记录，拿出来的顺序就是最终输出的顺序
        print(ts_end)
        res = []

        while True:
            #优先队列中拿出来的顺序是ts从小到大的顺序
            ts, item = pq.get()
            if ts <= ts_end:
                res.append(item)
            else:
                #如果拿多了，要塞回去, 且停止继续拿
                pq.put((ts, item))
                break
            if pq.qsize() == 0:
                break
        #最后补上最慢的target
        res.append(item_t)            
        #print(f'时刻 {ts_end}, 队列中样本 {res}')
        #
        for item in res:
            composed_stream.on_next(item)


    target_stream.subscribe(create_compose)

    composed_stream.subscribe(lambda value: print("Received {0}".format(value)))


    #最后才开始推送数据
    for item in [
        {'ts':0, 'type': 'v', 'data': 'v1'},
        {'ts':1, 'type': 'a', 'data': 'a1'},
        {'ts':2, 'type': 'a', 'data': 'a2'},
        {'ts':3, 'type': 'v', 'data': 'v2'},
        {'ts':4, 'type': 'a', 'data': 'a3'},
        {'ts':5, 'type': 'a', 'data': 'a4'},
        {'ts':6, 'type': 'v', 'data': 'v3'},
    ]:
        source_stream.on_next(item)    


if __name__ == '__main__':
    #demo1()
    #demo2_pq()
    demo3()