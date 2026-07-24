"""ipscore_kit — the one engine behind module 8.

Everything module 8 computes lives here: the questionnaire, the score profile, the
bridge from scores to economic parameters, and the ten-year discounted cash flow
that ends in a Net Present Value.

The model is **EPO IPScore 3.01**. Its questions, answer options and the eight
score→value tables were extracted once from the EPO workbook into
`ipscore_spec.json` (see `tools/extract_spec_from_excel.py`); nothing here opens
the spreadsheet. The formula chain below is a re-implementation of the workbook's
'Financial calculations' sheet.

Two things about this model are easy to get wrong and are asserted by the
acceptance test in `verify()`:

* **Investments and the investment reduction are one-time events** in the first
  revenue year — not annual charges.
* **Entry and exit years are fractional.** A technology that reaches the market
  after 2.5 years earns half a year of revenue in year 3.

Units: the cash-flow rows follow the workbook and are expressed as *percent of
business turnover*; only the final NPV multiplies back by turnover / 100.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

SPEC_PATH = Path(__file__).resolve().parent / "ipscore_spec.json"

HORIZON_YEARS = 10
SCORE_MIN, SCORE_MAX = 1, 5

#: How an answer came about. The whole point of module 8 is that these differ.
PROVENANCE = ("measured", "informed", "judgement")

#: One palette for every chart in this module, so the notebooks read as one report.
#: The six series hues are a validated categorical set (CVD-safe in this order);
#: the ink and surface values are the chart chrome around them.
PALETTE = {
    "revenue": "#2a78d6",
    "regained": "#eb6834",
    "efficiency": "#1baf7a",
    "investment_reduction": "#eda100",
    "costs": "#4a3aa7",
    "investments": "#e34948",
    "accent": "#be0f05",  # the course's red, for emphasis only
    "ink": "#0b0b0b",
    "ink_secondary": "#52514e",
    "ink_muted": "#898781",
    "grid": "#e1e0d9",
    "axis": "#c3c2b7",
    "surface": "#fcfcfb",
    "inactive": "#d8d7d0",
}

#: Plotly layout shared by every figure in the module.
CHART_LAYOUT = {
    "font": {"family": "system-ui, -apple-system, Segoe UI, sans-serif", "size": 13,
             "color": PALETTE["ink_secondary"]},
    "paper_bgcolor": PALETTE["surface"],
    "plot_bgcolor": PALETTE["surface"],
    "margin": {"l": 70, "r": 30, "t": 70, "b": 60},
    "xaxis": {"gridcolor": PALETTE["grid"], "linecolor": PALETTE["axis"], "zeroline": False},
    "yaxis": {"gridcolor": PALETTE["grid"], "linecolor": PALETTE["axis"], "zeroline": False},
    "legend": {"orientation": "h", "y": -0.18, "x": 0},
    # magic-underscore keys, so a figure can still pass its own `title=`
    "title_font": {"size": 17, "color": PALETTE["ink"]},
    "title_x": 0,
    "title_xanchor": "left",
}


# --------------------------------------------------------------------------- #
# The spec: questions, answers, OEK tables
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Question:
    id: str
    section: str
    question: str
    explanation: str
    factor: str
    answers: tuple[str, ...]
    is_risk_driver: bool
    is_opportunity_driver: bool
    oek_param: str | None = None
    oek_values: tuple[float, ...] | None = None

    @property
    def carries_money(self) -> bool:
        """True for the eight questions that reach the NPV. The other 32 do not."""
        return self.oek_param is not None

    def value_for(self, score: int) -> float:
        if not self.carries_money:
            raise ValueError(f"{self.id} does not feed the cash flow")
        return self.oek_values[_check_score(score) - 1]


@dataclass(frozen=True)
class Spec:
    meta: dict
    sections: dict[str, str]
    questions: tuple[Question, ...]

    def __getitem__(self, qid: str) -> Question:
        return self.by_id[qid]

    @property
    def by_id(self) -> dict[str, Question]:
        return {q.id: q for q in self.questions}

    @property
    def oek_questions(self) -> tuple[Question, ...]:
        return tuple(q for q in self.questions if q.carries_money)

    def of_section(self, key: str) -> tuple[Question, ...]:
        return tuple(q for q in self.questions if q.section == key)

    @property
    def max_points(self) -> int:
        return SCORE_MAX * len(self.questions)


def load_spec(path: Path | str = SPEC_PATH) -> Spec:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    questions = tuple(
        Question(
            id=q["id"],
            section=q["section"],
            question=q["question"],
            explanation=q["explanation"],
            factor=q["factor"],
            answers=tuple(q["answers"]),
            is_risk_driver=q["is_risk_driver"],
            is_opportunity_driver=q["is_opportunity_driver"],
            oek_param=(q["oek"] or {}).get("param"),
            oek_values=tuple((q["oek"] or {}).get("values", ())) or None,
        )
        for q in raw["questions"]
    )
    return Spec(
        meta=raw["meta"],
        sections={s["key"]: s["title"] for s in raw["sections"]},
        questions=questions,
    )


def test_patents(path: Path | str = SPEC_PATH) -> list[dict]:
    """The three patents the EPO workbook ships with, and its own NPV for each."""
    return json.loads(Path(path).read_text(encoding="utf-8"))["test_patents"]


def _check_score(score: int) -> int:
    if score not in range(SCORE_MIN, SCORE_MAX + 1):
        raise ValueError(f"score must be {SCORE_MIN}–{SCORE_MAX}, got {score!r}")
    return score


# --------------------------------------------------------------------------- #
# Answers and the score profile
# --------------------------------------------------------------------------- #

@dataclass
class Answer:
    """One scored question — and where the score came from.

    `provenance` is module 8's addition to the EPO model: *measured* means a
    PATSTAT fact decided it, *informed* means data narrowed it but a person chose,
    *judgement* means nothing but expert opinion stands behind it.
    """

    score: int
    provenance: str = "judgement"
    evidence: str = ""

    def __post_init__(self) -> None:
        _check_score(self.score)
        if self.provenance not in PROVENANCE:
            raise ValueError(f"provenance must be one of {PROVENANCE}, got {self.provenance!r}")


@dataclass
class Profile:
    """The qualitative read-out: points per section, and the risk/opportunity map."""

    section_points: dict[str, int]
    total_points: int
    max_points: int
    risk_by_question: dict[str, float]
    opportunity_by_question: dict[str, float]
    provenance_counts: dict[str, int] = field(default_factory=dict)

    @property
    def average_risk(self) -> float:
        return _mean(self.risk_by_question.values())

    @property
    def average_opportunity(self) -> float:
        return _mean(self.opportunity_by_question.values())


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def profile(answers: dict[str, Answer | int], spec: Spec | None = None) -> Profile:
    """Score profile from a full or partial answer set.

    Risk and opportunity follow the workbook's 'RiskOpportunity Calculation':
    a risk driver contributes ``(5 - score) * -0.25`` (so 0 at the best answer,
    -1 at the worst), an opportunity driver ``(score - 1) * 0.25``. Each average
    runs over the flagged questions only — 21 carry a risk flag, 15 an
    opportunity flag, and some carry both.
    """
    spec = spec or load_spec()
    normalised = {qid: _as_answer(a) for qid, a in answers.items()}
    unknown = set(normalised) - set(spec.by_id)
    if unknown:
        raise KeyError(f"not IPScore questions: {sorted(unknown)}")

    section_points = {key: 0 for key in spec.sections}
    risk, opportunity, prov = {}, {}, {p: 0 for p in PROVENANCE}
    for qid, answer in normalised.items():
        q = spec[qid]
        section_points[q.section] += answer.score
        prov[answer.provenance] += 1
        if q.is_risk_driver:
            risk[qid] = (SCORE_MAX - answer.score) * -0.25
        if q.is_opportunity_driver:
            opportunity[qid] = (answer.score - SCORE_MIN) * 0.25

    return Profile(
        section_points=section_points,
        total_points=sum(section_points.values()),
        max_points=spec.max_points,
        risk_by_question=risk,
        opportunity_by_question=opportunity,
        provenance_counts=prov,
    )


def _as_answer(value: Answer | int) -> Answer:
    return value if isinstance(value, Answer) else Answer(score=int(value))


def oek_from_answers(answers: dict[str, Answer | int], spec: Spec | None = None) -> dict[str, float]:
    """Map the eight money-carrying answers onto their economic parameters.

    Every other answer is ignored here — deliberately. Thirty-two of the forty
    questions never touch the NPV.
    """
    spec = spec or load_spec()
    missing = [q.id for q in spec.oek_questions if q.id not in answers]
    if missing:
        raise KeyError(f"the cash flow needs all 8 OEK answers, missing: {missing}")
    return {
        q.oek_param: q.value_for(_as_answer(answers[q.id]).score) for q in spec.oek_questions
    }


# --------------------------------------------------------------------------- #
# The financial side
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Financials:
    """The seven company figures the model needs, straight from the accounts."""

    turnover: float
    direct_costs: float
    indirect_costs: float
    depreciation: float
    depreciation_period: float
    business_area_share: float  # share of turnover the business area represents, 0–1
    discount_rate: float  # 0–1

    @property
    def cost_share(self) -> float:
        """(direct + indirect) / turnover."""
        return (self.direct_costs + self.indirect_costs) / self.turnover if self.turnover else 0.0

    @property
    def depreciation_share_pct(self) -> float:
        return self.depreciation / self.turnover * 100 if self.turnover else 0.0

    @property
    def investment_index(self) -> float:
        """Depreciation period × depreciation share — the workbook's 'investment index'."""
        return self.depreciation_period * self.depreciation_share_pct / 100


@dataclass(frozen=True)
class CashFlowYear:
    year: int
    active_fraction: float
    revenue: float
    costs: float
    investments: float
    regained_revenue: float
    efficiency: float
    investment_reduction: float
    liquidity: float
    discounted: float


def _active_fraction(year: int, years_to_market: float, life_expectancy: float) -> float:
    """How much of `year` the technology is actually on the market — 0…1.

    Entry and exit years are partial: reaching the market after 2.5 years means
    year 3 counts half. This is the workbook's nested IF, spelled out.
    """
    T, L = years_to_market, life_expectancy
    if year <= T:
        return 0.0
    if year - T < 1:
        return year - T  # entry year, partial
    if year <= T + L:
        return 1.0  # full year on the market
    if year - T - L < 1:
        return 1 - (year - T - L)  # exit year, partial
    return 0.0


def _is_launch_year(year: int, years_to_market: float) -> bool:
    """The single year that carries the one-time investment effects.

    The workbook writes this as ``y = T+1 OR y + (y-T) = T+1`` — which picks the
    year after market entry for a whole T, and the entry year itself for a
    fractional one.
    """
    T = years_to_market
    return math.isclose(year, T + 1) or math.isclose(year + (year - T), T + 1)


def cash_flow(fin: Financials, oek: dict[str, float]) -> list[CashFlowYear]:
    """The ten-year chain, one row per year, in percent of business turnover."""
    T = oek["years_to_market"]
    g = oek["market_growth"]
    L = oek["life_expectancy"]
    et = oek["extra_turnover_share"]
    maintainable = oek["output_maintainable"]
    development_cost = oek["development_cost_share"]
    production_index = oek["production_cost_index"]
    investment_index = oek["investment_index"]

    S = fin.business_area_share
    cost_share = fin.cost_share
    years = range(1, HORIZON_YEARS + 1)

    fraction = {y: _active_fraction(y, T, L) for y in years}
    revenue = {y: fraction[y] * et * (1 + g) ** (y - 1) * S * (1 + g) ** y * 100 for y in years}

    # The one-time investment is sized on the *average* turnover the technology is
    # expected to bring over the depreciation period, not on year one alone.
    within_depreciation = [
        revenue[y] for y in years if y > T and y <= T + 1 + fin.depreciation_period
    ]
    average_revenue = (
        sum(within_depreciation) / fin.depreciation_period if fin.depreciation_period else 0.0
    )

    rows = []
    for y in years:
        launch = _is_launch_year(y, T)
        development = development_cost * S * 100 if y <= T else 0.0
        costs = revenue[y] * production_index * cost_share + development
        investments = average_revenue * fin.investment_index * investment_index if launch else 0.0
        investment_reduction = (
            fin.depreciation_period
            * fin.depreciation_share_pct
            * (1 - investment_index)
            * S
            * (1 + g) ** y
            if launch
            else 0.0
        )
        regained = fraction[y] * (1 - cost_share) * 100 * (1 - maintainable) * S * (1 + g) ** y
        efficiency = fraction[y] * cost_share * 100 * (1 - production_index) * S * (1 + g) ** y
        liquidity = revenue[y] - costs - investments + regained + efficiency + investment_reduction
        rows.append(
            CashFlowYear(
                year=y,
                active_fraction=fraction[y],
                revenue=revenue[y],
                costs=costs,
                investments=investments,
                regained_revenue=regained,
                efficiency=efficiency,
                investment_reduction=investment_reduction,
                liquidity=liquidity,
                discounted=liquidity * fin.turnover / 100 / (1 + fin.discount_rate) ** y,
            )
        )
    return rows


def npv(fin: Financials, oek: dict[str, float]) -> float:
    """Net Present Value of the patented technology, in the accounts' currency."""
    return sum(row.discounted for row in cash_flow(fin, oek))


def npv_from_answers(
    fin: Financials, answers: dict[str, Answer | int], spec: Spec | None = None
) -> float:
    return npv(fin, oek_from_answers(answers, spec))


# --------------------------------------------------------------------------- #
# The acceptance test
# --------------------------------------------------------------------------- #

def verify(path: Path | str = SPEC_PATH, tolerance: float = 1e-6) -> list[dict]:
    """Reproduce the EPO workbook's own NPV for its three test patents.

    This is the gate: until all three match, nothing else this module computes is
    worth reading. Checking against the source of truth rather than against our
    own previous output is the habit that matters here — the same check, applied
    to module 7's engine, once caught a real off-by-one bug.
    """
    results = []
    for patent in test_patents(path):
        computed = npv(Financials(**patent["financials"]), patent["oek"])
        expected = patent["expected_npv"]
        results.append(
            {
                "name": patent["name"],
                "computed": computed,
                "expected": expected,
                "difference": computed - expected,
                "passed": abs(computed - expected) <= tolerance * max(1.0, abs(expected)),
            }
        )
    return results


def main() -> int:
    results = verify()
    for r in results:
        flag = "PASS" if r["passed"] else "FAIL"
        print(
            f"  {r['name']}: computed={r['computed']:15,.4f}  "
            f"expected={r['expected']:15,.4f}  diff={r['difference']:+.2e}  [{flag}]"
        )
    ok = all(r["passed"] for r in results)
    print("\n" + ("All three EPO test patents reproduced." if ok else "ACCEPTANCE TEST FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
