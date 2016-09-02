"""
Binary Dihedral Groups

AUTHORS:

- Travis Scrimshaw (2016-02): initial version
"""

#*****************************************************************************
#       Copyright (C) 2016 Travis Scrimshaw <tscrimsh at umn.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.groups.matrix_gps.finitely_generated import FinitelyGeneratedMatrixGroup_gap
from sage.structure.unique_representation import UniqueRepresentation
from sage.misc.latex import latex
from sage.rings.number_field.number_field import CyclotomicField
from sage.matrix.matrix_space import MatrixSpace
from sage.categories.groups import Groups
from sage.rings.all import ZZ

class BinaryDihedralGroup(UniqueRepresentation, FinitelyGeneratedMatrixGroup_gap):
    r"""
    The binary dihedral group `BD_n` of order `4n`.

    The binary dihedral group `BD_n` is a finite group of order `4n`, and
    can be considered as the matrix group generated by

    .. MATH::

        g_1 = \begin{pmatrix}
        \zeta_{2n} & 0 \\ 0 & \zeta_{2n}^{-1}
        \end{pmatrix}, \qquad\qquad
        g_2 = \begin{pmatrix} 0 & \zeta_4 \\ \zeta_4 & 0 \end{pmatrix},

    where `\zeta_k = e^{2\pi i / k}` is the primitive `k`-th root of unity.
    Furthermore, `BD_n` admits the following presentation (note that there
    is a typo in [Sun]_):

    .. MATH::

        BD_n = \langle x, y, z | x^2 = y^2 = z^n = x y z \rangle.

    REFERENCES:

    .. [Dolgachev09] Igor Dolgachev. *McKay Correspondence*. (2009).
       http://www.math.lsa.umich.edu/~idolga/McKaybook.pdf

    .. [Sun] Yi Sun. *The McKay correspondence*.
       http://www.math.miami.edu/~armstrong/686sp13/McKay_Yi_Sun.pdf

    - :wikipedia:`Dicyclic_group#Binary_dihedral_group`
    """
    def __init__(self, n):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: G = groups.matrix.BinaryDihedral(4)
            sage: TestSuite(G).run()
        """
        self._n = n

        if n % 2 == 0:
            R = CyclotomicField(2*n)
            zeta = R.gen()
            zeta_inv = ~zeta
            i = R.gen()**(n//2)
        else:
            R = CyclotomicField(4*n)
            zeta = R.gen()**2
            zeta_inv = ~zeta
            i = R.gen()**n

        MS = MatrixSpace(R, 2)
        zero = R.zero()
        gens = [ MS([zeta, zero, zero, ~zeta]), MS([zero, i, i, zero]) ]

        from sage.libs.gap.libgap import libgap
        gap_gens = [libgap(matrix_gen) for matrix_gen in gens]
        gap_group = libgap.Group(gap_gens)

        FinitelyGeneratedMatrixGroup_gap.__init__(self, ZZ(2), R, gap_group, category=Groups().Finite())

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: groups.matrix.BinaryDihedral(3)
            Binary dihedral group of order 12
        """
        return "Binary dihedral group of order {}".format(4 * self._n)

    def _latex_(self):
        r"""
        Return a latex representation of ``self``.

        EXAMPLES::

            sage: G = groups.matrix.BinaryDihedral(3)
            sage: latex(G)
            BD_{3}
        """
        return "BD_{{{}}}".format(self._n)

    def order(self):
        """
        Return the order of ``self``, which is `4n`.

        EXAMPLES::

            sage: G = groups.matrix.BinaryDihedral(3)
            sage: G.order()
            12

        TESTS::

            sage: for i in range(1, 10):
            ....:     G = groups.matrix.BinaryDihedral(5)
            ....:     assert len(list(G)) == G.order()
        """
        return ZZ(4 * self._n)

    cardinality = order

