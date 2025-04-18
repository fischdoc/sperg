""" safely execute custom code sent by client """
from RestrictedPython import compile_restricted_exec
from RestrictedPython.Eval import default_guarded_getiter, default_guarded_getitem
from types import FunctionType


def execute_recommendation(code_str: str, allowed_globals: dict) -> FunctionType:
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

    if "recommend" not in local_env:
        raise ValueError("No function named 'recommend' found in submitted code")

    return local_env["recommend"]
