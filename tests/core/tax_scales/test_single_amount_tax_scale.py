from pytest import fixture

from numpy import array

from openfisca_core.parameters import Scale
from openfisca_core.periods import Instant
from openfisca_core.taxscales import SingleAmountTaxScale
from openfisca_core.tools import assert_near


@fixture
def data():
    return {
        "description": "Social security contribution tax scale",
        "metadata": {
            "type": "single_amount",
            "threshold_unit": "currency-EUR",
            "rate_unit": "/1",
            },
        "brackets": [
            {
                "threshold": {"2017-10-01": {"value": 0.23}},
                "amount": {"2017-10-01": {"value": 6}, },
                }
            ],
        }


def test_calc():
    tax_base = array([1, 8, 10])
    tax_scale = SingleAmountTaxScale()
    tax_scale.add_bracket(6, 0.23)
    tax_scale.add_bracket(9, 0.29)

    result = tax_scale.calc(tax_base)

    assert_near(result, [0, 0.23, 0.29])


def test_to_dict():
    tax_scale = SingleAmountTaxScale()
    tax_scale.add_bracket(6, 0.23)
    tax_scale.add_bracket(9, 0.29)

    result = tax_scale.to_dict()

    assert result == {"6": 0.23, "9": 0.29}


# TODO: move, as we're testing Scale, not SingleAmountTaxScale
def test_assign_thresholds_on_creation(data):
    scale = Scale("amount_scale", data, "")
    first_jan = Instant((2017, 11, 1))
    scale_at_instant = scale.get_at_instant(first_jan)

    result = scale_at_instant.thresholds

    assert result == [0.23]


# TODO: move, as we're testing Scale, not SingleAmountTaxScale
def test_assign_amounts_on_creation(data):
    scale = Scale("amount_scale", data, "")
    first_jan = Instant((2017, 11, 1))
    scale_at_instant = scale.get_at_instant(first_jan)

    result = scale_at_instant.amounts

    assert result == [6]


# TODO: move, as we're testing Scale, not SingleAmountTaxScale
def test_dispatch_scale_type_on_creation(data):
    scale = Scale("amount_scale", data, "")
    first_jan = Instant((2017, 11, 1))

    result = scale.get_at_instant(first_jan)

    assert isinstance(result, SingleAmountTaxScale)
