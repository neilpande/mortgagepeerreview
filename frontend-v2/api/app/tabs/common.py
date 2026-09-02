"""Helpers shared by every tab assembler."""

from __future__ import annotations

from ..schemas import SourcedValue


def sourced(fact: dict | None) -> SourcedValue:
    if fact is None:
        return SourcedValue(value=None)
    return SourcedValue(
        value=fact["value"],
        tag=fact["tag"],
        form=fact["form"],
        filed=fact["filed"],
        accn=fact["accn"],
        end=fact["end"],
    )
