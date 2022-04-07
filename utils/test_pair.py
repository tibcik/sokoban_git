from pickle import TUPLE1
import pytest
from . import *

pairs = (
    (0,0),(1,0),(0,1),(1,1),
    (1,5),(5,1),(-12,-12),(-10,10),
    (1.,1.),(1.,5.),(5.,1.),(-12.,-12.),(-10.,10.),(1.5,2.5)
    )

def test_bad_init():
    with pytest.raises(AssertionError) as e:
        p = Pair(10,'b')
    with pytest.raises(TypeError) as e:
        p = Pair("a",10)
        p = Pair({'p1': 10, 'p2': 20})

def test_init_num():
    global pairs
    for point in pairs:
        p = Pair(point[0], point[1])
        assert p.p1 == point[0] and p.p2 == point[1]

def test_init_subscribed():
    global pairs
    for point in pairs:
        p = Pair(point)
        assert p.p1 == point[0] and p.p2 == point[1]

def test_add():
    global pairs
    for p1 in range(len(pairs)):
        for p2 in range(len(pairs)):
            tp1 = Pair(pairs[p1])
            tp2 = Pair(pairs[p2])
            p = tp1 + tp2
            assert (p.p1 == pairs[p1][0] + pairs[p2][0] and
                p.p2 == pairs[p1][1] + pairs[p2][1]), (f"{tp1} + {tp2} != {p}")
            tp2 = pairs[p2][0]
            p = tp1 + tp2
            assert (p.p1 == pairs[p1][0] + pairs[p2][0] and
                p.p2 == pairs[p1][1] + pairs[p2][0]), (f"{tp1} + {tp2} != {p}")

def test_sub():
    global pairs
    for p1 in range(len(pairs)):
        for p2 in range(len(pairs)):
            tp1 = Pair(pairs[p1])
            tp2 = Pair(pairs[p2])
            p = tp1 - tp2
            assert (p.p1 == pairs[p1][0] - pairs[p2][0] and
                p.p2 == pairs[p1][1] - pairs[p2][1]), (f"{tp1} - {tp2} != {p}")
            tp2 = pairs[p2][0]
            p = tp1 - tp2
            assert (p.p1 == pairs[p1][0] - pairs[p2][0] and
                p.p2 == pairs[p1][1] - pairs[p2][0]), (f"{tp1} - {tp2} != {p}")

def test_mul():
    global pairs
    for p1 in range(len(pairs)):
        for p2 in range(len(pairs)):
            tp1 = Pair(pairs[p1])
            tp2 = Pair(pairs[p2])
            p = tp1 * tp2
            assert (p.p1 == pairs[p1][0] * pairs[p2][0] and
                p.p2 == pairs[p1][1] * pairs[p2][1]), (f"{tp1} * {tp2} != {p}")
            tp2 = pairs[p2][0]
            p = tp1 * tp2
            assert (p.p1 == pairs[p1][0] * pairs[p2][0] and
                p.p2 == pairs[p1][1] * pairs[p2][0]), (f"{tp1} * {tp2} != {p}")

def test_truediv():
    for p1 in range(len(pairs)):
        for p2 in range(len(pairs)):
            tp1 = Pair(pairs[p1])
            tp2 = Pair(pairs[p2])
            if 0 in pairs[p2]:
                with pytest.raises(ZeroDivisionError) as e:
                    tp1 / tp2
            else:
                p = tp1 / tp2
                assert (round(p.p1,10) == round(pairs[p1][0] / pairs[p2][0],10) and
                    round(p.p2,10) == round(pairs[p1][1] / pairs[p2][1]),10), (f"{tp1} / {tp2} != {p}")
                tp2 = pairs[p2][0]
                p = tp1 / tp2
                assert (round(p.p1,10) == round(pairs[p1][0] / pairs[p2][0],10) and
                    round(p.p2,10) == round(pairs[p1][1] / pairs[p2][1]),10), (f"{tp1} / {tp2} != {p}")

def test_iadd():
    global pairs
    for p1 in range(len(pairs)):
        for p2 in range(len(pairs)):
            tp1 = Pair(pairs[p1])
            tp2 = Pair(pairs[p2])
            p = Pair(tp1)
            p += tp2
            assert (p.p1 == pairs[p1][0] + pairs[p2][0] and
                p.p2 == pairs[p1][1] + pairs[p2][1]), (f"{tp1} + {tp2} != {p}")
            tp2 = pairs[p2][0]
            p = Pair(tp1)
            p += tp2
            assert (p.p1 == pairs[p1][0] + pairs[p2][0] and
                p.p2 == pairs[p1][1] + pairs[p2][0]), (f"{tp1} + {tp2} != {p}")

def test_isub():
    global pairs
    for p1 in range(len(pairs)):
        for p2 in range(len(pairs)):
            tp1 = Pair(pairs[p1])
            tp2 = Pair(pairs[p2])
            p = Pair(tp1)
            p -= tp2
            assert (p.p1 == pairs[p1][0] - pairs[p2][0] and
                p.p2 == pairs[p1][1] - pairs[p2][1]), (f"{tp1} - {tp2} != {p}")
            tp2 = pairs[p2][0]
            p = Pair(tp1)
            p -= tp2
            assert (p.p1 == pairs[p1][0] - pairs[p2][0] and
                p.p2 == pairs[p1][1] - pairs[p2][0]), (f"{tp1} - {tp2} != {p}")

def test_imul():
    global pairs
    for p1 in range(len(pairs)):
        for p2 in range(len(pairs)):
            tp1 = Pair(pairs[p1])
            tp2 = Pair(pairs[p2])
            p = Pair(tp1)
            p *= tp2
            assert (p.p1 == pairs[p1][0] * pairs[p2][0] and
                p.p2 == pairs[p1][1] * pairs[p2][1]), (f"{tp1} * {tp2} != {p}")
            tp2 = pairs[p2][0]
            p = Pair(tp1)
            p *= tp2
            assert (p.p1 == pairs[p1][0] * pairs[p2][0] and
                p.p2 == pairs[p1][1] * pairs[p2][0]), (f"{tp1} * {tp2} != {p}")

def test_itruediv():
    global pairs
    for p1 in range(len(pairs)):
        for p2 in range(len(pairs)):
            tp1 = Pair(pairs[p1])
            tp2 = Pair(pairs[p2])
            p = Pair(tp1)
            if 0 in pairs[p2]:
                with pytest.raises(ZeroDivisionError) as e:
                    p /= tp2
            else:
                p /= tp2
                assert (round(p.p1,10) == round(pairs[p1][0] / pairs[p2][0],10) and
                    round(p.p2,10) == round(pairs[p1][1] / pairs[p2][1]),10), (f"{tp1} / {tp2} != {p}")
                p = Pair(tp1)
                tp2 = pairs[p2][0]
                p /= tp2
                assert (round(p.p1,10) == round(pairs[p1][0] / pairs[p2][0],10) and
                    round(p.p2,10) == round(pairs[p1][1] / pairs[p2][1]),10), (f"{tp1} / {tp2} != {p}")


def test_eq():
    global pairs
    for p1 in range(len(pairs)):
        for p2 in range(len(pairs)):
            tp1 = Pair(pairs[p1])
            tp2 = Pair(pairs[p2])
            eq = tp1 == tp2
            assert (eq == (pairs[p1][0] == pairs[p2][0] and
                pairs[p1][1] == pairs[p2][1])), (f"{tp1} == {tp2} != {eq}")
            tp2 = pairs[p2][0]
            eq = tp1 == tp2
            assert (eq == (pairs[p1][0] == pairs[p2][0] and
                pairs[p1][1] == pairs[p2][0])), (f"{tp1} == {tp2} != {eq}")

def test_getitem():
    global pairs
    for p1 in range(len(pairs)):
        p = Pair(pairs[p1])
        assert p[0] == int(pairs[p1][0]) and p[1] == int(pairs[p1][1]), (f"{p}[0,1] != "
            f"({int(pairs[p1][0])},{int(pairs[p1][1])}")

#TODO lt, le, gt, ge