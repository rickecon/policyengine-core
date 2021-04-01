from __future__ import annotations

import typing

import numpy

from openfisca_core import taxscales


class MarginalAmountTaxScale(taxscales.AmountTaxScaleLike):

    def calc(
            self,
            tax_base: typing.Union[numpy.ndarray[int], numpy.ndarray[float]],
            right: bool = False,
            ) -> numpy.ndarray[float]:
        """
        Matches the input amount to a set of brackets and returns the sum of cell
        values from the lowest bracket to the one containing the input.
        """
        base1 = numpy.tile(tax_base, (len(self.thresholds), 1)).T
        thresholds1 = numpy.tile(numpy.hstack((self.thresholds, numpy.inf)), (len(tax_base), 1))
        a = numpy.maximum(numpy.minimum(base1, thresholds1[:, 1:]) - thresholds1[:, :-1], 0)
        return numpy.dot(self.amounts, a.T > 0)
