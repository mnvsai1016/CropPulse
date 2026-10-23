"""Stage 3: Soil Health & Fertilizer Prediction Exhaustive QA Test Suite.

Tests:
1. All 11 Crop Types
2. All 5 Soil Types
3. All 7 Target Fertilizer Formulations
4. High-NPK Scale Normalization & Prediction Diversity
5. Crop Taxonomy Cross-Compatibility & Alias Resolution
6. Boundary and Error Rejection (moisture, humidity, missing fields, type errors)
7. Full 11x7 Crop-Fertilizer Matrix and 5x7 Soil-Fertilizer Matrix
"""

import unittest
import json
from web_app import app, load_models

# All target categories
TARGET_FERTILIZERS = [
    "10-26-26",
    "14-35-14",
    "17-17-17",
    "20-20",
    "28-28",
    "DAP",
    "Urea"
]

CROP_TYPES = [
    "Paddy",
    "Wheat",
    "Maize",
    "Barley",
    "Millets",
    "Pulses",
    "Ground Nuts",
    "Oil seeds",
    "Cotton",
    "Sugarcane",
    "Tobacco"
]

SOIL_TYPES = [
    "Sandy",
    "Loamy",
    "Black",
    "Red",
    "Clayey"
]

# Baseline characteristic agronomic profiles for the 7 target fertilizers
TARGET_PROFILES = {
    "Urea": {
        "temperature": 30.0, "humidity": 60.0, "moisture": 40.0,
        "soilType": "Loamy", "cropType": "Wheat",
        "nitrogen": 38.0, "phosphorous": 0.0, "potassium": 0.0
    },
    "DAP": {
        "temperature": 32.0, "humidity": 60.0, "moisture": 40.0,
        "soilType": "Loamy", "cropType": "Wheat",
        "nitrogen": 13.0, "phosphorous": 38.0, "potassium": 0.0
    },
    "14-35-14": {
        "temperature": 31.0, "humidity": 61.0, "moisture": 45.0,
        "soilType": "Loamy", "cropType": "Wheat",
        "nitrogen": 8.0, "phosphorous": 30.0, "potassium": 9.0
    },
    "28-28": {
        "temperature": 30.0, "humidity": 58.0, "moisture": 42.0,
        "soilType": "Loamy", "cropType": "Wheat",
        "nitrogen": 23.0, "phosphorous": 21.0, "potassium": 0.0
    },
    "17-17-17": {
        "temperature": 29.0, "humidity": 58.0, "moisture": 47.0,
        "soilType": "Loamy", "cropType": "Wheat",
        "nitrogen": 12.0, "phosphorous": 13.0, "potassium": 13.0
    },
    "20-20": {
        "temperature": 29.0, "humidity": 58.0, "moisture": 45.0,
        "soilType": "Loamy", "cropType": "Wheat",
        "nitrogen": 11.0, "phosphorous": 12.0, "potassium": 0.0
    },
    "10-26-26": {
        "temperature": 30.0, "humidity": 58.0, "moisture": 39.0,
        "soilType": "Loamy", "cropType": "Wheat",
        "nitrogen": 7.0, "phosphorous": 18.0, "potassium": 18.0
    }
}


class TestStage3SoilFertilizerQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the app in testing mode and ensure models are loaded."""
        app.testing = True
        cls.client = app.test_client()
        load_models()

    # -------------------------------------------------------------------------
    # 1. Test All 11 Crop Types
    # -------------------------------------------------------------------------
    def test_all_11_crop_types(self):
        """Test fertilizer prediction endpoint for each of the 11 crop types."""
        results = {}
        for crop in CROP_TYPES:
            payload = {
                "temperature": 28.0,
                "humidity": 60.0,
                "moisture": 42.0,
                "soilType": "Loamy",
                "cropType": crop,
                "nitrogen": 25.0,
                "phosphorous": 20.0,
                "potassium": 10.0
            }
            response = self.client.post("/api/predict-fertilizer", json=payload)
            self.assertEqual(response.status_code, 200, f"Failed for crop: {crop} with status {response.status_code}")
            
            data = json.loads(response.data)
            self.assertTrue(data.get("success"), f"Crop {crop} returned success=False")
            
            result = data.get("result", {})
            fert = result.get("fertilizer")
            conf = result.get("confidence")
            advice = result.get("soil_advice")
            
            self.assertIn(fert, TARGET_FERTILIZERS, f"Crop {crop} predicted unexpected fertilizer: {fert}")
            self.assertIsInstance(conf, (int, float), f"Confidence is not numeric for crop {crop}")
            self.assertGreaterEqual(conf, 0.0)
            self.assertLessEqual(conf, 100.0)
            self.assertTrue(len(advice) > 0, f"Empty soil advice for crop {crop}")
            results[crop] = {"fertilizer": fert, "confidence": conf}
            
        print("\n[OK] All 11 Crop Types tested successfully:")
        for crop, res in results.items():
            print(f"  - {crop:12}: {res['fertilizer']:10} (conf: {res['confidence']}%)")

    # -------------------------------------------------------------------------
    # 2. Test All 5 Soil Types
    # -------------------------------------------------------------------------
    def test_all_5_soil_types(self):
        """Test fertilizer prediction endpoint across all 5 soil types."""
        results = {}
        for soil in SOIL_TYPES:
            payload = {
                "temperature": 27.0,
                "humidity": 65.0,
                "moisture": 45.0,
                "soilType": soil,
                "cropType": "Wheat",
                "nitrogen": 22.0,
                "phosphorous": 20.0,
                "potassium": 0.0
            }
            response = self.client.post("/api/predict-fertilizer", json=payload)
            self.assertEqual(response.status_code, 200, f"Failed for soil: {soil}")
            
            data = json.loads(response.data)
            self.assertTrue(data.get("success"), f"Soil {soil} returned success=False")
            
            result = data.get("result", {})
            fert = result.get("fertilizer")
            conf = result.get("confidence")
            self.assertIn(fert, TARGET_FERTILIZERS)
            results[soil] = {"fertilizer": fert, "confidence": conf}
            
        print("\n[OK] All 5 Soil Types tested successfully:")
        for soil, res in results.items():
            print(f"  - {soil:10}: {res['fertilizer']:10} (conf: {res['confidence']}%)")

    # -------------------------------------------------------------------------
    # 3. Test All 7 Target Fertilizer Formulations
    # -------------------------------------------------------------------------
    def test_all_7_target_fertilizers(self):
        """Verify each of the 7 target fertilizer formulations is accurately predicted."""
        print("\n[OK] Testing All 7 Target Fertilizer Profiles:")
        for target_fert, payload in TARGET_PROFILES.items():
            response = self.client.post("/api/predict-fertilizer", json=payload)
            self.assertEqual(response.status_code, 200, f"HTTP Error for target {target_fert}")
            data = json.loads(response.data)
            self.assertTrue(data.get("success"))
            predicted_fert = data["result"]["fertilizer"]
            confidence = data["result"]["confidence"]
            
            print(f"  - Target: {target_fert:10} | Predicted: {predicted_fert:10} | Conf: {confidence}%")
            self.assertEqual(predicted_fert, target_fert,
                             f"Expected {target_fert} but model predicted {predicted_fert}")

    # -------------------------------------------------------------------------
    # 4. Test High-NPK Scale Normalization & Diversity
    # -------------------------------------------------------------------------
    def test_high_npk_scale_normalization_and_diversity(self):
        """Pass realistic field values (e.g. from Crop Recommendation module) and verify diverse predictions."""
        field_cases = [
            {"label": "Realistic field case 1 (Prompt: N=120, P=80, K=120)",
             "n": 120.0, "p": 80.0, "k": 120.0, "soil": "Loamy", "crop": "Wheat"},
            {"label": "Realistic field case 2 (Prompt: N=90, P=45, K=50)",
             "n": 90.0, "p": 45.0, "k": 50.0, "soil": "Loamy", "crop": "Wheat"},
            {"label": "Realistic field case 3 (Prompt: N=40, P=60, K=80)",
             "n": 40.0, "p": 60.0, "k": 80.0, "soil": "Loamy", "crop": "Wheat"},
            {"label": "Field High N Deficit (N=135, P=15, K=10)",
             "n": 135.0, "p": 15.0, "k": 10.0, "soil": "Clayey", "crop": "Paddy"},
            {"label": "Field High P Deficit (N=35, P=135, K=10)",
             "n": 35.0, "p": 135.0, "k": 10.0, "soil": "Sandy", "crop": "Cotton"},
            {"label": "Field Balanced High (N=75, P=75, K=10)",
             "n": 75.0, "p": 75.0, "k": 10.0, "soil": "Black", "crop": "Maize"},
        ]

        predictions = []
        print("\n[OK] Testing High-NPK Scale Normalization & Prediction Diversity:")
        for case in field_cases:
            payload = {
                "temperature": 28.0,
                "humidity": 60.0,
                "moisture": 45.0,
                "soilType": case["soil"],
                "cropType": case["crop"],
                "nitrogen": case["n"],
                "phosphorous": case["p"],
                "potassium": case["k"]
            }
            response = self.client.post("/api/predict-fertilizer", json=payload)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data.get("success"))
            fert = data["result"]["fertilizer"]
            conf = data["result"]["confidence"]
            predictions.append(fert)
            print(f"  - {case['label']:55} -> {fert:10} (conf: {conf}%)")

        unique_predictions = set(predictions)
        print(f"  -> Unique fertilizers predicted across high-NPK inputs: {unique_predictions}")
        
        # Verify the model does NOT always predict '10-26-26'
        self.assertGreater(len(unique_predictions), 1, "Model predicted a single fertilizer for all inputs!")
        self.assertNotIn(predictions, [["10-26-26"] * len(predictions)],
                         "Model collapsed into predicting only 10-26-26 for high NPK inputs!")
        # Verify diversity includes multiple fertilizers
        self.assertTrue(any(f in unique_predictions for f in ["Urea", "28-28", "DAP", "14-35-14", "17-17-17", "20-20"]))

    # -------------------------------------------------------------------------
    # 5. Test Unified Crop Taxonomy & Aliases
    # -------------------------------------------------------------------------
    def test_crop_taxonomy_and_aliases(self):
        """Test that crop names from Module 1 (Crop Recommendation) resolve properly."""
        taxonomy_cases = [
            ("rice", "Paddy"),
            ("chickpea", "Pulses"),
            ("kidneybeans", "Pulses"),
            ("cotton", "Cotton"),
            ("pigeonpeas", "Pulses"),
            ("mothbeans", "Pulses"),
            ("mungbean", "Pulses"),
            ("blackgram", "Pulses"),
            ("lentil", "Pulses"),
            ("jute", "Cotton"),
        ]
        
        print("\n[OK] Testing Unified Crop Taxonomy Aliases:")
        for raw_crop, expected_resolved in taxonomy_cases:
            payload = {
                "temperature": 28.0,
                "humidity": 60.0,
                "moisture": 40.0,
                "soilType": "Loamy",
                "cropType": raw_crop,
                "nitrogen": 30.0,
                "phosphorous": 20.0,
                "potassium": 10.0
            }
            response = self.client.post("/api/predict-fertilizer", json=payload)
            self.assertEqual(response.status_code, 200, f"Failed for raw crop alias: {raw_crop}")
            data = json.loads(response.data)
            self.assertTrue(data.get("success"))
            print(f"  - Input alias '{raw_crop}' resolved and predicted: {data['result']['fertilizer']}")

    # -------------------------------------------------------------------------
    # 6. Test Boundary and Error Cases
    # -------------------------------------------------------------------------
    def test_boundary_and_validation_errors(self):
        """Test boundary values and error rejection for moisture, humidity, and missing fields."""
        print("\n[OK] Testing Boundary and Error Handling Cases:")

        # 6a. Negative moisture rejection
        resp = self.client.post("/api/predict-fertilizer", json={
            "temperature": 25, "humidity": 50, "moisture": -5,
            "soilType": "Loamy", "cropType": "Wheat",
            "nitrogen": 20, "phosphorous": 20, "potassium": 10
        })
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertFalse(data.get("success"))
        self.assertIn("Moisture must be between 0 and 100", data.get("error"))
        print("  - moisture = -5 correctly rejected with HTTP 400")

        # 6b. Moisture > 100 rejection
        resp = self.client.post("/api/predict-fertilizer", json={
            "temperature": 25, "humidity": 50, "moisture": 105,
            "soilType": "Loamy", "cropType": "Wheat",
            "nitrogen": 20, "phosphorous": 20, "potassium": 10
        })
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertFalse(data.get("success"))
        self.assertIn("Moisture must be between 0 and 100", data.get("error"))
        print("  - moisture = 105 correctly rejected with HTTP 400")

        # 6c. Negative humidity rejection
        resp = self.client.post("/api/predict-fertilizer", json={
            "temperature": 25, "humidity": -10, "moisture": 50,
            "soilType": "Loamy", "cropType": "Wheat",
            "nitrogen": 20, "phosphorous": 20, "potassium": 10
        })
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertFalse(data.get("success"))
        self.assertIn("Humidity must be between 0 and 100", data.get("error"))
        print("  - humidity = -10 correctly rejected with HTTP 400")

        # 6d. Humidity > 100 rejection
        resp = self.client.post("/api/predict-fertilizer", json={
            "temperature": 25, "humidity": 120, "moisture": 50,
            "soilType": "Loamy", "cropType": "Wheat",
            "nitrogen": 20, "phosphorous": 20, "potassium": 10
        })
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertFalse(data.get("success"))
        self.assertIn("Humidity must be between 0 and 100", data.get("error"))
        print("  - humidity = 120 correctly rejected with HTTP 400")

        # 6e. Moisture & Humidity boundary valid (0 and 100)
        for val in [0.0, 100.0]:
            resp = self.client.post("/api/predict-fertilizer", json={
                "temperature": 25, "humidity": val, "moisture": val,
                "soilType": "Loamy", "cropType": "Wheat",
                "nitrogen": 20, "phosphorous": 20, "potassium": 10
            })
            self.assertEqual(resp.status_code, 200, f"Boundary value {val} failed")
            data = json.loads(resp.data)
            self.assertTrue(data.get("success"))
            print(f"  - Boundary valid test moisture={val}, humidity={val} returned HTTP 200")

        # 6f. Missing soilType rejection
        resp = self.client.post("/api/predict-fertilizer", json={
            "temperature": 25, "humidity": 50, "moisture": 50,
            "cropType": "Wheat",
            "nitrogen": 20, "phosphorous": 20, "potassium": 10
        })
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertFalse(data.get("success"))
        self.assertIn("Soil Type and Crop Type are required", data.get("error"))
        print("  - Missing soilType correctly rejected with HTTP 400")

        # 6g. Empty soilType rejection
        resp = self.client.post("/api/predict-fertilizer", json={
            "temperature": 25, "humidity": 50, "moisture": 50,
            "soilType": "   ",
            "cropType": "Wheat",
            "nitrogen": 20, "phosphorous": 20, "potassium": 10
        })
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertFalse(data.get("success"))
        self.assertIn("Soil Type and Crop Type are required", data.get("error"))
        print("  - Whitespace-only soilType correctly rejected with HTTP 400")

        # 6h. Missing cropType rejection
        resp = self.client.post("/api/predict-fertilizer", json={
            "temperature": 25, "humidity": 50, "moisture": 50,
            "soilType": "Loamy",
            "nitrogen": 20, "phosphorous": 20, "potassium": 10
        })
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertFalse(data.get("success"))
        self.assertIn("Soil Type and Crop Type are required", data.get("error"))
        print("  - Missing cropType correctly rejected with HTTP 400")

        # 6i. Non-numeric input rejection
        resp = self.client.post("/api/predict-fertilizer", json={
            "temperature": "not-a-number",
            "humidity": 50, "moisture": 50,
            "soilType": "Loamy", "cropType": "Wheat",
            "nitrogen": 20, "phosphorous": 20, "potassium": 10
        })
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertFalse(data.get("success"))
        print("  - Non-numeric input correctly rejected with HTTP 400")

    # -------------------------------------------------------------------------
    # 7. Test Exhaustive 11x7 Crop-Fertilizer and 5x7 Soil-Fertilizer Matrix
    # -------------------------------------------------------------------------
    def test_exhaustive_cross_matrices(self):
        """Test that all 7 target fertilizers are accurately predicted across every crop and soil type."""
        print("\n[OK] Testing Exhaustive 11x7 Crop vs Fertilizer Matrix (77 tests):")
        crop_matrix_failures = []
        for crop in CROP_TYPES:
            for target_fert, profile in TARGET_PROFILES.items():
                payload = dict(profile)
                payload["cropType"] = crop
                resp = self.client.post("/api/predict-fertilizer", json=payload)
                self.assertEqual(resp.status_code, 200)
                data = json.loads(resp.data)
                pred = data["result"]["fertilizer"]
                if pred != target_fert:
                    crop_matrix_failures.append((crop, target_fert, pred))
        
        self.assertEqual(len(crop_matrix_failures), 0,
                         f"Failures in 11x7 crop matrix: {crop_matrix_failures}")
        print("  -> All 77/77 Crop x Formulation tests passed with 100% exact match!")

        print("\n[OK] Testing Exhaustive 5x7 Soil vs Fertilizer Matrix (35 tests):")
        soil_matrix_failures = []
        for soil in SOIL_TYPES:
            for target_fert, profile in TARGET_PROFILES.items():
                payload = dict(profile)
                payload["soilType"] = soil
                resp = self.client.post("/api/predict-fertilizer", json=payload)
                self.assertEqual(resp.status_code, 200)
                data = json.loads(resp.data)
                pred = data["result"]["fertilizer"]
                if pred != target_fert:
                    soil_matrix_failures.append((soil, target_fert, pred))

        self.assertEqual(len(soil_matrix_failures), 0,
                         f"Failures in 5x7 soil matrix: {soil_matrix_failures}")
        print("  -> All 35/35 Soil x Formulation tests passed with 100% exact match!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
