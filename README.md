Contractual is a simple mocking library that lets you configure the two sides
of a mock relationship in a way that allows each side to verify the correct
behavior.

A single contract will have a provider and a consumer- the consumer gets a 
mock object that, when called with the specified arguments, will return the
expected value. The provider gets a convenience decorator, that combined with
a test function, will call the test function with the same arguments that are
used by the consumer and verify that the result is as the consumer expects.

The basic object is a Contractual object. This has a dictionary of contracts.
For each contract, there is a list of calls, each of which is a dictionary. A
call is of the form-

```python
{
	'preconditions': (val, val),
	'args': (val, val),
	'kwargs': {'kw': val, 'kw2': val},
	'return': val,
}
```

An example contract could be formed like-

```python
contractual = Contractual({
	'function_for_contract_args': [
		{
			'args': (2, 2),
			'return': 4,
		},
		{
			'args': (3, 5),
			'return': 8,
		},
	],
	'function_for_contract_kwargs': [
		{
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

```

This allows you to set up both mocks and verification tests as such-
```python
mock_obj_args = contractual.contract_mock('function_for_contract_args')

@contractual.contract('function_for_contract_args')
def check_contract_args(args, kwargs, preconditions):
	return function_with_args(*args)

mock_obj_args(2, 2) == 4
mock_obj_args(1, 7) # raises ContractError- these args aren't in the contract!

check_contract_args()
"""
asserts that function_with_args(2, 2) == 4 and function_with_args(3, 5) == 8
"""

```

Preconditions allow you to handle some setup of the function in question. They
are an extra set of arguments that get passed to the contract function. As an example-

```python
class Employee:
	def __init__(self, name):
		self.name = name
	def ret(self):
		return {'name': self.name}

employee_dict = {}

def get_employee(id):
	return employee_dict.get(id).ret()

contractual = Contractual({
	'function_for_contract_precondition': [
		{
			'preconditions': (7, 'tim'),
			'args': (7),
			'return': {'name': 'tim'},
		},
	]
})

# use the mock_obj by setting up preconditions before use on the consumer side
mock_obj = contractual.contract_mock('function_for_contract_precondition')
mock_obj(7)  # raises ContractError
with mock_obj.pre(7, 'tim'):
	mock_obj(7) == {'name': 'tim'}

# setup the producer side by writing a function that uses the
# preconditions array to setup state, and then call the function 
# in question
@contractual.contract('function_for_contract_precondition')
def check_contract(args, kwargs, preconditions):
	employee = Employee(preconditions[1])
	employee_dict[preconditions[0]] = employee
	return get_employee(*args)

```
As you can see, what actually goes into the preconditions arg is quite flexible, 
and will need to be decided between the producers and consumers.

The last important note is that you can use yaml files to share config in case the producer
and consumer live in separate code bases.

```yaml
function_for_contract_args:
  - args: [2, 2]
    return: 4
  - args: [3, 5]
    return: 8

function_for_contract_kwargs:
  - kwargs:
      kw: 7
    return: 5

function_for_contract_precondition:
  - preconditions: [7]
    args: [2, 2]
    return: 11
  - preconditions: [5]
    args: [3, 5]
    return: 13
```
```python
contractual = Contractual.from_yaml('my_yaml_filename.yaml')
```
This is equivalent to the python definition above.
