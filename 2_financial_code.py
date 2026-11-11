Below is the complete, production-ready Python implementation for the `corp-fin-analyzer` system (`corpfin` package). All code adheres strictly to PEP 8 standards, includes comprehensive docstrings, type hints, defensive numeric conversions using `Decimal`, and complete domain exception handling.

---

### File: `corpfin/__init__.py`

```python
"""Automated Corporate Finance Analysis System (`corpfin`).

This module provides high-reliability tools for parsing corporate financial statements,
calculating liquidity, solvency, and DuPont ROE decomposition metrics, and evaluating
credit risk scores.
"""

from .exceptions import (
    FinancialAnalysisError,
    InvalidThresholdError,
    MissingFinancialDataError,
    ZeroDivisionFinancialError,
)
from .models import (
    DuPontBreakdown,
    FinancialStatementInput,
    MetricResults,
)
from .parser import parse_input_dict
from .metrics import (
    calculate_current_ratio,
    calculate_debt_to_equity,
    calculate_dupont_roe,
    calculate_quick_ratio,
    analyze_financials,
)
from .credit_scoring import evaluate_credit_risk

__all__ = [
    "FinancialAnalysisError",
    "ZeroDivisionFinancialError",
    "MissingFinancialDataError",
    "InvalidThresholdError",
    "FinancialStatementInput",
    "DuPontBreakdown",
    "MetricResults",
    "parse_input_dict",
    "calculate_current_ratio",
    "calculate_quick_ratio",
    "calculate_debt_to_equity",
    "calculate_dupont_roe",
    "analyze_financials",
    "evaluate_credit_risk",
]
```

---

### File: `corpfin/exceptions.py`

```python
"""Custom exception domain model for financial computing audit trails."""


class FinancialAnalysisError(Exception):
    """Base exception for all financial engine errors."""

    pass


class ZeroDivisionFinancialError(FinancialAnalysisError):
    """Raised when a calculation denominator (e.g., Equity, Liabilities) is zero."""

    pass


class MissingFinancialDataError(FinancialAnalysisError):
    """Raised when required financial line items are missing from inputs."""

    pass


class InvalidThresholdError(FinancialAnalysisError):
    """Raised when credit risk threshold configurations violate logic boundaries."""

    pass
```

---

### File: `corpfin/models.py`

```python
"""Data models representing raw financial statements and analysis outputs."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class FinancialStatementInput:
    """Immutable data structure holding raw input line items from financial statements.
    
    All numeric values are enforced as `Decimal` to ensure exact financial arithmetic.
    """

    # Balance Sheet Items
    current_assets: Decimal
    current_liabilities: Decimal
    cash_and_equivalents: Decimal
    marketable_securities: Decimal
    receivables: Decimal
    total_debt: Decimal
    total_shareholders_equity: Decimal
    total_assets: Decimal

    # Income Statement Items
    revenue: Decimal
    net_income: Decimal


@dataclass(frozen=True)
class DuPontBreakdown:
    """Immutable representation of DuPont 3-Step Return on Equity (ROE) components."""

    net_profit_margin: Decimal
    asset_turnover: Decimal
    equity_multiplier: Decimal
    roe: Decimal


@dataclass(frozen=True)
class MetricResults:
    """Immutable collection of all computed financial metrics and risk evaluations."""

    current_ratio: Decimal
    quick_ratio: Decimal
    debt_to_equity: Decimal
    dupont: DuPontBreakdown
    credit_score: float
    risk_tier: str
```

---

### File: `corpfin/parser.py`

```python
"""Data parsing and validation module for corporate financial input data."""

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Tuple

from .exceptions import MissingFinancialDataError
from .models import FinancialStatementInput

REQUIRED_FIELDS: Tuple[str, ...] = (
    "current_assets",
    "current_liabilities",
    "cash_and_equivalents",
    "marketable_securities",
    "receivables",
    "total_debt",
    "total_shareholders_equity",
    "total_assets",
    "revenue",
    "net_income",
)


def parse_input_dict(data: Dict[str, Any]) -> FinancialStatementInput:
    """Parses, validates, and converts a dictionary of raw financial values into a type-safe input model.

    Args:
        data (Dict[str, Any]): Dictionary containing financial line items.

    Returns:
        FinancialStatementInput: Validated immutable financial input dataclass.

    Raises:
        MissingFinancialDataError: If any required financial fields are missing or None.
        ValueError: If any field value cannot be parsed as a valid Decimal.
    """
    missing = [
        field for field in REQUIRED_FIELDS if field not in data or data[field] is None
    ]
    if missing:
        raise MissingFinancialDataError(
            f"Missing required financial metrics: {', '.join(missing)}"
        )

    converted: Dict[str, Decimal] = {}
    for key in REQUIRED_FIELDS:
        val = data[key]
        try:
            converted[key] = Decimal(str(val))
        except (InvalidOperation, TypeError) as exc:
            raise ValueError(
                f"Invalid numeric value for key '{key}': '{val}'. Error: {exc}"
            ) from exc

    return FinancialStatementInput(**converted)
```

---

### File: `corpfin/metrics.py`

```python
"""Core computational engine for calculating liquidity, solvency, and DuPont ROE metrics."""

from decimal import Decimal

from .credit_scoring import evaluate_credit_risk
from .exceptions import ZeroDivisionFinancialError
from .models import DuPontBreakdown, FinancialStatementInput, MetricResults


def safe_divide(numerator: Decimal, denominator: Decimal, metric_name: str) -> Decimal:
    """Executes division using standard Decimal math while catching zero-division states.

    Args:
        numerator (Decimal): Dividend in the ratio computation.
        denominator (Decimal): Divisor in the ratio computation.
        metric_name (str): Label for the ratio being calculated (for context on error).

    Returns:
        Decimal: The result of the division operation.

    Raises:
        ZeroDivisionFinancialError: If denominator is equal to Decimal('0').
    """
    if denominator == Decimal("0"):
        raise ZeroDivisionFinancialError(
            f"Cannot compute {metric_name}: Denominator is zero."
        )
    return numerator / denominator


def calculate_current_ratio(data: FinancialStatementInput) -> Decimal:
    """Calculates the Current Ratio (Current Assets / Current Liabilities)."""
    return safe_divide(data.current_assets, data.current_liabilities, "Current Ratio")


def calculate_quick_ratio(data: FinancialStatementInput) -> Decimal:
    """Calculates the Quick Ratio ((Cash + Securities + Receivables) / Current Liabilities)."""
    quick_assets = (
        data.cash_and_equivalents + data.marketable_securities + data.receivables
    )
    return safe_divide(quick_assets, data.current_liabilities, "Quick Ratio")


def calculate_debt_to_equity(data: FinancialStatementInput) -> Decimal:
    """Calculates the Debt-to-Equity Ratio (Total Debt / Shareholders' Equity)."""
    return safe_divide(
        data.total_debt, data.total_shareholders_equity, "Debt-to-Equity"
    )


def calculate_dupont_roe(data: FinancialStatementInput) -> DuPontBreakdown:
    """Performs 3-Step DuPont Return on Equity (ROE) analysis.

    ROE = Net Profit Margin * Asset Turnover * Equity Multiplier

    Args:
        data (FinancialStatementInput): Input financial data object.

    Returns:
        DuPontBreakdown: Individual DuPont component ratios and aggregate ROE.
    """
    net_profit_margin = safe_divide(
        data.net_income, data.revenue, "Net Profit Margin (DuPont)"
    )
    asset_turnover = safe_divide(
        data.revenue, data.total_assets, "Asset Turnover (DuPont)"
    )
    equity_multiplier = safe_divide(
        data.total_assets, data.total_shareholders_equity, "Equity Multiplier (DuPont)"
    )

    roe = net_profit_margin * asset_turnover * equity_multiplier

    return DuPontBreakdown(
        net_profit_margin=net_profit_margin,
        asset_turnover=asset_turnover,
        equity_multiplier=equity_multiplier,
        roe=roe,
    )


def analyze_financials(data: FinancialStatementInput) -> MetricResults:
    """Executes full ratio analysis pipeline and computes overall credit score.

    Args:
        data (FinancialStatementInput): Input financial statements.

    Returns:
        MetricResults: Complete financial ratio and risk evaluation model.
    """
    cr = calculate_current_ratio(data)
    qr = calculate_quick_ratio(data)
    de = calculate_debt_to_equity(data)
    dupont = calculate_dupont_roe(data)

    score, tier = evaluate_credit_risk(cr, qr, de, dupont.roe)

    return MetricResults(
        current_ratio=cr,
        quick_ratio=qr,
        debt_to_equity=de,
        dupont=dupont,
        credit_score=score,
        risk_tier=tier,
    )
```

---

### File: `corpfin/credit_scoring.py`

```python
"""Automated credit risk evaluation engine based on institutional scoring thresholds."""

from decimal import Decimal
from typing import Tuple


def evaluate_credit_risk(
    current_ratio: Decimal,
    quick_ratio: Decimal,
    debt_to_equity: Decimal,
    roe: Decimal,
) -> Tuple[float, str]:
    """Computes a credit score out of 100 and maps it to an institutional risk classification tier.

    Scoring Weights:
    - Current Ratio (25%): >= 1.5 (25.0 pts), >= 1.0 (12.5 pts), < 1.0 (0 pts)
    - Quick Ratio (20%): >= 1.0 (20.0 pts), >= 0.8 (10.0 pts), < 0.8 (0 pts)
    - Debt-to-Equity (30%): <= 1.5 (30.0 pts), <= 2.5 (15.0 pts), > 2.5 (0 pts)
    - DuPont ROE (25%): >= 15% (25.0 pts), >= 8% (12.5 pts), < 8% (0 pts)

    Args:
        current_ratio (Decimal): Computed Current Ratio.
        quick_ratio (Decimal): Computed Quick Ratio.
        debt_to_equity (Decimal): Computed Debt-to-Equity Ratio.
        roe (Decimal): Computed Return on Equity (as a decimal fraction, e.g., 0.15 = 15%).

    Returns:
        Tuple[float, str]: Total numerical credit score (0-100) and risk tier classification.
    """
    score = 0.0

    # 1. Current Ratio Evaluation (25%)
    if current_ratio >= Decimal("1.5"):
        score += 25.0
    elif current_ratio >= Decimal("1.0"):
        score += 12.5

    # 2. Quick Ratio Evaluation (20%)
    if quick_ratio >= Decimal("1.0"):
        score += 20.0
    elif quick_ratio >= Decimal("0.8"):
        score += 10.0

    # 3. Debt to Equity Evaluation (30%)
    if debt_to_equity <= Decimal("1.5"):
        score += 30.0
    elif debt_to_equity <= Decimal("2.5"):
        score += 15.0

    # 4. ROE Evaluation (25%)
    if roe >= Decimal("0.15"):
        score += 25.0
    elif roe >= Decimal("0.08"):
        score += 12.5

    # Assign Risk Tier
    if score >= 85.0:
        risk_tier = "Tier 1 (Low Risk)"
    elif score >= 65.0:
        risk_tier = "Tier 2 (Moderate Risk)"
    elif score >= 45.0:
        risk_tier = "Tier 3 (High Risk)"
    else:
        risk_tier = "Tier 4 (Distressed)"

    return score, risk_tier
```

---

### File: `corpfin/cli.py`

```python
"""Command Line Interface (CLI) driver for the Corporate Finance Analysis System."""

import argparse
import json
import sys
from pathlib import Path

from .exceptions import FinancialAnalysisError
from .metrics import analyze_financials
from .parser import parse_input_dict


def run_analysis(file_path: str) -> None:
    """Loads a JSON file, parses financial data, executes analytics, and outputs JSON metrics.

    Args:
        file_path (str): File system path to input financial JSON statement.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"[ERROR] Input file not found: '{file_path}'", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"[ERROR] Invalid JSON file format: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        statements = parse_input_dict(raw_data)
        metrics = analyze_financials(statements)

        formatted_output = {
            "Liquidity Ratios": {
                "Current Ratio": f"{metrics.current_ratio:.2f}",
                "Quick Ratio": f"{metrics.quick_ratio:.2f}",
            },
            "Solvency Ratios": {
                "Debt-to-Equity": f"{metrics.debt_to_equity:.2f}",
            },
            "DuPont Analysis": {
                "Net Profit Margin": f"{metrics.dupont.net_profit_margin * 100:.2f}%",
                "Asset Turnover": f"{metrics.dupont.asset_turnover:.2f}x",
                "Equity Multiplier": f"{metrics.dupont.equity_multiplier:.2f}x",
                "Return on Equity (ROE)": f"{metrics.dupont.roe * 100:.2f}%",
            },
            "Credit Risk Assessment": {
                "Credit Score": f"{metrics.credit_score:.1f}/100",
                "Risk Classification": metrics.risk_tier,
            },
        }

        print(json.dumps(formatted_output, indent=4))

    except FinancialAnalysisError as fae:
        print(f"[FINANCIAL ENGINE ERROR] {fae}", file=sys.stderr)
        sys.exit(2)
    except Exception as exc:
        print(f"[UNEXPECTED ERROR] {exc}", file=sys.stderr)
        sys.exit(3)


def main() -> None:
    """CLI entry point routine."""
    parser = argparse.ArgumentParser(
        description="Corporate Finance & Automated Credit Risk CLI Utility"
    )
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="Path to JSON file containing target firm financial statements",
    )
    args = parser.parse_args()
    run_analysis(args.file)


if __name__ == "__main__":
    main()
```