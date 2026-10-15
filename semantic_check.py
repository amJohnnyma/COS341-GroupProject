from variable_rules import check_variable_rules
from function_rules import check_function_rules

def run_all_checks(crawler, symbol_table):
    errors = check_variable_rules(crawler, symbol_table)
    errors.extend(check_function_rules(crawler, symbol_table))
    return errors
