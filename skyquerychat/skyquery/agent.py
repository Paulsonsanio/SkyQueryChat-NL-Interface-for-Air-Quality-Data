"""The agent: understand -> plan -> validate -> query raw data -> verify -> answer.

Fail-safe design
  * LLM unavailable / errors / returns junk  -> one repair attempt, then deterministic RulePlanner.
  * Anything the data can't support (unknown city, outside coverage, other pollutant, no cloud-free
    day) -> a clear message, never a made-up number.
  * The final answer text is built from engine results by templates; the LLM never writes numbers.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

from . import config, engine, verifier
from .engine import level_label
from .planner import LLMPlanner, PlannerError, RulePlanner
from .schema import QueryPlan, UserFacingError
from .store import DataError, GridStore, ensure_data

S = config.UNIT_SCALE


def fmt(v: float | None) -> str:
    return "n/a" if v is None else f"{v / S:.2f} × 10¹⁵ {config.UNIT}"


def fnum(v: float | None) -> str:
    return "n/a" if v is None else f"{v / S:.2f}"


@dataclass
class Response:
    question: str
    answer: str
    ok: bool
    kind: str = "answer"                 # answer | clarify | unsupported | unknown_location | ...
    plan: dict | None = None
    result: dict | None = None
    verification: dict | None = None
    planner_used: str = ""
    trace: list[dict] = field(default_factory=list)


class SkyQueryAgent:
    def __init__(self, store: GridStore | None = None, llm: LLMPlanner | None = None,
                 verify: bool = True):
        if store is None:
            store = GridStore(ensure_data())
        self.store = store
        self.llm = llm if llm is not None else LLMPlanner()
        self.rules = RulePlanner()
        self.verify = verify

    # ------------------------------------------------------------------ public
    def ask(self, question: str) -> Response:
        trace: list[dict] = []
        used = ""
        q = (question or "").strip()
        if not q:
            return Response(question, "Ask me something like “What is the NO₂ level in Delhi?”", False, "clarify")
        if len(q) > config.MAX_QUESTION_CHARS:
            q = q[: config.MAX_QUESTION_CHARS]
            trace.append({"step": "sanitize", "detail": f"question truncated to {config.MAX_QUESTION_CHARS} chars"})
        try:
            plan, used = self._plan(q, trace)
            if plan.intent == "out_of_domain":
                return Response(
                    question,
                    "I answer questions about satellite tropospheric NO₂ observations. "
                    "I don't estimate general chatbot accuracy; the app reports the data source, "
                    "date range, and verification checks for each supported query.",
                    False,
                    "out_of_domain",
                    plan.to_dict(),
                    planner_used=used,
                    trace=trace,
                )
            resolved = engine.resolve(plan, self.store)
            trace.append({"step": "resolve", "detail": f"{len(resolved.locations)} location(s), "
                                                       f"{resolved.start} → {resolved.end}"})
            result = engine.execute(resolved, self.store)
            trace.append({"step": "query", "detail": f"{sum(r['n_valid'] for r in result['rows'])} valid "
                                                     f"city-days read from raw grid"})
            ver = None
            if self.verify:
                ver = verifier.verify(result, self.store)
                trace.append({"step": "verify", "detail": f"{len(ver['checks'])} independent checks, "
                                                          f"passed={ver['passed']}"})
            answer = compose(result, ver)
            return Response(question, answer, True, "answer", plan.to_dict(), result, ver, used, trace)
        except UserFacingError as e:
            trace.append({"step": "refuse", "detail": f"{e.kind}"})
            return Response(question, e.message, False, e.kind, None, None, None, used, trace)
        except DataError as e:
            return Response(question, f"Data problem: {e}", False, "data_error", trace=trace)
        except Exception as e:  # last-resort guard: the UI must never crash
            trace.append({"step": "error", "detail": f"{type(e).__name__}: {e}"})
            return Response(question, "Sorry, something went wrong while answering that. "
                            "Try rephrasing (e.g. “NO₂ trend in Chicago over the last 30 days”).",
                            False, "internal_error", trace=trace)

    # ------------------------------------------------------------------ planning with fallbacks
    def _plan(self, q: str, trace: list[dict]) -> tuple[QueryPlan, str]:
        ctx = {"first_date": self.store.first_date.isoformat(), "last_date": self.store.last_date.isoformat()}
        if self.llm.available:
            feedback = None
            for attempt in (1, 2):
                try:
                    plan = self.llm.plan(q, ctx, feedback)
                    if plan.intent != "out_of_domain":
                        engine.resolve(plan, self.store)  # dry-run: surfaces fixable problems
                    trace.append({"step": "plan", "detail": f"{self.llm.name} (attempt {attempt})"})
                    return plan, self.llm.name
                except UserFacingError as e:
                    if e.kind in ("unsupported", "out_of_coverage", "bad_period", "no_data") or attempt == 2:
                        # legitimate outcome - let the real run raise it with the same message
                        trace.append({"step": "plan", "detail": f"{self.llm.name} (attempt {attempt}), "
                                                                f"refusal={e.kind}"})
                        return plan, self.llm.name
                    feedback = e.message
                except PlannerError as e:
                    trace.append({"step": "plan_failed", "detail": f"{self.llm.name}: {e}"})
                    feedback = str(e) if "invalid plan" in str(e) else None
            trace.append({"step": "fallback", "detail": "offline planner used after Groq failure"})
        plan = self.rules.plan(q, ctx)
        trace.append({"step": "plan", "detail": "rules"})
        return plan, "rules"


# ---------------------------------------------------------------------- answer composition
def _span(res: dict) -> str:
    s, e = res["start"], res["end"]
    return s if s == e else f"{s} to {e}"


def _coverage(row: dict) -> str:
    return f"{row['n_valid']} of {row['n_total']} days had usable cloud-free data"


def compose(res: dict, ver: dict | None) -> str:
    intent, rows = res["intent"], res["rows"]
    lines: list[str] = []

    if intent == "current":
        for r in rows:
            if r["latest_value"] is None:
                lines.append(f"**{r['location']}**: no valid satellite data for this location between "
                             f"{_span(res)}. Try a longer period.")
                continue
            v = r["latest_value"]
            single = res["start"] == res["end"]
            note = "" if single or r["latest_date"] == res["end"] else " (the latest cloud-free day)"
            s = (f"**{r['location']}**: tropospheric NO₂ was **{fmt(v)}** on {r['latest_date']}{note} — "
                 f"{level_label(v)}.")
            cm = r.get("context_mean")
            if cm:
                diff = (v - cm) / cm * 100
                s += (f" That is {abs(diff):.0f}% {'above' if diff >= 0 else 'below'} its 30-day mean "
                      f"of {fnum(cm)} × 10¹⁵.")
            lines.append(s)

    elif intent == "average":
        for r in rows:
            if r["mean"] is None:
                lines.append(f"**{r['location']}**: no valid satellite data for this location in {_span(res)}.")
            else:
                lines.append(f"**{r['location']}**: average NO₂ over {_span(res)} was **{fmt(r['mean'])}** "
                             f"— {level_label(r['mean'])} ({_coverage(r)}; range {fnum(r['min'])}–{fnum(r['max'])} × 10¹⁵).")

    elif intent == "peak":
        for r in rows:
            if r["peak_value"] is None:
                lines.append(f"**{r['location']}**: no valid satellite data for this location in {_span(res)}.")
            else:
                lines.append(f"**{r['location']}**: highest NO₂ in {_span(res)} was **{fmt(r['peak_value'])}** "
                             f"on {r['peak_date']}; lowest was {fmt(r['low_value'])} on {r['low_date']} "
                             f"({_coverage(r)}).")

    elif intent == "trend":
        for r in rows:
            if r["n_valid"] == 0:
                lines.append(f"**{r['location']}**: no valid satellite data for this location in {_span(res)}.")
                continue
            if r["direction"] in ("insufficient data", "no data") or r["change_pct"] is None:
                lines.append(f"**{r['location']}**: not enough cloud-free days in {_span(res)} to judge a trend "
                             f"({_coverage(r)}; need at least {config.MIN_TREND_POINTS}).")
                continue
            word = {"increasing": "rose", "decreasing": "fell", "roughly flat": "stayed roughly flat"}[r["direction"]]
            amt = "" if r["direction"] == "roughly flat" else f" by about {abs(r['change_pct']):.0f}%"
            lines.append(f"**{r['location']}**: NO₂ {word}{amt} over {_span(res)} "
                         f"(linear fit, R² = {r['r2']:.2f}; mean {fnum(r['mean'])} × 10¹⁵; {_coverage(r)}). "
                         + ("" if r["r2"] >= 0.2 else "The fit is weak, so day-to-day weather noise dominates."))

    elif intent == "compare":
        rk = res["ranking"]
        by = {r["location"]: r for r in rows}
        for name in rk:
            r = by[name]
            lines.append(f"- **{name}**: {fmt(r['mean'])} ({_coverage(r)})")
        if len(rk) >= 2:
            a, b = by[rk[0]], by[rk[-1]]
            ratio = a["mean"] / b["mean"] if b["mean"] else float("inf")
            hi = "higher" if len(rk) == 2 else "highest"
            lines.insert(0, f"Average NO₂ over {_span(res)}: **{rk[0]}** is {hi}, about {ratio:.1f}× "
                            f"the level in **{rk[-1]}**.")
        missing = [r["location"] for r in rows if r["mean"] is None]
        if missing:
            lines.append(f"No valid satellite data for this location: {', '.join(missing)}.")

    elif intent == "rank":
        word = "highest" if res["order"] == "highest" else "lowest"
        by = {r["location"]: r for r in rows}
        lines.append(f"Cities with the {word} average NO₂ over {_span(res)} "
                     f"(among {len(rows)} cities in the loaded data):")
        for i, name in enumerate(res["ranking"], 1):
            lines.append(f"{i}. **{name}** — {fmt(by[name]['mean'])}")

    footer: list[str] = list(res.get("notes", []))
    footer.append(f"Area average within {res['radius_km']:.0f} km of the city centre; units: {config.UNIT}.")
    if ver is not None:
        n = len(ver["checks"])
        footer.append(("✅ Verified: " if ver["passed"] else "⚠️ Verification FAILED: ")
                      + f"{n} figures independently recomputed from the raw grid"
                      + ("." if ver["passed"] else " — treat numbers with caution."))
    if res.get("synthetic"):
        footer.append("⚠️ DEMO DATA: values come from a synthetic India-region grid, not real measurements.")
    else:
        footer.append(f"Source: {res['source']}.")
    return "\n".join(lines) + "\n\n" + "\n".join(f"_{f}_" for f in footer)
