"""Peer group configuration (company resolution layer, PRD Section 14).

Static for Phase 1 -- the 7-company mortgage-servicer peer group used
throughout the reference design (Servicer_Peer_Terminal_Render.html).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Company:
    ticker: str
    name: str
    note: str
    cik: str


COMPANIES: tuple[Company, ...] = (
    Company("RKT", "Rocket Companies", "incl. Mr. Cooper", "0001805284"),
    Company("RITM", "Rithm Capital", "Newrez", "0001556593"),
    Company("PFSI", "PennyMac Financial Services", "", "0001745916"),
    Company("ONIT", "Onity Group", "fka Ocwen", "0000873860"),
    Company("PMT", "PennyMac Mortgage Inv. Trust", "REIT", "0001464423"),
    Company("NLY", "Annaly Capital Management", "REIT", "0001043219"),
    Company("TWO", "Two Harbors Investment", "RoundPoint", "0001465740"),
)

BY_TICKER: dict[str, Company] = {c.ticker: c for c in COMPANIES}
