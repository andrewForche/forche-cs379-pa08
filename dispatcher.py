"""
PA 8: The VTable Dispatcher -- starter.

Complete VTable, build_vtable, USIObject, and dispatch below. See
PA_08_The_VTable_Dispatcher.md, Part B, for the full requirements.

Each table entry follows PA 7's Closure.call(args, caller_env) interface.
The harness supplies small closure-like methods so it can test dispatch
without adding string literals to the earlier interpreter grammar. Your
dispatch implementation must invoke .call with the receiver as the first
argument, followed by the explicit method arguments.
"""

from typing import Dict, Optional, Protocol


class MethodLike(Protocol):
    def call(self, args: list, caller_env) -> object:
        """PA 7 Closure-compatible call interface."""


class ClassDecl:
    """Given: a minimal class declaration -- just a name and its own (non-inherited) methods."""

    __slots__ = ("name", "methods")

    def __init__(self, name: str, methods: Dict[str, MethodLike]) -> None:
        self.name = name
        self.methods = methods  # methods declared on THIS class only


class VTable:
    def __init__(self, entries: Dict[str, MethodLike], owning_class_name: str = "?") -> None:
        self.entries = dict(entries)
        self.owning_class_name = owning_class_name

    def resolve(self, method_name: str) -> MethodLike:
        if method_name not in self.entries:
            raise AttributeError(
                f"Class '{self.owning_class_name}' "
                f"has no method '{method_name}'."
            )

        return self.entries[method_name]


def build_vtable(class_node: ClassDecl, parent_vtable: Optional[VTable] = None) -> VTable:
    if parent_vtable is None:
        entries = {}
    else:
        entries = parent_vtable.entries.copy()

    entries.update(class_node.methods)

    return VTable(
        entries,
        owning_class_name=class_node.name
    )


class USIObject:
    def __init__(self, class_descriptor: VTable, fields: dict) -> None:
        self.class_descriptor = class_descriptor
        self.fields = fields


def dispatch(obj: USIObject, method_name: str, args: list, caller_env) -> object:
    resolved_method = obj.class_descriptor.resolve(method_name)
    return resolved_method.call([obj, *args], caller_env)