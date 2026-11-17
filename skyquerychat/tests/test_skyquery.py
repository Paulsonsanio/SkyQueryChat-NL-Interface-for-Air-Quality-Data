"""Run:  python -m unittest discover -s tests -v     (no pytest or API key needed)"""
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skyquery import engine, gazetteer, verifier
from skyquery.agent import SkyQueryAgent
from skyquery.planner import LLMPlanner, PlannerError, RulePlanner
from skyquery.schema import PlanError, QueryPlan, UserFacingError
from skyquery.store import GridStore, ensure_data

STORE = GridStore(ensure_data())
CTX = {"first_date": STORE.first_date.isoformat(), "last_date": STORE.last_date.isoformat()}


class FakeLLM(LLMPlanner):
    """Scripted LLM so the LLM code path is tested without network or keys."""
    def __init__(self, outputs):
        super().__init__("none")
        self.provider, self.model, self.outputs, self.calls = "fake", "m", list(outputs), []

    def _call(self, system, user):
        self.calls.append(user)
        out = self.outputs.pop(0)
        if isinstance(out, Exception):
            raise out
        return out


class TestGazetteer(unittest.TestCase):
    def test_aliases(self):
        self.assertEqual(gazetteer.find_in_text("New Delhi vs Bombay"), ["Delhi", "Mumbai"])
        self.assertEqual(gazetteer.find_in_text("air quality in punjab"), ["Punjab"])
        self.assertEqual(gazetteer.find_in_text("NO2 in Itanagar and Panaji"), ["Itanagar", "Panaji"])

    def test_indian_states_uts_and_major_cities_fit_india_grid(self):
        self.assertEqual(len(gazetteer.INDIAN_STATES_AND_UTS), 36)
        self.assertGreaterEqual(len(gazetteer.INDIAN_CITY_COORDINATES), 150)
        for name in gazetteer.INDIAN_STATES_AND_UTS:
            self.assertIn(name, gazetteer.CITIES, name)
            lat, lon = gazetteer.CITIES[name]
            self.assertTrue(6 <= lat <= 38 and 68 <= lon <= 98, name)
            self.assertTrue(STORE.covers(lat, lon), name)
        for name in gazetteer.INDIAN_CITY_COORDINATES:
            lat, lon = gazetteer.CITIES[name]
            self.assertTrue(6 <= lat <= 38 and 68 <= lon <= 98, name)
            self.assertTrue(STORE.covers(lat, lon), name)


class TestRealDataGrid(unittest.TestCase):
    def test_omi_reader_crops_cloud_screened_field_and_masks_fill(self):
        import tempfile
        import h5py
        import numpy as np
        from scripts.fetch_real_data import FIELD, _crop, _read_grid

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "omi.he5"
            fill = -1.2676506002282294e30
            data = np.full((720, 1440), fill, dtype=np.float32)
            data[245, 1028] = 2.5e15
            with h5py.File(path, "w") as file:
                group_path, field_name = FIELD.rsplit("/", 1)
                field = file.require_group(group_path).create_dataset(field_name, data=data)
                field.attrs["_FillValue"] = fill
            lat, lon, values = _read_grid(path)
            lat, lon, cropped = _crop(lat, lon, values)
            self.assertEqual(cropped.shape, (128, 120))
            self.assertAlmostEqual(float(np.nanmax(cropped)), 2.5e15, delta=2.5e9)
            self.assertEqual(int(np.isfinite(cropped).sum()), 1)

    def test_grid_store_reads_requested_time_format_and_counts_valid_cells(self):
        import tempfile
        import numpy as np

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grid.npz"
            np.savez(
                path,
                time=np.array(["2026-07-17", "2026-07-18"]),
                lat=np.array([28.5, 28.75]),
                lon=np.array([77.0, 77.25]),
                no2=np.array([[[1.0, np.nan], [np.nan, np.nan]],
                              [[np.nan, np.nan], [np.nan, 2.0]]]),
                source=np.array("NASA OMI/Aura NO2, 0.25 deg"),
            )
            store = GridStore(path)
            self.assertEqual((store.first_date.isoformat(), store.last_date.isoformat()),
                             ("2026-07-17", "2026-07-18"))
            self.assertEqual(store.valid_cell_count, 2)
            self.assertFalse(store.is_synthetic)

    def test_empty_location_data_is_refused_without_a_number(self):
        import tempfile
        import numpy as np

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "empty.npz"
            np.savez(
                path,
                time=np.array(["2026-07-17", "2026-07-18"]),
                lat=np.array([28.5, 28.75]),
                lon=np.array([77.0, 77.25]),
                no2=np.full((2, 2, 2), np.nan),
                source=np.array("NASA OMI/Aura NO2, 0.25 deg"),
            )
            response = SkyQueryAgent(GridStore(path), LLMPlanner("none")).ask("NO2 in Delhi")
            self.assertFalse(response.ok)
            self.assertEqual(response.kind, "no_data")
            self.assertIn("no valid satellite data for this location", response.answer.lower())


class TestSchema(unittest.TestCase):
    def test_rejects_bad_intent(self):
        with self.assertRaises(PlanError):
            QueryPlan.from_dict({"intent": "drop table"})

    def test_rejects_non_dict_and_bad_dates(self):
        with self.assertRaises(PlanError):
            QueryPlan.from_dict("hi")
        with self.assertRaises(PlanError):
            QueryPlan.from_dict({"intent": "current", "start_date": "yesterday-ish"})

    def test_normalises(self):
        p = QueryPlan.from_dict({"intent": "RANK", "pollutant": "Nitrogen Dioxide", "top_n": 999,
                                 "start_date": "2025-09-30", "end_date": "2025-09-01"})
        self.assertEqual((p.intent, p.pollutant, p.top_n), ("rank", "no2", 20))
        self.assertEqual((p.start_date, p.end_date), ("2025-09-01", "2025-09-30"))  # swapped


class TestEngineAgainstManualMaths(unittest.TestCase):
    def test_delhi_mean_matches_hand_computation(self):
        import numpy as np
        lat, lon = gazetteer.CITIES["Delhi"]
        ser, _ = STORE.series(lat, lon)
        idx = STORE.slice_dates(date(2025, 9, 1), date(2025, 9, 30))
        expected = float(np.nanmean(ser[idx]))
        plan = QueryPlan.from_dict({"intent": "average", "locations": ["Delhi"],
                                    "start_date": "2025-09-01", "end_date": "2025-09-30"})
        res = engine.execute(engine.resolve(plan, STORE), STORE)
        self.assertAlmostEqual(res["rows"][0]["mean"], expected, delta=1e-3 * expected)

    def test_verifier_catches_tampering(self):
        plan = QueryPlan.from_dict({"intent": "average", "locations": ["Mumbai"], "last_n_days": 30})
        res = engine.execute(engine.resolve(plan, STORE), STORE)
        self.assertTrue(verifier.verify(res, STORE)["passed"])
        res["rows"][0]["mean"] *= 1.05          # simulate a buggy engine
        self.assertFalse(verifier.verify(res, STORE)["passed"])


class TestAgentOffline(unittest.TestCase):
    def setUp(self):
        self.agent = SkyQueryAgent(STORE, LLMPlanner("none"))

    def test_happy_paths_verified(self):
        for q in ["NO2 in Delhi right now", "Air quality in Punjab",
                  "Compare NO2 in Delhi and Mumbai last month", "Which cities have the highest NO2?",
                  "worst day for NO2 in Bengaluru in September", "average NO2 in Kolkata last week",
                  "How has air pollution in Bengaluru changed over the past month?"]:
            r = self.agent.ask(q)
            self.assertTrue(r.ok, q)
            self.assertTrue(r.verification["passed"], q)
            self.assertIn("DEMO DATA", r.answer)

    def test_refusals(self):
        cases = {"What is the PM2.5 in Delhi?": "unsupported", "air quality in New York": "out_of_coverage",
                 "pollution in Atlantis": "unknown_location", "NO2 in Delhi in 2019-03-01": "bad_period",
                 "hello": "clarify", "": "clarify", "Compare NO2 in Delhi": "clarify",
                 "how accurate are you": "out_of_domain", "NO2": "clarify"}
        for q, kind in cases.items():
            r = self.agent.ask(q)
            self.assertFalse(r.ok, q)
            self.assertEqual(r.kind, kind, q)

    def test_never_crashes_on_garbage(self):
        for q in ["💥" * 50, "'; DROP TABLE users; --", "a" * 5000, "NO2 in " + "Delhi " * 100, "\x00\x01"]:
            r = self.agent.ask(q)
            self.assertIsInstance(r.answer, str)


class TestLLMPathAndFallbacks(unittest.TestCase):
    def test_llm_plan_used(self):
        llm = FakeLLM([{"intent": "average", "locations": ["Bengaluru"], "last_n_days": 14}])
        r = SkyQueryAgent(STORE, llm).ask("how dirty is the air in the garden city")
        self.assertTrue(r.ok)
        self.assertTrue(r.planner_used.startswith("llm:"))
        self.assertTrue(r.verification["passed"])

    def test_malformed_then_repaired(self):
        llm = FakeLLM([{"intent": "nonsense"}, {"intent": "current", "locations": ["Kolkata"]}])
        r = SkyQueryAgent(STORE, llm).ask("NO2 Kolkata")
        self.assertTrue(r.ok)
        self.assertEqual(len(llm.calls), 2)
        self.assertIn("rejected", llm.calls[1])        # error was fed back to the model

    def test_llm_down_falls_back_to_rules(self):
        llm = FakeLLM([ConnectionError("network down"), TimeoutError("network still down")])
        r = SkyQueryAgent(STORE, llm).ask("NO2 in Delhi right now")
        self.assertTrue(r.ok)
        self.assertEqual(r.planner_used, "rules")
        self.assertEqual(len(llm.calls), 2)
        self.assertTrue(any(t["step"] == "fallback" for t in r.trace))

    def test_llm_cannot_inject_numbers_or_unknown_fields(self):
        llm = FakeLLM([{"intent": "current", "locations": ["Delhi"], "answer": "NO2 is 0", "value": 0}])
        r = SkyQueryAgent(STORE, llm).ask("anything")
        self.assertNotIn("is 0", r.answer)

    def test_llm_hallucinated_city_with_coords_outside_grid(self):
        llm = FakeLLM([{"intent": "current", "locations": [{"name": "NewYork-ish", "lat": 40.7, "lon": -74.0}]}])
        r = SkyQueryAgent(STORE, llm).ask("New York air")
        self.assertEqual(r.kind, "out_of_coverage")


if __name__ == "__main__":
    unittest.main()
