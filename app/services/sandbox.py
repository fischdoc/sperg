""" safely execute custom code sent by client """
from RestrictedPython import compile_restricted_exec
from RestrictedPython.Eval import default_guarded_getiter, default_guarded_getitem
from types import FunctionType


def execute_recommendation(code_str: str, allowed_globals: dict, function_name: str) -> FunctionType:
    compiled_result = compile_restricted_exec(code_str)
    byte_code = compiled_result.code

    if compiled_result.errors:
        raise ValueError(f"Compilation error: {compiled_result.errors}")

    SAFE_BUILTINS = {
        "len": len,
        "range": range,
        "min": min,
        "max": max,
        # expose more if needed
    }

    global_env = {
        "__builtins__": SAFE_BUILTINS,
        "_getiter_": default_guarded_getiter,
        "_getitem_": default_guarded_getitem,
        **allowed_globals
    }

    local_env = {}

    exec(byte_code, global_env, local_env)

    # function name must match generator field
    if function_name not in local_env:
        raise ValueError(f"No function named '{function_name}' found in the submitted code")

    # get func and ensure its callable
    function = local_env[function_name]
    if not callable(function):
        raise ValueError(f"'{function_name}' is not a callable function")

    return function
