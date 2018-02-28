r"""
`p`-Adic Elements with lattice precision.

AUTHOR:

- Xavier caruso (2018-02): initial version

TESTS::

    sage: R = ZpLC(2)
    doctest:...: FutureWarning: This class/method/function is marked as experimental. It, its functionality or its interface might change without a formal deprecation.
    See http://trac.sagemath.org/23505 for details.
    sage: R = ZpLF(2)
    sage: R = QpLC(2)
    sage: R = QpLF(2)
"""

# ****************************************************************************
#       Copyright (C) 2018 Xavier Caruso <xavier.caruso@normalesup.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
# ****************************************************************************


import weakref

from sage.misc.abstract_method import abstract_method

from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ
from sage.rings.infinity import Infinity

from sage.rings.padics.generic_nodes import pAdicRingBaseGeneric
from sage.rings.padics.padic_generic_element import pAdicGenericElement
from sage.rings.padics.lattice_precision import pRational

from sage.rings.padics.precision_error import PrecisionError


class pAdicLatticeElement(pAdicGenericElement):
    """
    Constructs new element with given parent and value.

    INPUT:

    - ``parent`` -- the parent of this element

    - ``x`` -- the newly created element

    - ``dx`` -- a dictionary representing the differential of ``x``

    - ``dx_mode`` -- a string, either ``linear_combination`` (the default)
      or ``values``

    - ``valuation`` -- an integer or ``None`` (default: ``None``), 
      the valuation of this element

    - ``check`` -- a boolean (default: ``True``), whether the function
      should check that the given values are well formed and coherent

    - ``reduce`` -- a boolean (default: ``True``), whether the given
      values need to be reduced

    TESTS::

        sage: R = ZpLC(2)
        sage: x = R(1, 10)  # indirect doctest
        sage: x
        1 + O(2^10)
    """
    def __init__(self, parent, x, prec=None, dx=[], dx_mode='linear_combination', valuation=None, check=True, reduce=True):
        """
        Initialize this element.

        INPUT:

        - ``parent`` -- the parent of this element

        - ``x`` -- the newly created element

        - ``dx`` -- a dictionary representing the differential of ``x``

        - ``dx_mode`` -- a string, either ``linear_combination`` (the default)
          or ``values``

        - ``valuation`` -- an integer or ``None`` (default: ``None``), 
          the valuation of this element

        - ``check`` -- a boolean (default: ``True``), whether the function
          should check that the given values are well formed and coherent

        - ``reduce`` -- a boolean (default: ``True``), whether the given
          values need to be reduced

        TESTS::

            sage: R = ZpLC(2)
            sage: x = R(1, 10)  # indirect doctest
            sage: x
            1 + O(2^10)
        """
        self._parent = parent
        p = parent.prime()
        pAdicGenericElement.__init__(self, parent)
        self._precision = parent.precision()
        if check:
            if isinstance(x, pAdicGenericElement):
                if parent.prime() != x.parent().prime():
                    raise TypeError("conversion between different p-adic rings/fields not supported")
                if prec is None:
                    prec = x.precision_absolute()
                else:
                    prec = min(prec, x.precision_absolute())
            x = QQ(x)
        if isinstance(x, pRational):
            self._value = x
        else:
            self._value = pRational(p, QQ(x))
        trunc = self._declare_new_element(dx, prec, dx_mode)
        if reduce:
            self._value = self._value.reduce(trunc)
        self._approx_zero = pRational(p, 0)
        self._approx_one = pRational(p, 1)
        self._approx_minusone = pRational(p, -1)

    @abstract_method
    def _declare_new_element(self, dx, prec, dx_mode):
        """
        Declare this element to the precision object and 
        return the precision at which this element can be truncated safely.

        Only for internal use.

        TESTS::

            sage: R = ZpLC(17)
            sage: prec = R.precision()

            sage: prec.del_elements()
            sage: nb = len(prec.tracked_elements())
            sage: x = R(1, 10)    # indirect doctest
            sage: len(prec.tracked_elements()) == nb + 1
            True
        """
        pass

    def __hash__(self):
        """
        Return a hash of this element.

        TESTS::

            sage: R = ZpLC(2)
            sage: x = R(1, 10)
            sage: hash(x)   # somewhat random
        """
        return id(self)

    # This doesn't work apparently (I don't know why)
    # Deletion is currently handled in PrecisionLattice 
    # def __del__(self):
    #     self._precision._mark_for_deletion(weakref.ref(self))

    def _is_base_elt(self, p):
        """
        Return ``True`` if this element is an element of Zp or Qp (rather than
        an extension).

        INPUT:

        - ``p`` -- a prime, which is compared with the parent of this element.

        EXAMPLES::

            sage: K = QpLC(7)
            sage: K.random_element()._is_base_elt(7)
            True
        """
        return p == self._parent.prime()

    def approximation(self):
        """
        Return an approximation of this element at
        its absolute precision.

        EXAMPLES::

            sage: R = ZpLC(2, print_mode='terse')
            sage: x = R(1234, 10); x
            210 + O(2^10)
            sage: x.approximation()
            210
        """
        prec = self.precision_absolute()
        app = self._value.reduce(prec)
        return app.value()

    def value(self):
        """
        Return the actual approximation of this element
        stored in memory. 
        In presence of diffused digits of precision, it can 
        have more precision than the absolute precision of
        the element.

        EXAMPLES::

            sage: R = ZpLC(2, print_mode='terse')
            sage: x = R(1234, 10); x
            210 + O(2^10)
            sage: x.approximation()
            210

        Another example with diffused digits::

            sage: x = R(2, 10); y = R(7, 5)
            sage: u = x - y
            sage: u
            27 + O(2^5)
            sage: u.value()
            1048571
        """
        return self._value.value()

    def precision_lattice(self):
        """
        Return the precision object (which is a lattice in a possibly
        high-dimensional vector space) that handles the precision of 
        this element.

        EXAMPLES::

            sage: R = ZpLC(2, label='precision')
            sage: x = R.random_element()
            sage: y = R.random_element()
            sage: x.precision_lattice()
            Precision lattice on 2 objects (label: precision)

        .. SEEALSO::

            :class:`sage.rings.padics.lattice_precision.PrecisionLattice`
        """
        return self._precision

    def precision_absolute(self):
        """
        Return the absolute precision of this element.

        This precision is computed by projecting the lattice precision
        onto the coordinate defined by this element.

        EXAMPLES::

            sage: R = ZpLC(2, print_mode='terse')
            sage: x = R(1234, 10); x
            210 + O(2^10)
            sage: x.precision_absolute()
            10

        Another example with diffused digits::

            sage: x = R(1, 10); y = R(1, 5)
            sage: x, y = x+y, x-y
            sage: x.precision_absolute()
            5
            sage: y.precision_absolute()
            5
            sage: (x+y).precision_absolute()
            11
        """
        prec = self._precision._precision_absolute(self)
        cap = self._value.valuation() + self._parent._prec_cap_relative
        return min(prec, cap)

    def is_precision_capped(self):
        """
        Return whether the absolute precision on this element results from a
        cap coming from the parent.

        EXAMPLES::

            sage: R = ZpLC(2)
            sage: x = R(1, 10); x
            1 + O(2^10)
            sage: x.is_precision_capped()
            False

            sage: y = x-x; y
            O(2^40)
            sage: y.is_precision_capped()
            True

            sage: y = x << 35; y
            2^35 + O(2^40)
            sage: y.is_precision_capped()
            True
            sage: z = y >> 35; z
            1 + O(2^5)
            sage: z.is_precision_capped()
            True
        """
        return self._precision._is_precision_capped(self)

    def valuation(self, secure=False):
        """
        Return the valuation of this element.

        INPUT:

        - ``secure`` -- a boolean (default: ``False``); when ``True``,
          an error is raised if the precision on the element is not
          enough to determine for sure its valuation; otherwise the
          absolute precision (which is the smallest possible valuation)
          is returned

        EXAMPLES::

            sage: R = ZpLC(2)
            sage: x = R(12, 10); x
            2^2 + 2^3 + O(2^10)
            sage: x.valuation()
            2

            sage: y = x - x; y
            O(2^40)
            sage: y.valuation()
            40
            sage: y.valuation(secure=True)
            Traceback (most recent call last):
            ...
            PrecisionError: Not enough precision
        """
        p = self._parent.prime()
        val = self._value.valuation()
        prec = self.precision_absolute()
        if val < prec: 
            return val
        elif secure:
            raise PrecisionError("Not enough precision")
        else:
            return prec

    def precision_relative(self, secure=False):
        """
        Return the relative precision of this element, that is
        the difference between its absolute precision and its
        valuation.

        INPUT:

        - ``secure`` -- a boolean (default: ``False``); when ``True``,
          an error is raised if the precision on the element is not
          enough to determine for sure its valuation

        EXAMPLES::

            sage: R = ZpLC(2)
            sage: x = R(12, 10); x
            2^2 + 2^3 + O(2^10)
            sage: x.precision_relative()
            8

            sage: y = x - x; y
            O(2^40)
            sage: y.precision_relative()
            0
            sage: y.precision_relative(secure=True)
            Traceback (most recent call last):
            ...
            PrecisionError: Not enough precision
        """
        return self.precision_absolute() - self.valuation(secure=secure)

    def _cmp_(self, other):
        """
        Compare this element with ``other``.

        TESTS::

            sage: R = ZpLC(2)
            sage: x = R(1, 5)
            sage: y = R(128, 10)
            sage: z = x + y

            sage: x
            1 + O(2^5)
            sage: z
            1 + O(2^5)

            sage: x == z   # Indirect doctest
            False
            sage: z - x
            2^7 + O(2^10)
        """
        if (self-other).is_zero():
            return 0
        else:
            return self.lift()._cmp_(other.lift())

    def _add_(self, other):
        """
        Return the sum of this element and ``other``.

        EXAMPLES::

            sage: R = ZpLC(19, 5)
            sage: a = R(-1); a
            18 + 18*19 + 18*19^2 + 18*19^3 + 18*19^4 + O(19^5)
            sage: b = R(-5/2); b
            7 + 9*19 + 9*19^2 + 9*19^3 + 9*19^4 + O(19^5)
            sage: a + b   # indirect doctest
            6 + 9*19 + 9*19^2 + 9*19^3 + 9*19^4 + O(19^5)

        TESTS::

            sage: a = R.random_element()
            sage: b = R.random_element()
            sage: a + b == b + a
            True
        """
        x = self._value + other._value
        if self._parent._zero_cap is not None:
            if x.valuation() >= min(self._value.valuation(), other._value.valuation()) + self._parent._zero_cap:
                x = self._approx_zero
        dx = [  [self, self._approx_one], 
               [other, self._approx_one] ]
        return self.__class__(self._parent, x, dx=dx, check=False)

    def _sub_(self, other):
        """
        Return the difference of this element and ``other``.

        EXAMPLES::

           sage: R = ZpLC(19, 5)
           sage: a = R(-1); a
           18 + 18*19 + 18*19^2 + 18*19^3 + 18*19^4 + O(19^5)
           sage: b = R(-5/2); b
           7 + 9*19 + 9*19^2 + 9*19^3 + 9*19^4 + O(19^5)
           sage: a - b   # indirect doctest
           11 + 9*19 + 9*19^2 + 9*19^3 + 9*19^4 + O(19^5)
        """
        x = self._value - other._value
        if self._parent._zero_cap is not None:
            if x.valuation() >= min(self._value.valuation(), other._value.valuation()) + self._parent._zero_cap:
                x = self._approx_zero
        dx = [  [self, self._approx_one], 
               [other, self._approx_minusone] ]
        return self.__class__(self._parent, x, dx=dx, check=False)

    def _mul_(self, other):
        """
        Return the product of this element and ``other``.

        EXAMPLES::

            sage: R = ZpLC(19, 5)
            sage: a = R(-1); a
            18 + 18*19 + 18*19^2 + 18*19^3 + 18*19^4 + O(19^5)
            sage: b = R(-5/2); b
            7 + 9*19 + 9*19^2 + 9*19^3 + 9*19^4 + O(19^5)
            sage: a * b   # indirect doctest
            12 + 9*19 + 9*19^2 + 9*19^3 + 9*19^4 + O(19^5)

        TESTS::

            sage: a = R.random_element()
            sage: b = R.random_element()
            sage: a * b == b * a
            True

            sage: a = R.random_element()
            sage: b = R.random_element()
            sage: c = R.random_element()
            sage: a * (b+c) == a*b + a*c
            True
        """
        x_self = self._value
        x_other = other._value
        x = x_self * x_other
        dx = [  [self, x_other],
               [other, x_self ] ]
        return self.__class__(self._parent, x, dx=dx, check=False)

    def _div_(self, other):
        """
        Return the quotient of this element and ``other``.

        NOTE::

        The result of division always lives in the fraction field,
        even if the element to be inverted is a unit.

        EXAMPLES::

            sage: R = ZpLC(19)
            sage: a = R(-1, 5); a
            18 + 18*19 + 18*19^2 + 18*19^3 + 18*19^4 + O(19^5)
            sage: b = R(-5/2, 5); b
            7 + 9*19 + 9*19^2 + 9*19^3 + 9*19^4 + O(19^5)
 
            sage: c = a / b   # indirect doctest
            sage: c
            8 + 11*19 + 7*19^2 + 11*19^3 + 7*19^4 + O(19^5)
            sage: c.parent()
            19-adic Field with lattice-cap precision

            sage: a / (19*b)
            8*19^-1 + 11 + 7*19 + 11*19^2 + 7*19^3 + O(19^4)

        If the division is indistinguishable from zero, an error is raised::

            sage: c = a / (2*b + 5)
            Traceback (most recent call last):
            ...
            PrecisionError: cannot divide by something indistinguishable from zero
        """
        if other.is_zero():
            raise PrecisionError("cannot divide by something indistinguishable from zero")
        x_self = self._value
        x_other = other._value
        x = x_self / x_other
        # dx = (1/other)*dself - (self/other^2)*dother
        dx = [  [self, self._approx_one/x_other],
               [other, -x_self/(x_other*x_other)] ]
        return self.__class__(self._parent.fraction_field(), x, dx=dx, check=False)

    def __invert__(self):
        """
        Return the multiplicative inverse of this element.

        NOTE::

        The result of division always lives in the fraction field,
        even if the element to be inverted is a unit.

        EXAMPLES::

            sage: R = ZpLC(19)
            sage: x = R(-5/2, 5); x
            7 + 9*19 + 9*19^2 + 9*19^3 + 9*19^4 + O(19^5)

            sage: y = ~x    # indirect doctest
            sage: y
            11 + 7*19 + 11*19^2 + 7*19^3 + 11*19^4 + O(19^5)
            sage: y == -2/5
            True

        TESTS::

            sage: a = R.random_element()
            sage: a * ~a == 1
            True
        """
        if self.is_zero():
            raise PrecisionError("cannot invert something indistinguishable from zero")
        x_self = self._value
        x = self._approx_one / x_self
        # dx = -(1/self^2)*dself
        dx = [  [self, self._approx_minusone/(x_self*x_self)] ]
        return self.__class__(self._parent.fraction_field(), x, dx=dx, check=False)

    def add_bigoh(self, prec):
        """
        Return a new element with absolute precision decreased to
        the specified precision.

        INPUT:

        - ``prec`` -- an integer or infinity

        EXAMPLES::

           sage: R = ZpLC(7)
           sage: a = R(8); a.add_bigoh(1)
           1 + O(7)
           sage: b = R(0); b.add_bigoh(3)
           O(7^3)

           sage: R = QpLC(7, 4)
           sage: a = R(8); a.add_bigoh(1)
           1 + O(7)
           sage: b = R(0); b.add_bigoh(3)
           O(7^3)

           The precision never increases::

           sage: R(4).add_bigoh(2).add_bigoh(4)
           4 + O(7^2)
        """
        x = self._value
        dx = [ [self, self._approx_one ] ]
        return self.__class__(self._parent, x, prec, dx=dx, check=False)

    def lift_to_precision(self, prec=None, infer_precision=False):
        """
        Return another element of the same parent with absolute precision
        at least ``prec``, congruent to this p-adic element modulo the
        precision of this element.

        INPUT:

        - ``prec`` -- an integer or ``None`` (default: ``None``), the
          absolute precision of the result. If ``None``, lifts to the 
          maximum precision allowed

        - ``infer_precision`` -- a boolean (default: ``False``)

        NOTE:

        In the lattice precision model, the precision of all variables is 
        handled globally by a unique object, namely a lattice in a certain
        vector space.

        When ``infer_precision`` is set to ``True``, the precision lattice
        is recomputed. This may affect the precision of other variables
        with the same parent.

        When ``infer_precision`` is set to ``False``, the precision on the
        newly created variable is independant as if the variable were created
        by hand by setting independantly the value of the absolute precision.
        In particular, if ``self`` used to share diffused digits of precision 
        with other variables, they are not preserved.

        EXAMPLES::

            sage: R = ZpLC(2)
            sage: x = R(1, 10); x
            1 + O(2^10)
            sage: x.lift_to_precision(15)
            1 + O(2^15)
            sage: x.lift_to_precision()
            1 + O(2^20)

        An example with diffused digits of precision::

            sage: x = R(1, 10); y = R(1, 5)
            sage: u = x+y; u
            2 + O(2^5)
            sage: v = x-y; v
            O(2^5)
            sage: u + v
            2 + O(2^11)

        The gain of precision on ``u + v`` is due to the presence of diffused
        digits of precision between ``u`` and ``v``.

        However, if we call :meth:`lift_to_precision` on one of these variables, 
        these diffused digits are lost and the precision on the sum is no longer
        sharp::

            sage: u.lift_to_precision() + v
            2 + O(2^5)

        We can avoid this issue as follows::

            sage: u.lift_to_precision(infer_precision=True) + v
            2 + O(2^11)

        But now the precision on ``y`` has changed::

            sage: y
            1 + O(2^10)

        Indeed if the absolute precision on ``u = x+y`` (resp. on ``x``)
        is 20 (resp. 10), we deduce that the absolution precision on 
        ``y = u-x`` is 10.

        .. SEEALSO::

            :meth:`lift_to_precision` of the precision object
        """
        #from warnings import warn
        #warn("use lift_to_precision with extreme caution in the framework of lattice precision")
        parent = self._parent
        if infer_precision:
            cap = min(parent.precision_cap_absolute(), parent.precision_cap_relative() + self._value.valuation())
            if prec is None or prec > cap:
                prec = cap
            lift = self.copy()
            parent.precision().lift_to_precision(lift, prec)
        else:
            lift = self.__class__(parent, self._value, prec, check=False)
        return lift

    def _is_inexact_zero(self):
        """
        Return ``True`` if this element is indistinguishable from zero.

        EXAMPLES::

            sage: R = ZpLC(5)
            sage: R(0)._is_inexact_zero()
            True
            sage: R(1)._is_inexact_zero()
            False
        """
        absprec = self.precision_absolute()
        return self._value.valuation() >= absprec

    def is_zero(self, prec=None):
        """
        Return ``True`` if this element is indistinguishable from zero
        at the given precision (if given).

        INPUT:

        - ``prec`` -- an integer or ``None`` (default: ``None``)

        EXAMPLES::

            sage: R = ZpLC(2)
            sage: x = R(2/5, 10); x
            2 + 2^3 + 2^4 + 2^7 + 2^8 + O(2^10)
            sage: x.is_zero()
            False
            sage: x.is_zero(1)
            True

            sage: (5*x-2).is_zero()
            True
            sage: 5*x == 2   # indirect doctest
            True
        """
        absprec = self.precision_absolute()
        if prec is None:
            prec = absprec
        else:
            prec = min(absprec, prec)
        return self._value.valuation() >= prec

    def lift(self):
        """
        Return an integer or rational congruent to this element modulo
        its absolute precision.
        If a rational is returned, its denominator will be a power of `p`.

        EXAMPLES:

           sage: R = ZpLC(7)
           sage: a = R(8); a.lift()
           8

           sage: R = QpLC(7)
           sage: a = R(8); a.lift()
           8
           sage: b = R(8/7); b.lift()
           8/7
        """
        return self._value.value()

    def __rshift__(self, n):
        """
        Divide this element by ``p^n``, and truncate
        (if the parent is not a field).

        EXAMPLES::

            sage: R = ZpLC(997, 7)
            sage: a = R(123456878908); a
            964*997 + 572*997^2 + 124*997^3 + O(997^8)

            sage: S = ZpLC(5)
            sage: b = S(17); b
            2 + 3*5 + O(5^20)

        Shifting to the right divides by a power of `p`, but drops
        terms with negative valuation::

            sage: a >> 3
            124 + O(997^5)
            sage: b >> 1
            3 + O(5^19)
            sage: b >> 40
            O(5^0)

        If the parent is a field no truncation is performed::

            sage: K = QpLC(5)
            sage: b = K(17); b
            2 + 3*5 + O(5^20)
            sage: b >> 1
            2*5^-1 + 3 + O(5^19)

        A negative shift multiplies by that power of `p`::

            sage: a >> -3
            964*997^4 + 572*997^5 + 124*997^6 + O(997^11)
            sage: b >> -5
            2*5^5 + 3*5^6 + O(5^25)
        """
        return self << (-n)

    def __lshift__(self, n):
        """
        Multiply this element by ``p^n``.

        If ``n`` is negative and this element does not lie in a field,
        digits may be truncated.  See :meth:`__rshift__` for details.

        EXAMPLES::

            sage: R = ZpLC(5)
            sage: a = R(1000); a
            3*5^3 + 5^4 + O(5^23)
            sage: a >> 1
            3*5^2 + 5^3 + O(5^22)

            sage: S = Zp(5); b = S(1000); b
            3*5^3 + 5^4 + O(5^23)
        """
        parent = self._parent
        p = parent.prime()
        if isinstance(parent, pAdicRingBaseGeneric):
            if self.precision_absolute() + n < 0:
                return self.__class__(parent, pRational(p, 0), 0, dx={}, check=False)
        powp = pRational(p, ZZ(1), n)
        x = self._value * powp
        if isinstance(parent, pAdicRingBaseGeneric):
            x -= x.reduce(0)
        dx = [ [self, powp] ]
        return self.__class__(parent, x, dx=dx, check=False)

    def unit_part(self):
        """
        Return `u`, where this element is `p^v u` and `u` is a unit.

        EXAMPLES::

            sage: R = ZpLC(17)
            sage: a = R(18*17, 4)
            sage: a.unit_part()
            1 + 17 + O(17^3)

            sage: b=1/a; b
            17^-1 + 16 + O(17^2)
            sage: b.unit_part()
            1 + 16*17 + O(17^3)

        If the element is indistinguishable from zero, an error is raised.

            sage: c = R(0, 5); c
            O(17^5)
            sage: c.unit_part()
            Traceback (most recent call last):
            ...
            PrecisionError: Not enough precision
        """
        v = self.valuation(secure=True)
        return self >> v

    def val_unit(self):
        """
        Return the pair `(v, u)`, where this element is 
        `p^v u` and `u` is a unit.

        EXAMPLES::

            sage: R = ZpLC(17)
            sage: a = R(18*17, 4)
            sage: a.val_unit()
            (1, 1 + 17 + O(17^3))

            sage: b=1/a; b
            17^-1 + 16 + O(17^2)
            sage: b.val_unit()
            (-1, 1 + 16*17 + O(17^3))

        If the element is indistinguishable from zero, an error is raised

            sage: c = R(0, 5); c
            O(17^5)
            sage: c.val_unit()
            Traceback (most recent call last):
            ...
            PrecisionError: Not enough precision
        """
        v = self.valuation(secure=True)
        return v, self >> v

    def copy(self, parent=None):
        """
        Return a copy of this element or convert this element
        to the given parent provided that the precision on this
        parent is handled by the same precision object.

        EXAMPLES::

            sage: R = ZpLC(2)
            sage: x = R(1, 10); x
            1 + O(2^10)
            sage: y = x.copy()
            sage: y
            1 + O(2^10)

        In the lattice precision model, Sage remembers that ``y`` is 
        actually equal to ``x``. Therefore, when we compute the difference,
        the `O(2^10)` cancel as well::

            sage: x - y
            O(2^20)

        This function can also be used for coersion/conversion as follows::

            sage: K = QpLC(2)
            sage: y = x.copy(K)
            sage: y
            1 + O(2^10)
            sage: y.parent()
            2-adic Field with lattice-cap precision

            sage: a = K(2, 10); a
            2 + O(2^10)
            sage: b = a.copy(R)
            sage: b
            2 + O(2^10)
            sage: b.parent()
            2-adic Ring with lattice-cap precision

        In any case, precision is sharp::

            sage: x - y
            O(2^20)
            sage: a - b
            O(2^21)

        If a parent is given, it must share the same precision object::

            sage: x.copy(ZpLC(5))
            Traceback (most recent call last):
            ...
            TypeError: parent must share the same precision object

            sage: x.copy(Zp(2))
            Traceback (most recent call last):
            ...
            TypeError: parent must share the same precision object

            sage: x.copy(ZpLC(2, label='other'))
            Traceback (most recent call last):
            ...
            TypeError: parent must share the same precision object

        TESTS::

            sage: K(1/2).copy(R)
            Traceback (most recent call last):
            ...
            ValueError: element of negative valuation cannot be convert to the integer ring
        """
        if parent is None:
            parent = self._parent
        else:
            try:
                if parent.precision() is not self._parent.precision():
                    raise TypeError("parent must share the same precision object")
            except AttributeError:
                raise TypeError("parent must share the same precision object")
            if isinstance(parent, pAdicRingBaseGeneric) and self.valuation() < 0:
                raise ValueError("element of negative valuation cannot be convert to the integer ring")
        dx = [ [ self, self._approx_one ] ]
        return self.__class__(parent, self._value, dx=dx, check=False)

    def __copy__(self):
        """
        Return a copy of this element.

        TESTS::

            sage: R = ZpLC(2)
            sage: x = R(1, 10); x
            1 + O(2^10)
            sage: y = copy(x)   # indirect doctest
            sage: y
            1 + O(2^10)

            sage: x - y
            O(2^20)
        """
        return self.copy()

    def expansion(self):
        """
        Return the coefficients in the `p`-adic expansion of this element
        starting from its valuation and ending at its absolute precision

        EXAMPLES::

            sage: R = ZpLC(5, 10)
            sage: x = R(123456789); x
            4 + 2*5 + 5^2 + 4*5^3 + 5^5 + 5^6 + 5^8 + 3*5^9 + O(5^10)
            sage: x.expansion()
            [4, 2, 1, 4, 0, 1, 1, 0, 1, 3]

        If any, final are included in the expansion::

            sage: y = R(1234); y
            4 + 5 + 4*5^2 + 4*5^3 + 5^4 + O(5^10)
            sage: y.expansion()
            [4, 1, 4, 4, 1, 0, 0, 0, 0, 0]
        """
        # TODO: implement other lift modes
        p = self._parent.prime()
        prec = self.precision_absolute()
        return self._value.list(prec)


class pAdicLatticeCapElement(pAdicLatticeElement):
    def _declare_new_element(self, dx, prec, dx_mode):
        """
        Declare this element to the precision object and 
        return the precision at which this element can be truncated safely.

        Only for internal use.

        TESTS::

            sage: R = ZpLC(17)
            sage: prec = R.precision()

            sage: prec.del_elements()
            sage: nb = len(prec.tracked_elements())
            sage: x = R(1, 10)    # indirect doctest
            sage: len(prec.tracked_elements()) == nb + 1
            True
        """
        parent = self._parent
        cap = min(parent.precision_cap_absolute(), parent.precision_cap_relative() + self._value.valuation())
        if prec is None or prec > cap:
            capped = True
            prec = cap
        else:
            capped = False
        self._precision._new_element(self, dx, bigoh=prec, dx_mode=dx_mode, capped=capped)
        return prec

    def _is_exact_zero(self):
        """
        Return ``True`` if this element is exactly zero.

        NOTE::

        Since exact zeros are not supported in the precision lattice
        model, this function always returns ``False``.

        EXAMPLES::

            sage: R = ZpLC(5)
            sage: R(0)._is_exact_zero()
            False
            sage: R(1)._is_exact_zero()
            False
        """
        return False


class pAdicLatticeFloatElement(pAdicLatticeElement):
    def _declare_new_element(self, dx, prec, dx_mode):
        """
        Declare this element to the precision object and 
        return the precision at which this element can be truncated safely.

        Only for internal use.

        TESTS::

            sage: R = ZpLF(17)
            sage: prec = R.precision()

            sage: prec.del_elements()
            sage: nb = len(prec.tracked_elements())
            sage: x = R(1, 10)    # indirect doctest
            sage: len(prec.tracked_elements()) == nb + 1
            True
        """
        self._precision._new_element(self, dx, bigoh=prec, dx_mode=dx_mode)
        cap = self._precision.internal_prec() + self._value.valuation()
        if prec is None:
            return cap
        else:
            return min(cap, prec)

    def _is_exact_zero(self):
        """
        Return ``True`` if this element is exactly zero.

        EXAMPLES::

            sage: R = ZpLF(5)
            sage: R(0)._is_exact_zero()
            True
            sage: R(0, 10)._is_exact_zero()
            False

            sage: R(1)._is_exact_zero()
            False
        """
        return self._value.is_zero() and self._precision._precision_absolute(self) is Infinity
