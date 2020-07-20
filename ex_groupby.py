import rx
from rx import of, operators as ops

def demo_group_by():
    '''tuple unpacking'''
    a = rx.of([
        {'id':1 , 'name': 'aaa'},
        {'id':2 , 'name': 'bbb'},
        {'id':1 , 'name': 'aaa'},
        {'id':1 , 'name': 'aaa'},
        {'id':2 , 'name': 'aaa'},
        ])

    a.pipe(
        ops.group_by(lambda x: x['id'], lambda x: x['name'], subject_mapper = rx.subject.ReplaySubject()),
        ops.to_iterable(),
    ).subscribe(print)




if __name__ == '__main__':
    #demo_zip()
    #demo_flatmap1()
    demo_group_by()