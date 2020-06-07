"""The engine for drawing Lindenmayer Systems.

This engine allows:
  * Basic L-Systems
    * Capital letters draw, lower letters are gaps
    * `+` and `-` update the angle
    * Brackets store the position and angle
  * Easy rotations of the full system by giving an axiom a rotation
  * Both degrees and radian orientation
  * Implicit start rules
  * Stochastic grammars

See Also:
    https://en.wikipedia.org/wiki/L-system

Author: Randy Paredis
Date:   06/02/2020
"""
from main.extra.IOHandler import IOHandler
from lark import Transformer
from main.viewer.shapes import Line, Properties
import math, random

# TODO: Docs, Semantics, Colors, Width, Background, Draw Mapping, Context-Dependency, Parametrics,
#       mathematical equations for rotations (i.e. "PI / 2")...
# Draw Mapping: by default small letters -> 0, capital letters -> 1

Config = IOHandler.get_preferences()

class LSystemRule:
    def __init__(self, head, tail, perc=1):
        self.head = head
        self.tails = [(perc, tail)]

    def __repr__(self):
        return "%s -> { %s }" % (self.head, "; ".join(["%.3f, %s" %(p, l) for p, l in self.tails]))

    def add_tail(self, tail, perc=1):
        self.tails.append((perc, tail))

    def get_tail(self, gen):
        if len(self.tails) == 1:
            return self.tails[:][0][1]
        r = gen.random()
        for p, tail in self.tails[:]:
            r -= p
            if r <= 0:
                return tail
        # When the percentages don't add up to 1, take the last element.
        # TODO: prevent this via semantic analysis.
        return self.tails[:][-1][1]


class LSystem:
    def __init__(self):
        self.alphabet = set()
        self.axiom = None
        self.rules = dict()
        self.depth = 1
        self.angle = 90
        self.sangle = 0
        self.seed = 0
        self.size = 10

    def add_rule(self, head, tail, perc=1):
        if head in self.rules:
            self.rules[head].add_tail(tail, perc)
        else:
            self.rules[head] = LSystemRule(head, tail, perc)

    def solve(self):
        rng = random.Random(self.seed)
        current = self.axiom
        for i in range(self.depth):
            new = []
            for tok in current:
                tail = self.rules.get(tok, LSystemRule(tok, tok)).get_tail(rng)
                new += tail
            current = new[:]
        return self.execute(current)

    def execute(self, stream):
        # TODO: Optimize!
        stack = []
        a = self.sangle
        pos = (0, 0)
        trail = []
        for s in stream:
            if s == '+':
                a += self.angle
            elif s == '-':
                a -= self.angle
            elif s == '[':
                stack.append((pos, a))
            elif s == ']':
                pos, a = stack.pop()
            else:
                rad = math.radians(a)
                npos = pos[0] + math.cos(rad) * self.size, pos[1] + math.sin(rad) * self.size
                if s.isupper():
                    trail.append((pos, npos))
                pos = npos
        return trail


class LindenmayerTransformer(Transformer):
    def __init__(self):
        super().__init__(True)
        self.system = LSystem()

    LETTER = CONST = str
    PERC = DOUBLE = float

    def INT(self, x):
        return int(float(x))

    def axiom(self, elms):
        self.system.axiom = elms[2]
        if len(elms) > 3:
            self.system.sangle = elms[4]

    def letters(self, elms):
        self.system.alpha = elms
        return elms

    def seed(self, elms):
        self.system.seed = elms[2]

    def depth(self, elms):
        self.system.depth = elms[2]

    def angle(self, elms):
        self.system.angle = elms[2]

    def ang(self, elms):
        if elms[1].type == "DEG":
            return elms[0]
        return math.degrees(elms[0])

    def alpha(self, elms):
        self.system.alpha = set(elms[2])

    def tail(self, elms):
        return elms

    def rule(self, elms):
        p = 1.0
        if len(elms) == 4:
            p = elms[1]
        self.system.add_rule(elms[0], elms[-1], p)


class LImage:
    def __init__(self, path):
        self.path = path

    def find_bounds(self):
        xmin = xmax = ymin = ymax = 0
        for (x1, y1), (x2, y2) in self.path:
            xmin = min(x1, x2, xmin)
            xmax = max(x1, x2, xmax)
            ymin = min(y1, y2, ymin)
            ymax = max(y1, y2, ymax)
        return (xmin, ymin), (xmax, ymax)

    def transform(self, tx, ty, sx=1, sy=1):
        for i in range(len(self.path)):
            (x1, y1), (x2, y2) = self.path[i]
            self.path[i] = Line(x1 * sx + tx, y1 * sy + ty, x2 * sx + tx, y2 * sy + ty)

    def pillow(self):
        stmts = []
        for (x1, y1), (x2, y2) in self.path:
            p = (round(x1, 6), round(y1, 6)), (round(x2, 6), round(y2, 6))
            stmts.append("line from %s to %s width 1" % p)
        return "\n".join(stmts)

    def get(self):
        (l, b), (r, t) = self.find_bounds()
        margin = 10
        self.transform(-l+margin, t+margin, 1, -1)
        w = r - l + 2 * margin
        h = t - b + 2 * margin
        return [Properties(w, h)] + self.path


def transform(text, T):
    trans = LindenmayerTransformer()
    trans.transform(T)
    img = LImage(trans.system.solve())
    return img.get()