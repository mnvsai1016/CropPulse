"""
System QA & Robustness Verification Test Suite for CropPulse.
Tests all endpoints, type conversions, input validations, edge cases, and CropManager resolution.
Runs with Python standard library unittest.
"""

import math
import unittest
from web_app import app, CropManager


class TestSystemQA(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    # =========================================================================
    # 1. CROP RECOMMENDATION ENDPOINT (/api/predict-crop)
    # =========================================================================

    def test_predict_crop_valid(self):
        """Test valid prediction request returns 200 and expected structure."""
        payload = {
            "n": 90,
            "p": 42,
            "k": 43,
            "temperature": 20.8,
            "humidity": 82.0,
            "ph": 6.5,
            "rainfall": 202.9
        }
        response = self.client.post("/api/predict-crop", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("crop", data["result"])
        self.assertIn("confidence", data["result"])
        self.assertIn("advice", data["result"])
        self.assertIsInstance(data["result"]["crop"], str)

    def test_predict_crop_edge_cases_and_invalid(self):
        """Test malformed, missing, NaN, Inf, and out-of-range inputs return 400."""
        # Empty body
        r = self.client.post("/api/predict-crop", data="", content_type="application/json")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.get_json()["success"])

        # Non-dict JSON (list)
        r = self.client.post("/api/predict-crop", json=[1, 2, 3])
        self.assertEqual(r.status_code, 400)

        # Negative nitrogen
        r = self.client.post("/api/predict-crop", json={"n": -10, "p": 50, "k": 50, "temperature": 25, "humidity": 70, "ph": 6.5, "rainfall": 100})
        self.assertEqual(r.status_code, 400)
        self.assertIn(">= 0", r.get_json()["error"])

        # Negative rainfall
        r = self.client.post("/api/predict-crop", json={"n": 50, "p": 50, "k": 50, "temperature": 25, "humidity": 70, "ph": 6.5, "rainfall": -5})
        self.assertEqual(r.status_code, 400)

        # pH out of range (>14)
        r = self.client.post("/api/predict-crop", json={"n": 50, "p": 50, "k": 50, "temperature": 25, "humidity": 70, "ph": 15, "rainfall": 100})
        self.assertEqual(r.status_code, 400)
        self.assertIn("<= 14", r.get_json()["error"])

        # pH out of range (<0)
        r = self.client.post("/api/predict-crop", json={"n": 50, "p": 50, "k": 50, "temperature": 25, "humidity": 70, "ph": -1, "rainfall": 100})
        self.assertEqual(r.status_code, 400)

        # Humidity out of range (>100)
        r = self.client.post("/api/predict-crop", json={"n": 50, "p": 50, "k": 50, "temperature": 25, "humidity": 105, "ph": 6.5, "rainfall": 100})
        self.assertEqual(r.status_code, 400)

        # Non-numeric string
        r = self.client.post("/api/predict-crop", json={"n": "invalid", "p": 50, "k": 50, "temperature": 25, "humidity": 70, "ph": 6.5, "rainfall": 100})
        self.assertEqual(r.status_code, 400)

        # NaN / Inf string
        r = self.client.post("/api/predict-crop", json={"n": "nan", "p": 50, "k": 50, "temperature": 25, "humidity": 70, "ph": 6.5, "rainfall": 100})
        self.assertEqual(r.status_code, 400)
        self.assertIn("finite number", r.get_json()["error"])

        r = self.client.post("/api/predict-crop", json={"n": "inf", "p": 50, "k": 50, "temperature": 25, "humidity": 70, "ph": 6.5, "rainfall": 100})
        self.assertEqual(r.status_code, 400)
        self.assertIn("finite number", r.get_json()["error"])

        # Null values
        r = self.client.post("/api/predict-crop", json={"n": None, "p": 50, "k": 50, "temperature": 25, "humidity": 70, "ph": 6.5, "rainfall": 100})
        self.assertEqual(r.status_code, 400)

    # =========================================================================
    # 2. YIELD PREDICTION ENDPOINT (/api/predict-yield)
    # =========================================================================

    def test_predict_yield_valid(self):
        """Test valid yield prediction returns 200 and expected values."""
        payload = {
            "state": "Andhra Pradesh",
            "season": "Kharif",
            "crop": "Rice",
            "area": 1000.0
        }
        response = self.client.post("/api/predict-yield", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("yield_per_hectare", data["result"])
        self.assertIn("total_yield", data["result"])
        self.assertGreater(data["result"]["yield_per_hectare"], 0)
        self.assertGreater(data["result"]["total_yield"], 0)
        self.assertEqual(data["result"]["area"], 1000.0)

    def test_predict_yield_unseen_and_whitespace_categories(self):
        """Test yield prediction handles trailing space encoder classes and unseen categories gracefully."""
        # Test state with trailing space in encoder (Telangana)
        payload = {
            "state": "Telangana",
            "season": "Kharif",
            "crop": "Rice",
            "area": 50.0
        }
        response = self.client.post("/api/predict-yield", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])

        # Test season with trailing space (all 6 seasons in encoder)
        for season in ["Kharif", "Rabi", "Autumn", "Summer", "Whole Year", "Winter"]:
            p = {"state": "Punjab", "season": season, "crop": "Wheat", "area": 10.0}
            r = self.client.post("/api/predict-yield", json=p)
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.get_json()["success"])

        # Test crop with trailing space (Coconut)
        p = {"state": "Kerala", "season": "Whole Year", "crop": "Coconut", "area": 20.0}
        r = self.client.post("/api/predict-yield", json=p)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["success"])

        # Test unseen state and crop (should resolve safely without 500 error)
        p_unseen = {"state": "Atlantis", "season": "Kharif", "crop": "DragonFruit", "area": 5.0}
        r_unseen = self.client.post("/api/predict-yield", json=p_unseen)
        self.assertEqual(r_unseen.status_code, 200)
        self.assertTrue(r_unseen.get_json()["success"])

    def test_predict_yield_invalid_inputs(self):
        """Test missing fields, zero/negative area, and malformed types return 400."""
        # Missing required state
        r = self.client.post("/api/predict-yield", json={"season": "Kharif", "crop": "Rice", "area": 10})
        self.assertEqual(r.status_code, 400)

        # Area <= 0
        r = self.client.post("/api/predict-yield", json={"state": "Punjab", "season": "Rabi", "crop": "Wheat", "area": 0})
        self.assertEqual(r.status_code, 400)

        r = self.client.post("/api/predict-yield", json={"state": "Punjab", "season": "Rabi", "crop": "Wheat", "area": -10})
        self.assertEqual(r.status_code, 400)

        # Non-numeric area
        r = self.client.post("/api/predict-yield", json={"state": "Punjab", "season": "Rabi", "crop": "Wheat", "area": "invalid"})
        self.assertEqual(r.status_code, 400)

        # NaN area
        r = self.client.post("/api/predict-yield", json={"state": "Punjab", "season": "Rabi", "crop": "Wheat", "area": "nan"})
        self.assertEqual(r.status_code, 400)

    # =========================================================================
    # 3. FERTILIZER PREDICTION ENDPOINT (/api/predict-fertilizer)
    # =========================================================================

    def test_predict_fertilizer_valid(self):
        """Test valid fertilizer prediction returns 200 and advice."""
        payload = {
            "temperature": 26.0,
            "humidity": 52.0,
            "moisture": 38.0,
            "soilType": "Sandy",
            "cropType": "Maize",
            "nitrogen": 37.0,
            "potassium": 0.0,
            "phosphorous": 0.0
        }
        response = self.client.post("/api/predict-fertilizer", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("fertilizer", data["result"])
        self.assertIn("soil_advice", data["result"])
        self.assertIsInstance(data["result"]["fertilizer"], str)

    def test_predict_fertilizer_unseen_and_case_insensitive(self):
        """Test lowercase / unseen soil and crop types handle gracefully."""
        payload = {
            "temperature": 28.0,
            "humidity": 65.0,
            "moisture": 45.0,
            "soilType": "sandy",  # lowercase
            "cropType": "rice",   # lowercase alias
            "nitrogen": 80.0,     # kg/ha scale (gets scaled down safely)
            "potassium": 40.0,
            "phosphorous": 40.0
        }
        response = self.client.post("/api/predict-fertilizer", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])

        # Unseen soil and crop type
        payload_unseen = {
            "temperature": 25.0,
            "humidity": 60.0,
            "moisture": 40.0,
            "soilType": "Volcanic Ash",
            "cropType": "Mystical Orchid",
            "nitrogen": 20.0,
            "potassium": 10.0,
            "phosphorous": 10.0
        }
        r = self.client.post("/api/predict-fertilizer", json=payload_unseen)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["success"])

    def test_predict_fertilizer_invalid_inputs(self):
        """Test missing fields, negative nutrients, and NaN inputs return 400."""
        # Missing soilType
        r = self.client.post("/api/predict-fertilizer", json={"cropType": "Maize", "temperature": 25})
        self.assertEqual(r.status_code, 400)

        # Negative moisture
        r = self.client.post("/api/predict-fertilizer", json={
            "soilType": "Loamy", "cropType": "Wheat", "temperature": 20,
            "humidity": 50, "moisture": -5, "nitrogen": 20, "potassium": 10, "phosphorous": 10
        })
        self.assertEqual(r.status_code, 400)

        # Negative nitrogen
        r = self.client.post("/api/predict-fertilizer", json={
            "soilType": "Loamy", "cropType": "Wheat", "temperature": 20,
            "humidity": 50, "moisture": 30, "nitrogen": -10, "potassium": 10, "phosphorous": 10
        })
        self.assertEqual(r.status_code, 400)

        # Non-numeric
        r = self.client.post("/api/predict-fertilizer", json={
            "soilType": "Loamy", "cropType": "Wheat", "temperature": "hot",
            "humidity": 50, "moisture": 30, "nitrogen": 10, "potassium": 10, "phosphorous": 10
        })
        self.assertEqual(r.status_code, 400)

    # =========================================================================
    # 4. CHATBOT ENDPOINT (/api/chat)
    # =========================================================================

    def test_chat_endpoint_validation(self):
        """Test chat endpoint input validation."""
        # Empty JSON
        r = self.client.post("/api/chat", json={})
        self.assertEqual(r.status_code, 400)

        # Missing message
        r = self.client.post("/api/chat", json={"message": "   "})
        self.assertEqual(r.status_code, 400)

        # Message too long (>500 chars)
        r = self.client.post("/api/chat", json={"message": "x" * 501})
        self.assertEqual(r.status_code, 400)

        # Non-dict body
        r = self.client.post("/api/chat", json=["not", "a", "dict"])
        self.assertEqual(r.status_code, 400)

    # =========================================================================
    # 5. CROPMANAGER CROSS-MODULE RESOLUTION AUDIT
    # =========================================================================

    def test_crop_manager_recommendation_crops(self):
        """Verify all 22 recommendation crops map to valid classes."""
        crops = CropManager.get_recommendation_crops()
        self.assertEqual(len(crops), 22)

        for key, data in crops.items():
            self.assertIn("yield_class", data)
            self.assertIn("fertilizer_class", data)
            # Test resolution functions
            resolved_yield = CropManager.resolve_for_yield(key)
            resolved_fert = CropManager.resolve_for_fertilizer(key)
            self.assertIsInstance(resolved_yield, str)
            self.assertGreater(len(resolved_yield), 0)
            self.assertIsInstance(resolved_fert, str)
            self.assertGreater(len(resolved_fert), 0)

    def test_crop_manager_edge_cases(self):
        """Verify CropManager handles None, empty strings, numbers, NaN, and arbitrary strings safely."""
        edge_cases = [None, "", "   ", 123, float("nan"), [], {}, "UnknownCrop123", "!@#$%"]

        for val in edge_cases:
            res_yield = CropManager.resolve_for_yield(val)
            res_fert = CropManager.resolve_for_fertilizer(val)
            self.assertIsInstance(res_yield, str)
            self.assertGreater(len(res_yield), 0)
            self.assertIsInstance(res_fert, str)
            self.assertGreater(len(res_fert), 0)
            # Check that resolve_for_fertilizer returns one of the 11 classes
            self.assertIn(res_fert, [
                "Paddy", "Wheat", "Maize", "Barley", "Millets",
                "Pulses", "Ground Nuts", "Oil seeds", "Cotton",
                "Sugarcane", "Tobacco"
            ])

    def test_crop_manager_dropdown_options(self):
        """Verify dropdown helper methods return well-formed lists."""
        yield_options = CropManager.get_yield_dropdown_options(["Rice", "Wheat", "Coconut "])
        self.assertEqual(len(yield_options), 3)
        for opt in yield_options:
            self.assertIn("value", opt)
            self.assertIn("label", opt)
            self.assertIn("category", opt)

        fert_options = CropManager.get_fertilizer_dropdown_options()
        self.assertEqual(len(fert_options), 11)


if __name__ == "__main__":
    unittest.main()
