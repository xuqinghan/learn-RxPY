import rx
from rx import operators as ops
import operator

def demo_zip():

    a = rx.of(1, 2, 3, 4)
    b = rx.of(2, 2, 4, 4)

    a.pipe(
        ops.zip(b), # returns a tuple with the items of a and b
        ops.map(lambda z: operator.mul(z[0], z[1]))
    ).subscribe(print)

def demo_starmap():
    '''tuple unpacking'''
    
    a = rx.of(1, 2, 3, 4)
    b = rx.of(2, 2, 4, 4)

    a.pipe(
        ops.zip(b),
        ops.starmap(operator.mul)
    ).subscribe(print)

if __name__ == '__main__':
    #demo_zip()
    demo_starmap()