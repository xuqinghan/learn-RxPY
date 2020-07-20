import rx
from rx import of, operators as ops

def demo_flatmap1():
    '''tuple unpacking'''
    a = rx.of(1, 2, 3, 4)

    a.pipe(
        ops.flat_map(rx.of(1, 2, 3))
    ).subscribe(print)

def demo_flatmap2():
    '''tuple unpacking'''
    a = rx.of(1, 2, 3, 4)

    a.pipe(
        ops.flat_map(lambda x: range(0, x))
        #ops.flat_map(range)
    ).subscribe(print)


if __name__ == '__main__':
    #demo_zip()
    #demo_flatmap1()
    demo_flatmap2()