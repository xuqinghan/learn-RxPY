import rx, operator as op

def demo_merge1():

    obs1 = rx.from_([1, 2, 3, 4])
    obs2 = rx.from_([5, 6, 7, 8])

    res = rx.merge(obs1, obs2)
    res.subscribe(print)

def demo_merge2():

    obs1 = rx.from_([1, 2, 3, 4])
    obs2 = rx.from_([5, 6, 7, 8])

    obs_list = [obs1, obs2]

    res = rx.merge(*obs_list)
    res.subscribe(print)

if __name__ == '__main__':
    demo_merge1()
    demo_merge2()

