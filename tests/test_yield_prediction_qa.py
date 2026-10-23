"""Comprehensive QA Test Suite for Stage 2: Yield Prediction (CropPulse).

Tests:
1. All 22 recommended crops passed by common names and verified against CropManager.resolve_for_yield().
2. Standalone crops from the 124 dataset classes (Wheat, Barley, Bajra, Groundnut, Sugarcane, Turmeric).
3. Diverse states (Andhra Pradesh, Punjab, Maharashtra, Uttar Pradesh, Karnataka, Tamil Nadu, Gujarat)
   and seasons (Kharif, Rabi, Summer, Whole Year).
4. Multiple land area scales (0.5, 1.0, 5.0, 25.0, 100.0 hectares).
5. Mathematical consistency: total_yield == round(yield_per_hectare * area, 2), both > 0.
6. Boundary and edge cases: negative/zero area, missing fields, unseen/misspelled inputs.
"""

import sys
import json
import unittest
import warnings
from typing import Dict, Any, List

warnings.filterwarnings("ignore")

# Import Flask app and CropManager
from web_app import app
from agri_guide.utils.crop_manager import CropManager, RECOMMENDATION_CROPS


class TestYieldPredictionQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.testing = True
        cls.client = app.test_client()

    def _post_yield(self, payload: Dict[str, Any]):
        return self.client.post(
            "/api/predict-yield",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def _assert_yield_math_consistency(self, result: Dict[str, Any], area: float):
        self.assertIn("yield_per_hectare", result)
        self.assertIn("total_yield", result)
        self.assertIn("area", result)

        y_per_ha = result["yield_per_hectare"]
        total_y = result["total_yield"]
        res_area = result["area"]

        self.assertGreater(y_per_ha, 0, f"yield_per_hectare must be > 0, got {y_per_ha}")
        self.assertGreater(total_y, 0, f"total_yield must be > 0, got {total_y}")
        self.assertAlmostEqual(res_area, area, places=4)

        expected_total = round(y_per_ha * area, 2)
        self.assertEqual(
            total_y,
            expected_total,
            f"Mathematical inconsistency: total_yield ({total_y}) != round(yield_per_hectare * area, 2) ({expected_total})",
        )

    # -------------------------------------------------------------------------
    # Test Suite 1: All 22 Recommendation Crops Mapping & Prediction
    # -------------------------------------------------------------------------
    def test_01_all_22_recommended_crops_resolution_and_prediction(self):
        print("\n" + "=" * 80)
        print("TEST SUITE 1: 22 RECOMMENDED CROPS (COMMON NAMES -> YIELD PREDICTION)")
        print("=" * 80)

        # Expected resolution mappings from RECOMMENDATION_CROPS
        passed_count = 0
        total_count = len(RECOMMENDATION_CROPS)

        table_rows = []
        for common_name, meta in sorted(RECOMMENDATION_CROPS.items()):
            expected_yield_class = meta["yield_class"]
            resolved = CropManager.resolve_for_yield(common_name)
            self.assertEqual(
                resolved,
                expected_yield_class,
                f"CropManager resolution mismatch for '{common_name}': expected '{expected_yield_class}', got '{resolved}'",
            )

            # Test through API endpoint with common name
            area = 2.0
            payload = {
                "state": "Maharashtra",
                "season": "Kharif",
                "crop": common_name,
                "area": area,
            }
            resp = self._post_yield(payload)
            self.assertEqual(
                resp.status_code, 200, f"Failed prediction for crop '{common_name}': {resp.data}"
            )
            data = resp.get_json()
            self.assertTrue(data.get("success"), f"API success was not True: {data}")

            result = data["result"]
            self._assert_yield_math_consistency(result, area)
            passed_count += 1
            table_rows.append(
                f"| {common_name:<14} | {resolved:<18} | {result['yield_per_hectare']:>8.2f} t/ha | {result['total_yield']:>8.2f} t | PASS |"
            )

        print(
            f"| {'Input Crop':<14} | {'Resolved Class':<18} | {'Yield/ha':>13} | {'Total (2ha)':>13} | Status |"
        )
        print("|" + "-" * 16 + "|" + "-" * 20 + "|" + "-" * 15 + "|" + "-" * 15 + "|--------|")
        for row in table_rows:
            print(row)
        print(f"\n>> All {passed_count}/{total_count} recommended crops successfully verified!\n")

    # -------------------------------------------------------------------------
    # Test Suite 2: Standalone Crops from 124 Dataset Classes
    # -------------------------------------------------------------------------
    def test_02_standalone_crops(self):
        print("\n" + "=" * 80)
        print("TEST SUITE 2: STANDALONE CROPS FROM 124 DATASET CLASSES")
        print("=" * 80)

        standalone_crops = [
            ("Wheat", "Punjab", "Rabi", 5.0),
            ("Barley", "Rajasthan", "Rabi", 3.0),
            ("Bajra", "Gujarat", "Kharif", 4.0),
            ("Groundnut", "Andhra Pradesh", "Kharif", 2.5),
            ("Sugarcane", "Uttar Pradesh", "Whole Year", 10.0),
            ("Turmeric", "Tamil Nadu", "Whole Year", 1.5),
        ]

        print(
            f"| {'Crop':<12} | {'State':<16} | {'Season':<12} | {'Area (ha)':>9} | {'Yield/ha':>10} | {'Total':>10} | Status |"
        )
        print("|" + "-" * 14 + "|" + "-" * 18 + "|" + "-" * 14 + "|" + "-" * 11 + "|" + "-" * 12 + "|" + "-" * 12 + "|--------|")

        for crop, state, season, area in standalone_crops:
            payload = {
                "state": state,
                "season": season,
                "crop": crop,
                "area": area,
            }
            resp = self._post_yield(payload)
            self.assertEqual(resp.status_code, 200, f"Failed for standalone crop {crop}: {resp.data}")
            data = resp.get_json()
            self.assertTrue(data.get("success"))
            result = data["result"]
            self._assert_yield_math_consistency(result, area)

            print(
                f"| {crop:<12} | {state:<16} | {season:<12} | {area:>9.1f} | {result['yield_per_hectare']:>8.2f} t | {result['total_yield']:>8.2f} t | PASS |"
            )

    # -------------------------------------------------------------------------
    # Test Suite 3: Diverse Geographic States & Seasons Matrix
    # -------------------------------------------------------------------------
    def test_03_states_and_seasons_matrix(self):
        print("\n" + "=" * 80)
        print("TEST SUITE 3: DIVERSE STATES & SEASONS COMBINATIONS")
        print("=" * 80)

        states = [
            "Andhra Pradesh",
            "Punjab",
            "Maharashtra",
            "Uttar Pradesh",
            "Karnataka",
            "Tamil Nadu",
            "Gujarat",
        ]
        seasons = ["Kharif", "Rabi", "Summer", "Whole Year"]
        test_crop = "Rice"
        area = 4.0

        success_count = 0
        total_combos = len(states) * len(seasons)

        print(f"Testing {total_combos} combinations of States x Seasons for crop: {test_crop} (Area: {area} ha)")
        print(f"| {'State':<18} | {'Season':<12} | {'Yield/ha':>10} | {'Total Yield':>12} | Status |")
        print("|" + "-" * 20 + "|" + "-" * 14 + "|" + "-" * 12 + "|" + "-" * 14 + "|--------|")

        for st in states:
            for sn in seasons:
                payload = {
                    "state": st,
                    "season": sn,
                    "crop": test_crop,
                    "area": area,
                }
                resp = self._post_yield(payload)
                self.assertEqual(
                    resp.status_code, 200, f"Failed state/season combination {st} - {sn}: {resp.data}"
                )
                data = resp.get_json()
                self.assertTrue(data.get("success"))
                result = data["result"]
                self._assert_yield_math_consistency(result, area)
                success_count += 1
                print(
                    f"| {st:<18} | {sn:<12} | {result['yield_per_hectare']:>8.2f} t | {result['total_yield']:>10.2f} t | PASS |"
                )

        self.assertEqual(success_count, total_combos)
        print(f"\n>> All {success_count}/{total_combos} State x Season combinations passed!\n")

    # -------------------------------------------------------------------------
    # Test Suite 4: Multi-Scale Land Area Scaling
    # -------------------------------------------------------------------------
    def test_04_land_area_scaling(self):
        print("\n" + "=" * 80)
        print("TEST SUITE 4: MULTI-SCALE LAND AREA (0.5 to 100.0 HECTARES)")
        print("=" * 80)

        area_scales = [0.5, 1.0, 5.0, 25.0, 100.0]
        test_crops = ["Wheat", "chickpea", "Cotton", "Sugarcane"]

        print(
            f"| {'Crop':<12} | {'Area (ha)':>10} | {'Yield/ha':>10} | {'Total Yield':>14} | {'Math Consistency':>18} |"
        )
        print("|" + "-" * 14 + "|" + "-" * 12 + "|" + "-" * 12 + "|" + "-" * 16 + "|" + "-" * 20 + "|")

        for crop in test_crops:
            for area in area_scales:
                payload = {
                    "state": "Punjab",
                    "season": "Rabi",
                    "crop": crop,
                    "area": area,
                }
                resp = self._post_yield(payload)
                self.assertEqual(resp.status_code, 200)
                data = resp.get_json()
                self.assertTrue(data.get("success"))
                result = data["result"]
                self._assert_yield_math_consistency(result, area)
                print(
                    f"| {crop:<12} | {area:>10.1f} | {result['yield_per_hectare']:>8.2f} t | {result['total_yield']:>12.2f} t | EXACT PASS (100%) |"
                )

    # -------------------------------------------------------------------------
    # Test Suite 5: Boundary & Negative/Edge Cases
    # -------------------------------------------------------------------------
    def test_05_boundary_and_edge_cases(self):
        print("\n" + "=" * 80)
        print("TEST SUITE 5: BOUNDARY AND EDGE CASES VALIDATION")
        print("=" * 80)

        # 5a. Area <= 0
        zero_area_payloads = [
            ({"state": "Punjab", "season": "Rabi", "crop": "Wheat", "area": 0.0}, "Zero Area (0.0)"),
            ({"state": "Punjab", "season": "Rabi", "crop": "Wheat", "area": -1.5}, "Negative Area (-1.5)"),
            ({"state": "Punjab", "season": "Rabi", "crop": "Wheat", "area": -100.0}, "Large Negative Area (-100.0)"),
        ]
        for payload, desc in zero_area_payloads:
            resp = self._post_yield(payload)
            self.assertEqual(
                resp.status_code, 400, f"Expected 400 for {desc}, got {resp.status_code}"
            )
            data = resp.get_json()
            self.assertFalse(data.get("success"))
            self.assertIn("area", data.get("error", "").lower())
            print(f"[EDGE CASE] {desc:<35} -> HTTP 400 Rejected properly: '{data.get('error')}'")

        # 5b. Missing required fields
        missing_field_payloads = [
            ({"season": "Rabi", "crop": "Wheat", "area": 5.0}, "Missing 'state'"),
            ({"state": "Punjab", "crop": "Wheat", "area": 5.0}, "Missing 'season'"),
            ({"state": "Punjab", "season": "Rabi", "area": 5.0}, "Missing 'crop'"),
            ({"state": "", "season": "Rabi", "crop": "Wheat", "area": 5.0}, "Empty 'state' string"),
            ({"state": "Punjab", "season": "", "crop": "Wheat", "area": 5.0}, "Empty 'season' string"),
            ({"state": "Punjab", "season": "Rabi", "crop": "", "area": 5.0}, "Empty 'crop' string"),
            ({}, "Completely empty payload"),
        ]
        for payload, desc in missing_field_payloads:
            resp = self._post_yield(payload)
            self.assertEqual(
                resp.status_code, 400, f"Expected 400 for {desc}, got {resp.status_code}"
            )
            data = resp.get_json()
            self.assertFalse(data.get("success"))
            print(f"[EDGE CASE] {desc:<35} -> HTTP 400 Rejected properly: '{data.get('error')}'")

        # 5c. Invalid types for area
        invalid_type_payload = {"state": "Punjab", "season": "Rabi", "crop": "Wheat", "area": "not_a_number"}
        resp = self._post_yield(invalid_type_payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertFalse(data.get("success"))
        print(f"[EDGE CASE] {'Invalid non-numeric area':<35} -> HTTP 400 Rejected properly: '{data.get('error')}'")

        # 5d. Unseen / misspelled state, season, crop fallback (Graceful handling without 500)
        fallback_payloads = [
            (
                {"state": "AtlantisRepublic", "season": "Rabi", "crop": "Wheat", "area": 5.0},
                "Unseen fictitious State",
            ),
            (
                {"state": "PunnjabMisspelled", "season": "Rabi", "crop": "Wheat", "area": 5.0},
                "Misspelled State name",
            ),
            (
                {"state": "Punjab", "season": "AlienSeason", "crop": "Wheat", "area": 5.0},
                "Unseen Season name",
            ),
            (
                {"state": "Punjab", "season": "Rabi", "crop": "MysticalDragonFruit", "area": 5.0},
                "Unseen Crop name",
            ),
        ]
        for payload, desc in fallback_payloads:
            resp = self._post_yield(payload)
            self.assertEqual(
                resp.status_code, 200, f"Expected 200 graceful fallback for {desc}, got {resp.status_code}"
            )
            data = resp.get_json()
            self.assertTrue(data.get("success"))
            result = data["result"]
            self._assert_yield_math_consistency(result, payload["area"])
            print(
                f"[FALLBACK]  {desc:<35} -> HTTP 200 Handled Gracefully (Yield: {result['yield_per_hectare']} t/ha, Total: {result['total_yield']} t)"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
