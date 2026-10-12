# eki.labs brand kit · the wordmark, drawn in curves from Geist.
# «eki.» goes in Geist 600 and the second name (labs, agro, energy…) in Geist 400.
# Font units (1000 per em), baseline at y = 0, no kerning and no tracking: the same setting
# as the original wordmark master, so «eki.» keeps exactly the curves it always had.
import os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, 'fonts_dl', 'geist_Geist[wght].ttf')
BASE, BASE_WEIGHT, NAME_WEIGHT = 'eki.', 600, 400

_inst = {}


def _font(weight):
    if weight not in _inst:
        _inst[weight] = instancer.instantiateVariableFont(TTFont(FONT), {'wght': weight})
    return _inst[weight]


def _r(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.')


def paths(segments):
    """[(text, weight), …] → (list of SVG path data, xMax of the drawing)."""
    out, x, xmax = [], 0.0, 0.0
    for text, weight in segments:
        f = _font(weight)
        gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f['hmtx']
        for ch in text:
            g = cmap[ord(ch)]
            pen = SVGPathPen(gs, ntos=_r)
            gs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
            bp = BoundsPen(gs)
            gs[g].draw(bp)
            if bp.bounds:
                xmax = max(xmax, x + bp.bounds[2])
            out.append(pen.getCommands())
            x += hmtx[g][0]
    return out, xmax


def name(second=''):
    """Path data and width for «eki.» plus an optional second name."""
    segs = [(BASE, BASE_WEIGHT)] + ([(second, NAME_WEIGHT)] if second else [])
    return paths(segs)
