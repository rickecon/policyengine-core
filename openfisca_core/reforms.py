# -*- coding: utf-8 -*-

import copy

from .parameters import Node
from .taxbenefitsystems import TaxBenefitSystem


class Reform(TaxBenefitSystem):
    """A modified TaxBenefitSystem

    In OpenFisca, a reform is a modified TaxBenefitSystem. It can add or replace variables and call `self.modify_parameters()` to modify the parameters of the legislation. All reforms must subclass `Reform` and implement a math `apply()`. Such a function can add or replace variables and call `self.modify_parameters()` to modify the parameters of the legislation.

    Example:

    >>> from openfisca_core import reforms
    >>> from openfisca_core.parameters import load_file
    >>>
    >>> def modify_my_parameters(parameters):
    >>>     # Add new parameters
    >>>     new_parameters = load_file(name='reform_name', file_path='path_to_yaml_file.yaml')
    >>>     parameters.add_child('reform_name', new_parameters)
    >>>
    >>>     # Update a value
    >>>     parameters.taxes.some_tax.some_param.update(period=some_period, value=1000.0)
    >>>
    >>>    return parameters
    >>>
    >>> class MyReform(reforms.Reform):
    >>>    def apply(self):
    >>>        self.add_variable(some_variable)
    >>>        self.update_variable(some_other_variable)
    >>>        self.modify_parameters(modifier_function=modify_my_parameters)
    """
    name = None

    def __init__(self, baseline):
        """
        :param baseline: Baseline TaxBenefitSystem.
        """
        self.baseline = baseline
        self._parameters = baseline.get_parameters()
        self._parameters_at_instant_cache = baseline._parameters_at_instant_cache
        self.column_by_name = baseline.column_by_name.copy()
        self.decomposition_file_path = baseline.decomposition_file_path
        self.Scenario = baseline.Scenario
        self.key = unicode(self.__class__.__name__)
        if not hasattr(self, 'apply'):
            raise Exception("Reform {} must define an `apply` function".format(self.key))
        self.apply()

    def __getattr__(self, attribute):
        return getattr(self.baseline, attribute)

    @property
    def full_key(self):
        key = self.key
        assert key is not None, 'key was not set for reform {} (name: {!r})'.format(self, self.name)
        if self.baseline is not None and hasattr(self.baseline, 'key'):
            baseline_full_key = self.baseline.full_key
            key = u'.'.join([baseline_full_key, key])
        return key

    def modify_parameters(self, modifier_function):
        """
        Make modifications on the parameters of the legislation

        Call this function in `apply()` if the reform asks for legislation parameter modifications.

        :param modifier_function: A function that takes an object of type `openfisca_core.parameters.Node` and should return an object of the same type.
        """
        baseline_parameters = self.baseline.get_parameters()
        baseline_parameters_copy = copy.deepcopy(baseline_parameters)
        reform_parameters = modifier_function(baseline_parameters_copy)
        assert reform_parameters is not None, \
            'modifier_function {} in module {} must return the modified parameters'.format(
                modifier_function.__name__,
                modifier_function.__module__,
                )
        assert isinstance(reform_parameters, Node)
        self._parameters = reform_parameters
        self._parameters_at_instant_cache = {}
