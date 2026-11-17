"""Terminal chat:  python cli.py   (add --no-llm to force the offline rule-based planner)"""
import sys
from skyquery.agent import SkyQueryAgent
from skyquery.planner import LLMPlanner

HELP = """Examples:
  What is the NO2 level in Delhi right now?
  Is NO2 in Mumbai getting better over the last 60 days?
  Compare NO2 in Mumbai and Chennai last month
  Which cities have the highest NO2?
  What was the worst day for NO2 in LA in September?
Commands: :trace (show last steps)  :plan (show last query plan)  :help  :quit"""


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    llm = LLMPlanner("none") if "--no-llm" in sys.argv else LLMPlanner()
    agent = SkyQueryAgent(llm=llm)
    print(f"SkyQueryChat | data: {agent.store.first_date} → {agent.store.last_date} | "
          f"planner: {llm.name if llm.available else 'rules (offline)'} | source: {agent.store.source} | "
          f"valid grid cells: {agent.store.valid_cell_count}")
    if agent.store.is_synthetic:
        print("Demo synthetic data")
    if llm.available and llm.provider == "groq":
        print(f"Groq planner startup self-test: {llm.startup_self_test()}")
    print(HELP)
    last = None
    while True:
        try:
            q = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q in (":quit", ":q", "exit", "quit"):
            break
        if q == ":help":
            print(HELP); continue
        if q == ":trace" and last:
            for t in last.trace: print(" -", t["step"], "|", t["detail"])
            continue
        if q == ":plan" and last:
            print(last.plan); continue
        last = agent.ask(q)
        if last.planner_used == "rules":
            print("(offline planner used)")
        print("\n" + last.answer)


if __name__ == "__main__":
    main()
