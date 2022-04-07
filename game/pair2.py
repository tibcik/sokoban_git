from numbers import Number

class Pair:
    def __init__(self, p1c = 0, p2 = 0):
        if isinstance(p1c, Number):
            p1 = p1c
            p2 = p2
        if hasattr(p1c, "__getitem__") and len(p1c) >= 2:
            p1 = p1c[0]
            p2 = p1c[1]
        self.p1 = p1
        self.p2 = p2

    def __add__(self, other):
        if isinstance(other, Number):
            return Pair(self.p1 + other, self.p2 + other)
        elif isinstance(other, Pair):
            return Pair(self.p1 + other.p1, self.p2 + other.p2)
        elif hasattr(other, "__getitem__") and len(other) >= 2:
            return Pair(self.p1 + other[0], self.p2 + other[1])

        raise NotImplemented

    def __sub__(self, other):
        return self + other * -1

    def __mul__(self, other):
        if isinstance(other, Number):
            return Pair(self.p1 * other, self.p2 * other)
        elif isinstance(other, Pair):
            return Pair(self.p1 * other.p1, self.p2 * other.p2)
        elif hasattr(other, "__getitem__") and len(other) >= 2:
            return Pair(self.p1 * other[0], self.p2 * other[1])

        raise NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Number):
            mul = (1/other, 1/other)
        elif isinstance(other, Pair):
            mul = (1/other.p1, 1/other.p2)
        elif hasattr(other, "__getitem__") and len(other) >= 2:
            mul = (1/other[0], 1/other[1])

        return self * mul

    def __iadd__(self, other):
        if isinstance(other, Number):
            self.p1 += other
            self.p2 += other
        elif isinstance(other, Pair):
            self.p1 += other.p1
            self.p2 += other.p2
        elif hasattr(other, "__getitem__") and len(other) >= 2:
            self.p1 += other[0]
            self.p2 += other[1]

        return self

    def __isub__(self, other):
        self += other * -1

        return self

    def __imul__(self, other):
        if isinstance(other, Number):
            self.p1 *= other
            self.p2 *= other
        elif isinstance(other, Pair):
            self.p1 *= other.p1
            self.p2 *= other.p2
        elif hasattr(other, "__getitem__") and len(other) >= 2:
            self.p1 *= other[0]
            self.p2 *= other[1]

        return self

    def __itruediv__(self, other):
        if isinstance(other, Number):
            mul = (1/other, 1/other)
        elif isinstance(other, Pair):
            mul = (1/other.p1, 1/other.p2)
        elif hasattr(other, "__getitem__") and len(other) >= 2:
            mul = (1/other[0], 1/other[1])

        return self * mul

    def __eq__(self, other):
        if hasattr(other, "__getitem__") and len(other) >= 2:
            return self.p1 == other[0] and self.p2 == other[1]
        elif isinstance(other, Number):
            return self.p1 == other and self.p2 == other

        return False

    def __getitem__(self, key):
        if key == 0:
            return int(self.p1)
        elif key == 1:
            return int(self.p2)

        raise KeyError

    def __len__(self):
        return 2

    def __repr__(self):
        return f"Pair(p1: {int(self.p1)}[{self.p1}], p2: {int(self.p2)}[{self.p2}])"
