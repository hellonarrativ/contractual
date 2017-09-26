from unittest import TestCase

from contractual import Contractual, ContractException

"""
This is a set of three functions that we want to write tests
for, which we will mock out on the calling side, and then
verify the actual function behavior agrees with the mocked
behavior
"""


def function_with_args(arg1, arg2):
    return arg1 + arg2


def function_with_kwargs(kw):
    return kw - 2


def function_with_fixtures(fix, arg1, arg2):
    return fix + arg1 + arg2


class TestContractual(TestCase):
    """
    This contract defines the expected behavior of the above
    functions. Each function has a list of contracts. For each
    of those, we have precondition arguments, args, kwargs, and
    an expected return value. If a Mock is created using this
    contract, and it is called with one of the given sets
    of arguments, it will return the given value. If called with
    anything else, it will raise an exception. There is a context
    manager that allows you to set up preconditions that must
    be in place before the mock object would be expected to
    return the given value.

    On the other side, we can create a function decorated with
    this contract to test the behavior of the function. If the
    decorated function is called, it will call the underlying
    function with each set of arguments and assert that the
    return value matches.
    """
    contractual = Contractual({
        'function_for_contract_args': [
            {
                'preconditions': None,
                'args': (2, 2),
                'return': 4,
            },
            {
                'preconditions': None,
                'args': (3, 5),
                'return': 8,
            },
        ],
        'function_for_contract_kwargs': [
            {
                'preconditions': None,
                'kwargs': {'kw': 7},
                'return': 5,
            }
        ],
        'function_for_contract_precondition': [
            {
                'preconditions': (7,),
                'args': (2, 2),
                'return': 11,
            },
            {
                'preconditions': (5,),
                'args': (3, 5),
                'return': 13,
            },
        ]
    })

    def setUp(self):

        # The mock objects created to replace the three functions in tests
        self.mock_obj_args = self.contractual.contract_mock('function_for_contract_args')
        self.mock_obj_kwargs = self.contractual.contract_mock('function_for_contract_kwargs')
        self.mock_obj_pre = self.contractual.contract_mock('function_for_contract_precondition')

        # the contract verification functions
        @self.contractual.contract('function_for_contract_args')
        def check_contract_args(args, kwargs, preconditions):
            return function_with_args(*args)

        @self.contractual.contract('function_for_contract_args')
        def bad_contract_function(args, kwargs, preconditions):
            return 0

        @self.contractual.contract('function_for_contract_kwargs')
        def check_contract_kwargs(args, kwargs, preconditions):
            return function_with_kwargs(**kwargs)

        @self.contractual.contract('function_for_contract_precondition')
        def check_contract_precondition(args, kwargs, preconditions):
            return function_with_fixtures(*preconditions, *args)

        self.funcs = {
            'check_contract_args': check_contract_args,
            'bad_contract_function': bad_contract_function,
            'check_contract_kwargs': check_contract_kwargs,
            'check_contract_precondition': check_contract_precondition,
        }

    def test_mocked_side_works(self):
        self.assertEqual(self.mock_obj_args(2, 2), 4)
        self.assertEqual(self.mock_obj_args(3, 5), 8)
        with self.assertRaises(ContractException):
            # Won't return anything, this isn't a defined
            # set of arguments
            self.mock_obj_args(1, 4)

    def test_mocked_kwargs(self):
        self.assertEqual(self.mock_obj_kwargs(kw=7), 5)

    def test_mocked_precondition(self):
        with self.mock_obj_pre.pre(7):
            # the mock will only return the given value if
            # the preconditions are set using the context
            # manager
            self.assertEqual(self.mock_obj_pre(2, 2), 11)
        with self.mock_obj_pre.pre(5):
            self.assertEqual(self.mock_obj_pre(3, 5), 13)

    def test_bad_mocked_precondition(self):
        with self.assertRaises(ContractException):
            with self.mock_obj_pre.pre(5):
                self.assertEqual(self.mock_obj_pre(2, 2), 11)

    def test_preconditions_cleared(self):
        with self.mock_obj_pre.pre(7):
            self.assertEqual(self.mock_obj_pre(2, 2), 11)
        with self.assertRaises(ContractException):
            self.assertEqual(self.mock_obj_pre(2, 2), 11)

    def test_bad_contract_raises(self):
        with self.assertRaises(ContractException):
            # the test function, when called with the contract
            # arguments, returns a value different than what
            # the contract specifies
            self.funcs['bad_contract_function']()

    def test_contract_args(self):
        # This checks ALL of the given sets of args against
        # the test function
        self.funcs['check_contract_args']()

    def test_contract_kwargs(self):
        self.funcs['check_contract_kwargs']()

    def test_contract_precons(self):
        self.funcs['check_contract_precondition']()


class TestContractualYaml(TestContractual):
    contractual = Contractual.from_yaml('test_definition.yaml')

