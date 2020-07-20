import rx
from rx import of, operators as op

def demo1():

    source = of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")

    composed = source.pipe(
        op.map(lambda s: len(s)),
        op.filter(lambda i: i >= 5)
    )
    composed.subscribe(lambda value: print("Received {0}".format(value)))

def demo_chains_op():
    of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
        op.map(lambda s: len(s)),
        op.filter(lambda i: i >= 5)
    ).subscribe(lambda value: print("Received {0}".format(value)))

def demo_custom_op():
    def length_more_than_5():
        return rx.pipe(
            op.map(lambda s: len(s)),
            op.filter(lambda i: i >= 5),
        )

    rx.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
        length_more_than_5()
    ).subscribe(lambda value: print("Received {0}".format(value)))

def demo_custom_op_manual():
    '''不使用op组合  太复杂'''
    def lowercase():
        '''op是无参函数, 构造'''
        def _lowercase(source):
            '''Observable -> Observable'''
            def subscribe(observer, scheduler = None):
                '''source被observer订阅的时候, source推送给observer的on_next变掉'''
                def on_next(value):
                    #消费得到推送之前转小写
                    observer.on_next(value.lower())

                return source.subscribe(
                    on_next,
                    observer.on_error,
                    observer.on_completed,
                    scheduler)
            return rx.create(subscribe)

        return _lowercase

    rx.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
            lowercase()
         ).subscribe(lambda value: print("Received {0}".format(value)))


if __name__ == '__main__':
    #demo1()
    demo_chains_op()
    demo_custom_op()
    demo_custom_op_manual()