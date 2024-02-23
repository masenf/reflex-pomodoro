"""Helpers for dealing with browser-local state."""
import reflex as rx
from reflex.components.component import MemoizationLeaf


class IntegralFragment(rx.Fragment, MemoizationLeaf):
    """A fragment that does not individually memoize its children."""


integral_fragment = IntegralFragment.create


def useState(name, initial_value) -> tuple[rx.Var, str]:
    """Create a react browser useState var.

    Args:
        name: The name of the state variable.
        initial_value: The initial value of the state variable.

    Returns:
        A tuple of the state variable and the name of the setter function.
    """
    set_name = f"set_{name}"
    var_type = type(initial_value)
    get_var = rx.Var.create(name)._replace(
        _var_type=var_type,
        _var_is_local=False,
        _var_is_string=False,
        merge_var_data=rx.vars.VarData(
            imports={"react": {rx.utils.imports.ImportVar(tag="useState")}},
            hooks={f"const [{name}, {set_name}] = useState({initial_value});"},
        ),
    )
    return get_var, set_name
