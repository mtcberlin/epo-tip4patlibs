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
EXAMPLE_PATH = Path(__file__).resolve().parent / "worked_example.json"

HORIZON_YEARS = 10
SCORE_MIN, SCORE_MAX = 1, 5

#: How an answer came about. The whole point of module 8 is that these differ.
PROVENANCE = ("measured", "informed", "judgement")

#: The eleven questions PATSTAT can say something about — and what notebook 2 will source
#: for each. Everything not listed here is expert judgement, and the report says so.
#:
#: ``strength`` is deliberately not a score. *strong* means the answer is a matter of
#: record and a query decides it; *good* means the query yields a genuine new insight but
#: a person still picks the level; *proxy* means the number correlates with the question
#: without answering it (claim count is not claim breadth, citations are attention rather
#: than superiority) and must be labelled as such wherever it is shown; *context* informs
#: the answer without narrowing it.
#:
#: Settled on TIP, 2026-08-15 (see ``9_documentation/results-tipsession.md``): the legal-event
#: tables **are** present and populated, so A7 moved off *open* (to *good* — a query gives the
#: opposition rate, but turning a rate into "customary" is still a person's call) and A1/A3
#: gained the in-force half of their answer. Two traps live in that data — ``tls803.event_impact`` is NULL for all
#: 4,332 codes, and the lapsed state sits in ``tls231.lapse_country``, not ``event_text``.
PATSTAT_CANDIDATES: dict[str, dict[str, str]] = {
    "A1": {"strength": "strong",
           "sources": "tls201_appln.granted ('Y'/'N') + publication kind codes, plus the "
                      "opposition outcome from tls231 (26N none / 26 filed / 27W revoked)"},
    "A3": {"strength": "strong",
           "sources": "earliest filing date + 20 years for the nominal term, and tls231 PGFP "
                      "renewal payments (fee_renewal_year) for how far fees are actually paid"},
    "A5": {"strength": "strong",
           "sources": "designated_states at grant vs the states still paid for - tls231 "
                      "lapse_country for lapses, PGFP fee_country for what is still in force "
                      "(which markets are the *relevant* ones stays judgement)"},
    "E1": {"strength": "good",
           "sources": "this family's jurisdictions against the applicant's historical footprint"},
    "E2": {"strength": "good",
           "sources": "jurisdictions in this family that the applicant has never filed in before"},
    "E7": {"strength": "good",
           "sources": "share of the applicant's own families in the same IPC subclass"},
    "A4": {"strength": "proxy",
           "sources": "tls211_pat_publn.publn_claims - take it from the B1 (100% covered, mean "
                      "11.5 for granted EP), never the A1 (51%, and those are the as-filed "
                      "claims). WO has 0% coverage. Breadth is not count, so label it"},
    "B1": {"strength": "proxy",
           "sources": "forward citations received - attention, not uniqueness"},
    "B2": {"strength": "proxy",
           "sources": "forward citations received - attention, not technical superiority"},
    "C4": {"strength": "context",
           "sources": "size and composition of the IPC neighbourhood - context, not an answer"},
    "A7": {"strength": "good",
           "sources": "opposition frequency from tls231: the 26N/26 pair gives both halves of "
                      "the fraction (EP baseline ~4.5%), and 27O/27A/27W give the outcome"},
}

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


def answers_from_scores(
    scores: dict[str, int],
    provenance: str = "judgement",
    promise_patstat: bool = True,
) -> dict[str, Answer]:
    """Turn forty bare scores into forty :class:`Answer` objects.

    ``promise_patstat`` fills the ``evidence`` field of the questions listed in
    :data:`PATSTAT_CANDIDATES` with what notebook 2 *will* source for them. The text
    deliberately opens with ``-> notebook 2`` so it can never be misread as something
    that was measured — the provenance stays ``judgement`` until a query actually runs.
    """
    out = {}
    for qid, score in scores.items():
        candidate = PATSTAT_CANDIDATES.get(qid)
        evidence = ""
        if promise_patstat and candidate and provenance == "judgement":
            evidence = f"-> notebook 2 ({candidate['strength']}): {candidate['sources']}"
        out[qid] = Answer(score, provenance=provenance, evidence=evidence)
    return out


def load_worked_example(path: Path | str = EXAMPLE_PATH) -> dict:
    """The module's worked example — patent, company figures and forty scores.

    It lives in one file so notebooks 3 and 4 cannot drift apart, and so decision **V5**
    (swap in a real family from module 6's corpus) is an edit to that file alone.

    Returns ``patent`` · ``financials`` · ``financials_note`` · ``scores`` · ``answers`` ·
    ``known_facts``.

    Two of those need a word. ``financials_note`` must be shown wherever the figures are —
    PATSTAT holds no financial data, so they are illustrative and are **not** the real
    applicant's accounts. ``known_facts`` is what the TIP session established about the
    patent; notebook 2 re-derives every one of them from PATSTAT rather than reading them
    here, and it exists so the other notebooks can describe the patent before notebook 2
    has been run.

    The ``scores`` are the adviser's **first pass**, deliberately left uncorrected. The
    difference between them and what notebook 2 measures is the module's argument.
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    scores = raw["scores"]
    return {
        "patent": raw["patent"],
        "financials": Financials(**raw["financials"]),
        "financials_note": raw.get("financials_note", ""),
        "scores": scores,
        "answers": answers_from_scores(scores),
        "known_facts": {k: v for k, v in raw.get("known_facts", {}).items()
                        if not k.startswith("_")},
    }


EVIDENCE_PATH = (Path(__file__).resolve().parent
                 / "2_evidence_from_patstat_output" / "evidence_answers.json")


def load_answers(
    evidence_path: Path | str = EVIDENCE_PATH,
    example_path: Path | str = EXAMPLE_PATH,
) -> tuple[dict[str, Answer], str]:
    """The best answer set available, and a label saying which one it is.

    Notebook 2 writes ``evidence_answers.json`` when it runs on TIP: the same forty
    questions, but with ``measured`` / ``informed`` provenance and a real PATSTAT fact
    wherever a query decided or narrowed the score. If that file is there, it wins.

    If it is not — the normal state until notebook 2 has been run — this falls back to the
    adviser's first pass in ``worked_example.json``, and the label says so. Reports must
    print the label: a valuation built on the first pass is a structured opinion, and the
    reader has to be able to tell the two apart at a glance.

    Returns ``(answers, source_label)``.
    """
    path = Path(evidence_path)
    if path.exists():
        raw = json.loads(path.read_text(encoding="utf-8"))
        answers = {
            qid: Answer(a["score"], provenance=a.get("provenance", "judgement"),
                        evidence=a.get("evidence", ""))
            for qid, a in raw["answers"].items()
        }
        return answers, raw.get("label", "measured against PATSTAT by notebook 2")
    return (load_worked_example(example_path)["answers"],
            "the adviser's first pass - notebook 2 has not been run")


def answer_table(answers: dict[str, Answer | int], spec: Spec | None = None) -> list[dict]:
    """One tidy row per question — the table the report is built around.

    It carries the four things a reader of a valuation needs to check at a glance:
    what was asked, what was answered, **whether that answer reached the money**, and
    **where it came from**. The last two are the ones a spreadsheet hides.

    Returned as plain dicts so this module's engine stays free of pandas; wrap it in a
    DataFrame where you need one.
    """
    spec = spec or load_spec()
    rows = []
    for q in spec.questions:
        raw = answers.get(q.id)
        answer = _as_answer(raw) if raw is not None else None
        candidate = PATSTAT_CANDIDATES.get(q.id)
        rows.append({
            "id": q.id,
            "section": q.section,
            "section_title": spec.sections[q.section],
            "question": q.question,
            "factor": q.factor,
            "score": answer.score if answer else None,
            "answer": q.answers[answer.score - 1] if answer else "",
            "provenance": answer.provenance if answer else "unanswered",
            "evidence": answer.evidence if answer else "",
            "carries_money": q.carries_money,
            "oek_param": q.oek_param or "",
            "oek_value": q.value_for(answer.score) if (answer and q.carries_money) else None,
            "is_risk_driver": q.is_risk_driver,
            "is_opportunity_driver": q.is_opportunity_driver,
            "patstat_strength": candidate["strength"] if candidate else "",
            "patstat_sources": candidate["sources"] if candidate else "",
        })
    return rows


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
# Sensitivity: which of the eight levers actually moves the number
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class LeverResponse:
    """What one OEK question does to the NPV across its five possible answers.

    The other seven levers and all seven company figures are held at their current
    values, so each row isolates a single question. That is the honest reading of
    "which answer matters most" — levers do interact, and :attr:`swing` is therefore
    a one-at-a-time result, not a decomposition of the total.
    """

    question_id: str
    param: str
    factor: str
    current_score: int
    current_npv: float
    npv_by_score: tuple[float, ...]  # the NPV at scores 1…5

    @property
    def best_score(self) -> int:
        return max(range(1, SCORE_MAX + 1), key=lambda i: self.npv_by_score[i - 1])

    @property
    def worst_score(self) -> int:
        return min(range(1, SCORE_MAX + 1), key=lambda i: self.npv_by_score[i - 1])

    @property
    def swing(self) -> float:
        """Best minus worst — the full width of this lever."""
        return max(self.npv_by_score) - min(self.npv_by_score)

    @property
    def upside(self) -> float:
        """What is still on the table above today's answer."""
        return max(self.npv_by_score) - self.current_npv

    @property
    def downside(self) -> float:
        """How far the number falls if this answer turns out to be worse (negative)."""
        return min(self.npv_by_score) - self.current_npv

    @property
    def step_up(self) -> float | None:
        """What exactly one better answer is worth. None at the top of the scale."""
        if self.current_score >= SCORE_MAX:
            return None
        return self.npv_by_score[self.current_score] - self.current_npv

    @property
    def step_down(self) -> float | None:
        """What exactly one worse answer costs (negative). None at the bottom."""
        if self.current_score <= SCORE_MIN:
            return None
        return self.npv_by_score[self.current_score - 2] - self.current_npv


def sensitivity(
    fin: Financials, answers: dict[str, Answer | int], spec: Spec | None = None
) -> list[LeverResponse]:
    """Vary each money-carrying answer across all five levels, one at a time.

    Returns one :class:`LeverResponse` per OEK question, widest :attr:`swing` first —
    the computed answer to *"what should we do about it?"*.

    The thirty-two other questions are not in the result because their swing is exactly
    zero. That is not an omission; it is the finding.
    """
    spec = spec or load_spec()
    base_scores = {qid: _as_answer(a).score for qid, a in answers.items()}
    current = npv(fin, oek_from_answers(base_scores, spec))

    rows = []
    for q in spec.oek_questions:
        curve = []
        for score in range(SCORE_MIN, SCORE_MAX + 1):
            trial = dict(base_scores)
            trial[q.id] = score
            curve.append(npv(fin, oek_from_answers(trial, spec)))
        rows.append(LeverResponse(
            question_id=q.id, param=q.oek_param, factor=q.factor,
            current_score=base_scores[q.id], current_npv=current,
            npv_by_score=tuple(curve),
        ))
    return sorted(rows, key=lambda r: r.swing, reverse=True)


# --------------------------------------------------------------------------- #
# Handing a section to the assembler
# --------------------------------------------------------------------------- #
#
# Module 6 merges a pile of charts by an `order` number, because three notebooks scatter
# figures across three folders. A valuation cannot be assembled that way: it has a
# required shape, and `4_assemble_tool` builds that spine itself. What the contract below
# adds is the *optional* part — a notebook that has something extra to say hands over one
# finished section, and the assembler slots it in by `order`.
#
# Spine orders are 100 (verdict), 200 (patent and company), 300 (profile), 400 (data
# reach), 500 (the eight money answers), 600 (cash flow) and 900 (all forty answers).
# Contributions land in the gaps; notebook 3's sensitivity uses 700.

PARTS_DIRNAME = "_report_parts"


def record_section(
    order: int,
    slug: str,
    title: str,
    *,
    fragment_html: str,
    sheets: dict[str, list[dict]] | None = None,
    note: str | None = None,
    output_dir: Path | str = ".",
) -> Path:
    """Hand one finished report section to ``4_assemble_tool``.

    ``fragment_html`` is inline HTML — a Plotly figure rendered with
    ``full_html=False, include_plotlyjs=False``, a table, or both concatenated. It must
    never be an ``<iframe>``: Jupyter serves ``/files/`` under a CSP sandbox that
    disables JavaScript, so an iframed chart renders blank inside TIP.

    ``sheets`` maps a workbook sheet label to plain rows (``list[dict]``), so the numbers
    behind the section end up in the data workbook. Rows are stored as JSON, which keeps
    this module free of both pandas and a parquet engine.

    Re-running the cell overwrites the entry, because the manifest is keyed by ``slug``.
    """
    parts = Path(output_dir) / PARTS_DIRNAME
    parts.mkdir(parents=True, exist_ok=True)

    (parts / f"{slug}.fragment.html").write_text(fragment_html, encoding="utf-8")

    sheet_files: dict[str, str] = {}
    for label, rows in (sheets or {}).items():
        safe = "".join(c if c.isalnum() else "_" for c in label.lower()).strip("_")
        fname = f"{slug}__{safe}.json"
        (parts / fname).write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                                   encoding="utf-8")
        sheet_files[label] = fname

    manifest_path = parts / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    manifest[slug] = {"order": order, "slug": slug, "title": title, "note": note,
                      "fragment": f"{slug}.fragment.html", "sheets": sheet_files}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return parts / f"{slug}.fragment.html"


def load_sections(module_root: Path | str = None) -> list[dict]:
    """Every contributed section under ``module_root``, ordered by ``order``.

    Scans ``*/_report_parts/manifest.json``. Returns an empty list when no notebook has
    contributed yet — which is exactly the state the module ships in until notebook 3 has
    been run, and the assembler must cope with it.
    """
    root = Path(module_root) if module_root else Path(__file__).resolve().parent
    entries = []
    for manifest_path in sorted(root.glob(f"*/{PARTS_DIRNAME}/manifest.json")):
        parts_dir = manifest_path.parent
        for entry in json.loads(manifest_path.read_text(encoding="utf-8")).values():
            entry = dict(entry)
            entry["fragment_path"] = parts_dir / entry["fragment"]
            entry["sheet_paths"] = {k: parts_dir / v for k, v in entry["sheets"].items()}
            entries.append(entry)
    entries.sort(key=lambda e: e["order"])
    return entries


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
