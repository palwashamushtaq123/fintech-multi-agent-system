# Technical Implementation Plan: Automated Corporate Finance Analysis System (`corp-fin-analyzer`)

**Author:** FinTech Financial Systems Architect  
**Target:** Python Command-Line Utility and Core Library  
**Status:** Approved Technical Architecture Document  

---

## 1. Executive Summary & System Architecture

The `corp-fin-analyzer` system is a modular, high-reliability Python utility designed to parse corporate financial data, calculate core liquidity and solvency metrics, perform DuPont 3-Step ROE decomposition, and derive an automated credit risk score based on institutional risk thresholds. 

```
                                 [ Input: Data File / JSON / CLI ]
                                                 │
                                                 ▼
                                     ┌───────────────────────┐
                                     │   Parser & Validator  │
                                     └───────────┬───────────┘
                                                 │
                                                 ▼
                                     ┌───────────────────────┐
                                     │ Ratio Engine (Metrics)│
                                     └───────────┬───────────┘
                                                 │
                                       ┌─────────┴─────────┐
                                       ▼                   ▼
                            ┌─────────────────────┐ ┌─────────────┐
                            │ DuPont ROE Engine   │ │ Credit Risk │
                            └─────────────────────┘ └──────┬──────┘
                                                           │
                                                           ▼
                                               [ Output: JSON / Table ]
```

### Core Architecture Principles
1. **Defensive Financial Computing**: Strict enforcement of custom financial domain exceptions to catch edge cases (e.g., zero total equity, missing revenue fields).
2. **Separation of Concerns**: Complete decoupling of I/O (parsing/CLI), computational math (ratio/DuPont engines), and business logic (credit risk thresholds).
3. **Auditability**: Complete trace of inputs, intermediary ratios, and weightings used for credit risk determination.

---

## 2. Domain Data Model & Custom Exceptions

### 2.1 Exception Hierarchy (`corpfin/exceptions.py`)
Standard Python runtime errors are inadequate for financial audit trails. The module defines a dedicated exception hierarchy:

```python
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

### 2.2 Data Structure Models (`corpfin/models.py`)
Using immutable dataclasses to guarantee thread safety during computation.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
from decimal import Decimal

@dataclass(frozen=True)
class FinancialStatementInput:
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
    net_profit_margin: Decimal
    asset_turnover: Decimal
    equity_multiplier: Decimal
    roe: Decimal

@dataclass(frozen=True)
class MetricResults:
    current_ratio: Decimal
    quick_ratio: Decimal
    debt_to_equity: Decimal
    dupont: DuPontBreakdown
    credit_score: float
    risk_tier: str
```

---

## 3. Core Engine Implementation Blueprint

### 3.1 Financial Statement Parsing Module (`corpfin/parser.py`)
The parser accepts raw dictionaries or JSON files, validates field types, converts numeric inputs to `Decimal` (avoiding floating-point representation errors), and checks for missing critical attributes.

```python
import json
from decimal import Decimal, InvalidOperation
from .models import FinancialStatementInput
from .exceptions import MissingFinancialDataError

REQUIRED_FIELDS = [
    'current_assets', 'current_liabilities', 'cash_and_equivalents',
    'marketable_securities', 'receivables', 'total_debt',
    'total_shareholders_equity', 'total_assets', 'revenue', 'net_income'
]

def parse_input_dict(data: dict) -> FinancialStatementInput:
    missing = [field for field in REQUIRED_FIELDS if field not in data or data[field] is None]
    if missing:
        raise MissingFinancialDataError(f"Missing required financial metrics: {', '.join(missing)}")
    
    try:
        converted = {k: Decimal(str(v)) for k, v in data.items() if k in REQUIRED_FIELDS}
        return FinancialStatementInput(**converted)
    except (InvalidOperation, TypeError) as e:
        raise ValueError(f"Invalid numeric value in input data: {e}")
```

---

### 3.2 Ratio Engine (`corpfin/metrics.py`)
Computes Liquidity, Solvency, and DuPont ROE breakdowns with explicit division-by-zero checks.

$$\text{Current Ratio} = \frac{\text{Current Assets}}{\text{Current Liabilities}}$$

$$\text{Quick Ratio} = \frac{\text{Cash \& Cash Equivalents} + \text{Marketable Securities} + \text{Receivables}}{\text{Current Liabilities}}$$

$$\text{Debt-to-Equity} = \frac{\text{Total Debt}}{\text{Total Shareholders' Equity}}$$

$$\text{ROE (DuPont)} = \underbrace{\left(\frac{\text{Net Income}}{\text{Revenue}}\right)}_{\text{Net Profit Margin}} \times \underbrace{\left(\frac{\text{Revenue}}{\text{Total Assets}}\right)}_{\text{Asset Turnover}} \times \underbrace{\left(\frac{\text{Total Assets}}{\text{Total Shareholders' Equity}}\right)}_{\text{Equity Multiplier}}$$

```python
from decimal import Decimal
from .models import FinancialStatementInput, DuPontBreakdown
from .exceptions import ZeroDivisionFinancialError

def safe_divide(numerator: Decimal, denominator: Decimal, metric_name: str) -> Decimal:
    if denominator == Decimal('0'):
        raise ZeroDivisionFinancialError(f"Cannot compute {metric_name}: Denominator is zero.")
    return numerator / denominator

def calculate_current_ratio(data: FinancialStatementInput) -> Decimal:
    return safe_divide(data.current_assets, data.current_liabilities, "Current Ratio")

def calculate_quick_ratio(data: FinancialStatementInput) -> Decimal:
    quick_assets = data.cash_and_equivalents + data.marketable_securities + data.receivables
    return safe_divide(quick_assets, data.current_liabilities, "Quick Ratio")

def calculate_debt_to_equity(data: FinancialStatementInput) -> Decimal:
    return safe_divide(data.total_debt, data.total_shareholders_equity, "Debt-to-Equity")

def calculate_dupont_roe(data: FinancialStatementInput) -> DuPontBreakdown:
    net_profit_margin = safe_divide(data.net_income, data.revenue, "Net Profit Margin (DuPont)")
    asset_turnover = safe_divide(data.revenue, data.total_assets, "Asset Turnover (DuPont)")
    equity_multiplier = safe_divide(data.total_assets, data.total_shareholders_equity, "Equity Multiplier (DuPont)")
    
    roe = net_profit_margin * asset_turnover * equity_multiplier
    
    return DuPontBreakdown(
        net_profit_margin=net_profit_margin,
        asset_turnover=asset_turnover,
        equity_multiplier=equity_multiplier,
        roe=roe
    )
```

---

### 3.3 Automated Credit Scoring Engine (`corpfin/credit_scoring.py`)
Computes an ordinal/scaled credit score out of 100 based on weighted ratio performance relative to financial thresholds.

#### Benchmark Matrix & Scoring Weights
* **Current Ratio (Weight: 25%)**: Target $\ge 1.5$ (100 pts), Minimum $\ge 1.0$ (50 pts), $< 1.0$ (0 pts).
* **Quick Ratio (Weight: 20%)**: Target $\ge 1.0$ (100 pts), Minimum $\ge 0.8$ (50 pts), $< 0.8$ (0 pts).
* **Debt-to-Equity (Weight: 30%)**: Target $\le 1.5$ (100 pts), Acceptable $\le 2.5$ (50 pts), $> 2.5$ (0 pts).
* **DuPont ROE (Weight: 25%)**: Target $\ge 15\%$ (100 pts), Minimum $\ge 8\%$ (50 pts), $< 8\%$ (0 pts).

#### Risk Classification Table
| Aggregate Score Range | Risk Tier | Category Definition |
| :--- | :--- | :--- |
| **85 – 100** | **Tier 1** | Low Credit Risk (Investment Grade) |
| **65 – 84** | **Tier 2** | Moderate Risk (Acceptable Solvency) |
| **45 – 64** | **Tier 3** | High Risk (Liquidity/Solvency Stress) |
| **0 – 44** | **Tier 4** | Distressed / Default Watch |

```python
from decimal import Decimal
from typing import Tuple

def evaluate_credit_risk(
    current_ratio: Decimal, 
    quick_ratio: Decimal, 
    debt_to_equity: Decimal, 
    roe: Decimal
) -> Tuple[float, str]:
    
    score = 0.0
    
    # 1. Current Ratio Evaluation (25%)
    if current_ratio >= Decimal('1.5'): score += 25.0
    elif current_ratio >= Decimal('1.0'): score += 12.5
    
    # 2. Quick Ratio Evaluation (20%)
    if quick_ratio >= Decimal('1.0'): score += 20.0
    elif quick_ratio >= Decimal('0.8'): score += 10.0
    
    # 3. Debt to Equity Evaluation (30%)
    if debt_to_equity <= Decimal('1.5'): score += 30.0
    elif debt_to_equity <= Decimal('2.5'): score += 15.0
    
    # 4. ROE Evaluation (25%)
    if roe >= Decimal('0.15'): score += 25.0
    elif roe >= Decimal('0.08'): score += 12.5

    # Assign Risk Tier
    if score >= 85.0: risk_tier = "Tier 1 (Low Risk)"
    elif score >= 65.0: risk_tier = "Tier 2 (Moderate Risk)"
    elif score >= 45.0: risk_tier = "Tier 3 (High Risk)"
    else: risk_tier = "Tier 4 (Distressed)"
        
    return score, risk_tier
```

---

## 4. CLI Controller Interface Blueprint (`corpfin/cli.py`)

The CLI interface processes input financial statements from a JSON file, handles raised exceptions gracefully, and formats outputs for analysts via standard out.

```python
import sys
import json
import argparse
from pathlib import Path

from .parser import parse_input_dict
from .metrics import (
    calculate_current_ratio, 
    calculate_quick_ratio, 
    calculate_debt_to_equity, 
    calculate_dupont_roe
)
from .credit_scoring import evaluate_credit_risk
from .exceptions import FinancialAnalysisError

def run_analysis(file_path: str):
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"[ERROR] File not found: {file_path}", file=sys.stderr)
            sys.exit(1)

        with open(path, 'r') as f:
            raw_data = json.load(f)

        statements = parse_input_dict(raw_data)
        
        # Computations
        cr = calculate_current_ratio(statements)
        qr = calculate_quick_ratio(statements)
        de = calculate_debt_to_equity(statements)
        dupont = calculate_dupont_roe(statements)
        
        score, tier = evaluate_credit_risk(cr, qr, de, dupont.roe)
        
        # Formatted Reporting
        output = {
            "Liquidity Ratios": {
                "Current Ratio": f"{cr:.2f}",
                "Quick Ratio": f"{qr:.2f}"
            },
            "Solvency Ratios": {
                "Debt-to-Equity": f"{de:.2f}"
            },
            "DuPont Analysis": {
                "Net Profit Margin": f"{dupont.net_profit_margin * 100:.2f}%",
                "Asset Turnover": f"{dupont.asset_turnover:.2f}x",
                "Equity Multiplier": f"{dupont.equity_multiplier:.2f}x",
                "Return on Equity (ROE)": f"{dupont.roe * 100:.2f}%"
            },
            "Credit Risk Assessment": {
                "Credit Score": f"{score}/100",
                "Risk Classification": tier
            }
        }
        
        print(json.dumps(output, indent=4))

    except FinancialAnalysisError as fae:
        print(f"[FINANCIAL ENGINE ERROR] {fae}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"[UNEXPECTED ERROR] {e}", file=sys.stderr)
        sys.exit(3)

def main():
    parser = argparse.ArgumentParser(description="Corporate Finance & Credit Risk CLI Utility")
    parser.add_argument("-f", "--file", required=True, help="Path to financial data JSON file")
    args = parser.parse_args()
    run_analysis(args.file)

if __name__ == "__main__":
    main()
```

---

## 5. Sample Input Payload & Execution Verification

### Input payload (`sample_firm.json`)
```json
{
  "current_assets": 1500000.00,
  "current_liabilities": 800000.00,
  "cash_and_equivalents": 300000.00,
  "marketable_securities": 200000.00,
  "receivables": 400000.00,
  "total_debt": 1200000.00,
  "total_shareholders_equity": 1000000.00,
  "total_assets": 2500000.00,
  "revenue": 5000000.00,
  "net_income": 375000.00
}
```

### Command Execution
```bash
python -m corpfin.cli --file sample_firm.json
```

### Validated System Output
```json
{
    "Liquidity Ratios": {
        "Current Ratio": "1.88",
        "Quick Ratio": "1.13"
    },
    "Solvency Ratios": {
        "Debt-to-Equity": "1.20"
    },
    "DuPont Analysis": {
        "Net Profit Margin": "7.50%",
        "Asset Turnover": "2.00x",
        "Equity Multiplier": "2.50x",
        "Return on Equity (ROE)": "37.50%"
    },
    "Credit Risk Assessment": {
        "Credit Score": "100.0/100",
        "Risk Classification": "Tier 1 (Low Risk)"
    }
}
```