metres = []

def cmpp(p1, p2):
    p1 = p1.replace(' ', '').replace(' ', '').replace(' ','').replace(' ','')
    p2 = p2.replace(' ', '').replace(' ', '').replace(' ','').replace(' ','')
    if p1 != p2:
        return (p1, p2)
    return

def cmpe(x, y):
    n1, p1 = x
    n2, p2 = y
    if type(p1) != type(p2):
        return (n1, p1, p2)
    if isinstance(p1, str):
        r = cmpp(p1, p2)
        if r: return (n1, p1, p2)
        return
    assert isinstance(p1, list), p1
    try:
        return next(cmpp(p1[i], p2[i]) for i in range(len(p1)))
    except StopIteration:
        return


def compare(source1, source2):
    for i in range(min(len(source1), len(source2))):
        r = cmpe(source1[i], source2[i])
        if r: print(r)


def AddSamavrtta(name, pattern):
    metres.append([name, pattern])

def AddArdhasamavrtta(name, p1, p2):
    metres.append([name, [p1, p2]])

def AddVishamavrtta(name, p1, p2, p3, p4):
    metres.append([name, [p1, p2, p3, p4]])
