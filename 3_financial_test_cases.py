```python
"""Comprehensive Unit Test Suite for the Corporate Finance Analysis System (`corpfin`).

Author: Financial QA Test Engineer
Target Package: corpfin
Framework: Python unittest
"""

from decimal import Decimal
import unittest

from corpfin.credit_scoring import evaluate_credit_risk
from corpfin.exceptions import (
    FinancialAnalysisError,
    MissingFinancialDataError,
    ZeroDivisionFinancialError,
)
from corpfin.metrics import (
    analyze_financials,
    calculate_current_ratio,
    calculate_debt_to_equity,
    calculate_dupont_roe,
    calculate_quick_ratio,
    safe_divide,
)
from corpfin.models import (
    DuPontBreakdown,
    FinancialStatementInput,
    MetricResults,
)
from corpfin.parser import parse_input_dict


class TestFinancialParser(unittest.TestCase):
    """Unit tests for `corpfin.parser.parse_input_dict` input parsing and validation."""

    def setUp(self) -> None:
        self.valid_payload = {
            "current_assets": "1500000.00",
            "current_liabilities": "800000.00",
            "cash_and_equivalents": "300000.00",
            "marketable_securities": "200000.00",
            "receivables": "400000.00",
            "total_debt": "1200000.00",
            "total_shareholders_equity": "1000000.00",
            "total_assets": "2500000.00",
            "revenue": "5000000.00",
            "net_income": "375000.00",
        }

    def test_parse_valid_payload_success(self) -> None:
        """Verify successful conversion of standard dict values to Decimal model."""
        parsed = parse_input_dict(self.valid_payload)
        self.assertIsInstance(parsed, FinancialStatementInput)
        self.assertEqual(parsed.current_assets, Decimal("1500000.00"))
        self.assertEqual(parsed.net_income, Decimal("375000.00"))

    def test_parse_missing_required_field_raises_exception(self) -> None:
        """Verify MissingFinancialDataError when required keys are omitted."""
        invalid_payload = self.valid_payload.copy()
        del invalid_payload["total_shareholders_equity"]
        
        with self.assertRaises(MissingFinancialDataError) as ctx:
            parse_input_dict(invalid_payload)
        self.assertIn("total_shareholders_equity", str(ctx.exception))

    def test_parse_none_field_value_raises_exception(self) -> None:
        """Verify MissingFinancialDataError when a required field value is None."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["revenue"] = None
        
        with self.assertRaises(MissingFinancialDataError) as ctx:
            parse_input_dict(invalid_payload)
        self.assertIn("revenue", str(ctx.exception))

    def test_parse_invalid_numeric_format_raises_value_error(self) -> None:
        """Verify ValueError is raised when non-numeric strings are supplied."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["current_assets"] = "INVALID_NUMBER"
        
        with self.assertRaises(ValueError) as ctx:
            parse_input_dict(invalid_payload)
        self.assertIn("current_assets", str(ctx.exception))


class TestSafeDivide(unittest.TestCase):
    """Unit tests for `corpfin.metrics.safe_divide` defensive division logic."""

    def test_safe_divide_valid_computation(self) -> None:
        """Verify normal Decimal division behavior."""
        result = safe_divide(Decimal("100"), Decimal("4"), "Test Ratio")
        self.assertEqual(result, Decimal("25"))

    def test_safe_divide_zero_denominator_raises_financial_exception(self) -> None:
        """Verify ZeroDivisionFinancialError is raised when denominator is zero."""
        with self.assertRaises(ZeroDivisionFinancialError) as ctx:
            safe_divide(Decimal("100"), Decimal("0"), "Test Ratio")
        self.assertIn("Cannot compute Test Ratio: Denominator is zero.", str(ctx.exception))
        self.assertTrue(issubclass(ZeroDivisionFinancialError, FinancialAnalysisError))


class TestRatioEngine(unittest.TestCase):
    """Unit tests for liquidity, solvency, and DuPont ROE calculations."""

    def setUp(self) -> None:
        self.standard_input = FinancialStatementInput(
            current_assets=Decimal("1500000.00"),
            current_liabilities=Decimal("800000.00"),
            cash_and_equivalents=Decimal("300000.00"),
            marketable_securities=Decimal("200000.00"),
            receivables=Decimal("400000.00"),
            total_debt=Decimal("1200000.00"),
            total_shareholders_equity=Decimal("1000000.00"),
            total_assets=Decimal("2500000.00"),
            revenue=Decimal("5000000.00"),
            net_income=Decimal("375000.00"),
        )

    def test_calculate_current_ratio_standard(self) -> None:
        """Verify Current Ratio calculation (1,500,000 / 800,000 = 1.875)."""
        expected = Decimal("1.875")
        actual = calculate_current_ratio(self.standard_input)
        self.assertEqual(actual, expected)

    def test_calculate_quick_ratio_standard(self) -> None:
        """Verify Quick Ratio calculation ((300k + 200k + 400k) / 800k = 1.125)."""
        expected = Decimal("1.125")
        actual = calculate_quick_ratio(self.standard_input)
        self.assertEqual(actual, expected)

    def test_calculate_debt_to_equity_standard(self) -> None:
        """Verify Debt-to-Equity ratio calculation (1,200,000 / 1,000,000 = 1.2)."""
        expected = Decimal("1.2")
        actual = calculate_debt_to_equity(self.standard_input)
        self.assertEqual(actual, expected)

    def test_calculate_dupont_roe_standard(self) -> None:
        """Verify DuPont ROE decomposition calculation components and aggregate identity."""
        dupont = calculate_dupont_roe(self.standard_input)
        
        self.assertIsInstance(dupont, DuPontBreakdown)
        self.assertEqual(dupont.net_profit_margin, Decimal("0.075"))  # 375k / 5m
        self.assertEqual(dupont.asset_turnover, Decimal("2.0"))       # 5m / 2.5m
        self.assertEqual(dupont.equity_multiplier, Decimal("2.5"))    # 2.5m / 1m
        self.assertEqual(dupont.roe, Decimal("0.375"))                # 7.5% * 2.0 * 2.5 = 37.5%

    def test_zero_liabilities_raises_division_by_zero(self) -> None:
        """Verify zero current liabilities raises ZeroDivisionFinancialError."""
        zero_liab_input = FinancialStatementInput(
            current_assets=Decimal("100"),
            current_liabilities=Decimal("0"),
            cash_and_equivalents=Decimal("10"),
            marketable_securities=Decimal("10"),
            receivables=Decimal("10"),
            total_debt=Decimal("50"),
            total_shareholders_equity=Decimal("100"),
            total_assets=Decimal("200"),
            revenue=Decimal("500"),
            net_income=Decimal("50"),
        )
        with self.assertRaises(ZeroDivisionFinancialError):
            calculate_current_ratio(zero_liab_input)
        with self.assertRaises(ZeroDivisionFinancialError):
            calculate_quick_ratio(zero_liab_input)

    def test_zero_equity_raises_division_by_zero(self) -> None:
        """Verify zero equity raises ZeroDivisionFinancialError in Debt/Equity and DuPont."""
        zero_equity_input = FinancialStatementInput(
            current_assets=Decimal("100"),
            current_liabilities=Decimal("50"),
            cash_and_equivalents=Decimal("10"),
            marketable_securities=Decimal("10"),
            receivables=Decimal("10"),
            total_debt=Decimal("50"),
            total_shareholders_equity=Decimal("0"),
            total_assets=Decimal("200"),
            revenue=Decimal("500"),
            net_income=Decimal("50"),
        )
        with self.assertRaises(ZeroDivisionFinancialError):
            calculate_debt_to_equity(zero_equity_input)
        with self.assertRaises(ZeroDivisionFinancialError):
            calculate_dupont_roe(zero_equity_input)

    def test_zero_revenue_and_assets_in_dupont(self) -> None:
        """Verify zero revenue/assets handled gracefully with expected exceptions in DuPont."""
        zero_rev_input = FinancialStatementInput(
            current_assets=Decimal("100"),
            current_liabilities=Decimal("50"),
            cash_and_equivalents=Decimal("10"),
            marketable_securities=Decimal("10"),
            receivables=Decimal("10"),
            total_debt=Decimal("50"),
            total_shareholders_equity=Decimal("100"),
            total_assets=Decimal("200"),
            revenue=Decimal("0"),
            net_income=Decimal("50"),
        )
        with self.assertRaises(ZeroDivisionFinancialError):
            calculate_dupont_roe(zero_rev_input)

    def test_negative_net_income_handling(self) -> None:
        """Verify negative net income (net loss) produces correct negative ROE and NPM."""
        loss_input = FinancialStatementInput(
            current_assets=Decimal("1000"),
            current_liabilities=Decimal("500"),
            cash_and_equivalents=Decimal("200"),
            marketable_securities=Decimal("100"),
            receivables=Decimal("100"),
            total_debt=Decimal("300"),
            total_shareholders_equity=Decimal("1000"),
            total_assets=Decimal("2000"),
            revenue=Decimal("4000"),
            net_income=Decimal("-500"),
        )
        dupont = calculate_dupont_roe(loss_input)
        self.assertEqual(dupont.net_profit_margin, Decimal("-0.125"))
        self.assertEqual(dupont.roe, Decimal("-0.25"))

    def test_negative_equity_distressed_firm(self) -> None:
        """Verify negative equity (accumulated deficit > capital) produces negative Debt-to-Equity."""
        distressed_input = FinancialStatementInput(
            current_assets=Decimal("500"),
            current_liabilities=Decimal("1000"),
            cash_and_equivalents=Decimal("50"),
            marketable_securities=Decimal("0"),
            receivables=Decimal("50"),
            total_debt=Decimal("2000"),
            total_shareholders_equity=Decimal("-500"),
            total_assets=Decimal("1500"),
            revenue=Decimal("1000"),
            net_income=Decimal("-200"),
        )
        de = calculate_debt_to_equity(distressed_input)
        self.assertEqual(de, Decimal("-4.0"))


class TestCreditScoringEngine(unittest.TestCase):
    """Unit tests for `corpfin.credit_scoring.evaluate_credit_risk` institutional threshold engine."""

    def test_tier_1_perfect_score(self) -> None:
        """Verify maximum score (100.0) yields Tier 1 (Low Risk)."""
        score, tier = evaluate_credit_risk(
            current_ratio=Decimal("2.0"),    # >= 1.5 -> 25.0 pts
            quick_ratio=Decimal("1.2"),      # >= 1.0 -> 20.0 pts
            debt_to_equity=Decimal("0.8"),   # <= 1.5 -> 30.0 pts
            roe=Decimal("0.20"),             # >= 0.15 -> 25.0 pts
        )
        self.assertEqual(score, 100.0)
        self.assertEqual(tier, "Tier 1 (Low Risk)")

    def test_tier_2_moderate_score(self) -> None:
        """Verify mid-range score yields Tier 2 (Moderate Risk)."""
        # Score calculation: 25.0 + 10.0 + 15.0 + 25.0 = 75.0
        score, tier = evaluate_credit_risk(
            current_ratio=Decimal("1.5"),    # >= 1.5 -> 25.0 pts
            quick_ratio=Decimal("0.8"),      # >= 0.8 -> 10.0 pts
            debt_to_equity=Decimal("2.0"),   # <= 2.5 -> 15.0 pts
            roe=Decimal("0.15"),             # >= 0.15 -> 25.0 pts
        )
        self.assertEqual(score, 75.0)
        self.assertEqual(tier, "Tier 2 (Moderate Risk)")

    def test_tier_3_high_risk_score(self) -> None:
        """Verify lower score yields Tier 3 (High Risk)."""
        # Score calculation: 12.5 + 10.0 + 15.0 + 12.5 = 50.0
        score, tier = evaluate_credit_risk(
            current_ratio=Decimal("1.1"),    # >= 1.0 -> 12.5 pts
            quick_ratio=Decimal("0.9"),      # >= 0.8 -> 10.0 pts
            debt_to_equity=Decimal("2.2"),   # <= 2.5 -> 15.0 pts
            roe=Decimal("0.10"),             # >= 0.08 -> 12.5 pts
        )
        self.assertEqual(score, 50.0)
        self.assertEqual(tier, "Tier 3 (High Risk)")

    def test_tier_4_distressed_score(self) -> None:
        """Verify failing all thresholds yields score 0.0 and Tier 4 (Distressed)."""
        score, tier = evaluate_credit_risk(
            current_ratio=Decimal("0.5"),    # < 1.0 -> 0 pts
            quick_ratio=Decimal("0.3"),      # < 0.8 -> 0 pts
            debt_to_equity=Decimal("4.0"),   # > 2.5 -> 0 pts
            roe=Decimal("0.02"),             # < 0.08 -> 0 pts
        )
        self.assertEqual(score, 0.0)
        self.assertEqual(tier, "Tier 4 (Distressed)")

    def test_boundary_conditions_exact_thresholds(self) -> None:
        """Verify exact boundary values trigger upper tier allocations."""
        # Boundaries: CR=1.0 (12.5), QR=1.0 (20.0), D/E=1.5 (30.0), ROE=0.08 (12.5) -> Total: 75.0
        score, tier = evaluate_credit_risk(
            current_ratio=Decimal("1.0"),
            quick_ratio=Decimal("1.0"),
            debt_to_equity=Decimal("1.5"),
            roe=Decimal("0.08"),
        )
        self.assertEqual(score, 75.0)
        self.assertEqual(tier, "Tier 2 (Moderate Risk)")

    def test_boundary_conditions_just_below_thresholds(self) -> None:
        """Verify values slightly below thresholds trigger lower point allocations."""
        # Boundaries: CR=1.4999 (12.5), QR=0.7999 (0.0), D/E=1.5001 (15.0), ROE=0.0799 (0.0) -> Total: 27.5
        score, tier = evaluate_credit_risk(
            current_ratio=Decimal("1.4999"),
            quick_ratio=Decimal("0.7999"),
            debt_to_equity=Decimal("1.5001"),
            roe=Decimal("0.0799"),
        )
        self.assertEqual(score, 27.5)
        self.assertEqual(tier, "Tier 4 (Distressed)")


class TestFinancialAnalysisIntegration(unittest.TestCase):
    """Integration test suite executing full pipeline analytics."""

    def test_analyze_financials_full_pipeline(self) -> None:
        """Verify standard firm input produces complete, expected MetricResults dataclass."""
        data = FinancialStatementInput(
            current_assets=Decimal("1500000.00"),
            current_liabilities=Decimal("800000.00"),
            cash_and_equivalents=Decimal("300000.00"),
            marketable_securities=Decimal("200000.00"),
            receivables=Decimal("400000.00"),
            total_debt=Decimal("1200000.00"),
            total_shareholders_equity=Decimal("1000000.00"),
            total_assets=Decimal("2500000.00"),
            revenue=Decimal("5000000.00"),
            net_income=Decimal("375000.00"),
        )
        
        results = analyze_financials(data)
        
        self.assertIsInstance(results, MetricResults)
        self.assertEqual(results.current_ratio, Decimal("1.875"))
        self.assertEqual(results.quick_ratio, Decimal("1.125"))
        self.assertEqual(results.debt_to_equity, Decimal("1.2"))
        self.assertEqual(results.dupont.roe, Decimal("0.375"))
        self.assertEqual(results.credit_score, 100.0)
        self.assertEqual(results.risk_tier, "Tier 1 (Low Risk)")

    def test_metric_results_immutability(self) -> None:
        """Verify MetricResults object immutability (frozen dataclass enforcement)."""
        data = FinancialStatementInput(
            current_assets=Decimal("1000"),
            current_liabilities=Decimal("500"),
            cash_and_equivalents=Decimal("100"),
            marketable_securities=Decimal("100"),
            receivables=Decimal("100"),
            total_debt=Decimal("500"),
            total_shareholders_equity=Decimal("500"),
            total_assets=Decimal("1000"),
            revenue=Decimal("2000"),
            net_income=Decimal("200"),
        )
        results = analyze_financials(data)
        
        with self.assertRaises(AttributeError):
            results.credit_score = 50.0  # type: ignore


if __name__ == "__main__":
    unittest.main()
```