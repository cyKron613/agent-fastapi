def param_invalid_details(param: str) -> str:
    return f"the param: {param} is invalid!"


def not_found_details(entity: str) -> str:
    return f"the `{entity}` doesn't exist!"


def already_exist_details(entity: str) -> str:
    return f"the `{entity}` already exist!"
