'''
    数据源启动后，定时推送数据到 subject 供订阅
'''
import rx
from rx import of, operators as ops
from rx.subject import Subject
import time

from multiprocessing import Process
import time



def one_channel(para):
    print(f'开始处理通道{para}')
    #用rx +纯函数定义处理流程
    in_stream = Subject()

    out_stream = in_stream.pipe(
        #模拟简单处理
        ops.map(lambda data: len(data)),
        #ops.filter(lambda record_zoc1: record_zoc1 is not None)
    )


    #订阅处理 最终输出
    out_stream.subscribe(print)

    #实际开始
    while True:
        #模拟产生数据
        time.sleep(1)
        data = '哈哈哈'
        #推送到in_stream 进行梳理
        in_stream.on_next(data)



class DataSource(Process):
    '''暂时无法如此运行？
        TypeError: cannot pickle '_thread.RLock' object
        PermissionError: [WinError 5] 拒绝访问。
    '''
    def __init__(self, para):
        super(DataSource, self).__init__()
        self.para=para
        self.need_run = True
        self.is_done = False

        #用rx +纯函数定义处理流程
        self.in_stream = Subject()

        self.out_stream = self.in_stream.pipe(
            #模拟简单处理
            ops.map(lambda data: len(data)),
            #ops.filter(lambda record_zoc1: record_zoc1 is not None)
        )


        #订阅处理 最终输出
        self.out_stream.subscribe(print)


    def run(self):
        '''根据para开始产生数据'''
        print(f'开始处理通道{para}')
        while self.need_run:
            #模拟产生数据
            time.sleep(1)
            data = '哈哈哈'
            #推送到in_stream
            self.in_stream.on_next(data)
        #后处理完毕，可以退出
        self.is_done = True

    def terminate(self):
        self.need_run = False
        #等待run结束
        while not self.is_done:
            pass
        #结束
        super().terminate()


if __name__ == '__main__':

    p1= Process(target=one_channel,args=('1',))
    #p1 = DataSource('asdf')
    p1.start()
    print('主进程')
    time.sleep(5)
    print('主进程退出前关闭全部子进程')
    p1.terminate()        # 结束子进程