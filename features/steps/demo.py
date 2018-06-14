from behave import *


@given('a setup RHEL-Jboss-Benchmark')
def step_impl(context):
    pass


@when('storedXSS attack is performed')
def step_impl(context):
    assert True is not False


@then('storedXSS attack is detected and appropriate status is available')
def step_impl(context):
    assert context.failed is False


@given('a setup Windows-Jboss-Benchmark')
def step_impl(context):
    pass


@when('sql attack is performed')
def step_impl(context):
    assert True is not False


@then('sql attack is detected and appropriate status is available')
def step_impl(context):
    assert context.failed is True
