"""
Stage 1 QA Test Script: Crop Recommendation
Automated test suite using Flask test client against web_app.py
Exhaustively tests all 22 supported crop classes and input boundary conditions.
"""

import json
import os
import sys
import unittest
from web_app import app

class CropRecommendationQATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure test client
        app.config['TESTING'] = True
        cls.client = app.test_client()
        cls.crop_test_results = []
        cls.boundary_test_results = []

    # -------------------------------------------------------------------------
    # TEST SUITE 1: 22 Target Crop Classes Test
    # -------------------------------------------------------------------------
    def test_01_all_22_crop_classes(self):
        """Construct realistic agronomic profiles for all 22 crops and verify accuracy."""
        profiles = {
            'rice': {
                'n': 80, 'p': 40, 'k': 40, 'temperature': 24.0, 'humidity': 82.0, 'ph': 6.5, 'rainfall': 240.0
            },
            'maize': {
                'n': 80, 'p': 45, 'k': 20, 'temperature': 23.0, 'humidity': 65.0, 'ph': 6.5, 'rainfall': 80.0
            },
            'chickpea': {
                'n': 40, 'p': 68, 'k': 80, 'temperature': 19.0, 'humidity': 17.0, 'ph': 7.3, 'rainfall': 80.0
            },
            'kidneybeans': {
                'n': 20, 'p': 68, 'k': 20, 'temperature': 20.0, 'humidity': 22.0, 'ph': 5.7, 'rainfall': 105.0
            },
            'pigeonpeas': {
                'n': 20, 'p': 68, 'k': 20, 'temperature': 28.0, 'humidity': 55.0, 'ph': 5.8, 'rainfall': 150.0
            },
            'mothbeans': {
                'n': 22, 'p': 48, 'k': 20, 'temperature': 28.0, 'humidity': 53.0, 'ph': 6.8, 'rainfall': 51.0
            },
            'mungbean': {
                'n': 21, 'p': 47, 'k': 20, 'temperature': 28.5, 'humidity': 86.0, 'ph': 6.7, 'rainfall': 49.0
            },
            'blackgram': {
                'n': 40, 'p': 68, 'k': 20, 'temperature': 30.0, 'humidity': 65.0, 'ph': 7.2, 'rainfall': 68.0
            },
            'lentil': {
                'n': 19, 'p': 68, 'k': 19, 'temperature': 25.0, 'humidity': 65.0, 'ph': 6.9, 'rainfall': 46.0
            },
            'pomegranate': {
                'n': 22, 'p': 20, 'k': 40, 'temperature': 22.0, 'humidity': 90.0, 'ph': 6.4, 'rainfall': 107.0
            },
            'banana': {
                'n': 100, 'p': 82, 'k': 50, 'temperature': 27.0, 'humidity': 80.0, 'ph': 6.0, 'rainfall': 105.0
            },
            'mango': {
                'n': 20, 'p': 27, 'k': 30, 'temperature': 31.0, 'humidity': 50.0, 'ph': 5.7, 'rainfall': 95.0
            },
            'grapes': {
                'n': 23, 'p': 133, 'k': 200, 'temperature': 24.0, 'humidity': 82.0, 'ph': 6.0, 'rainfall': 69.0
            },
            'watermelon': {
                'n': 99, 'p': 18, 'k': 50, 'temperature': 26.0, 'humidity': 85.0, 'ph': 6.5, 'rainfall': 51.0
            },
            'muskmelon': {
                'n': 100, 'p': 18, 'k': 50, 'temperature': 28.5, 'humidity': 92.0, 'ph': 6.4, 'rainfall': 25.0
            },
            'apple': {
                'n': 22, 'p': 130, 'k': 200, 'temperature': 22.0, 'humidity': 92.0, 'ph': 6.0, 'rainfall': 115.0
            },
            'orange': {
                'n': 20, 'p': 16, 'k': 10, 'temperature': 23.0, 'humidity': 92.0, 'ph': 7.0, 'rainfall': 110.0
            },
            'papaya': {
                'n': 50, 'p': 59, 'k': 50, 'temperature': 34.0, 'humidity': 92.0, 'ph': 6.7, 'rainfall': 142.0
            },
            'coconut': {
                'n': 22, 'p': 17, 'k': 30, 'temperature': 27.0, 'humidity': 95.0, 'ph': 6.0, 'rainfall': 176.0
            },
            'cotton': {
                'n': 120, 'p': 46, 'k': 20, 'temperature': 24.0, 'humidity': 80.0, 'ph': 6.8, 'rainfall': 80.0
            },
            'jute': {
                'n': 78, 'p': 46, 'k': 40, 'temperature': 25.0, 'humidity': 80.0, 'ph': 6.7, 'rainfall': 175.0
            },
            'coffee': {
                'n': 101, 'p': 29, 'k': 30, 'temperature': 25.5, 'humidity': 58.0, 'ph': 6.8, 'rainfall': 158.0
            }
        }

        print("\n" + "="*100)
        print("STAGE 1: EXHAUSTIVE 22 CROP CLASS VERIFICATION")
        print("="*100)

        for expected_crop, profile in profiles.items():
            resp = self.client.post('/api/predict-crop', json=profile)
            status_code = resp.status_code
            self.assertEqual(status_code, 200, f"Expected 200 OK for crop: {expected_crop}")

            data = resp.get_json()
            self.assertTrue(data.get('success'), f"Expected success=True for {expected_crop}")
            
            result = data.get('result', {})
            predicted_crop = result.get('crop')
            confidence = result.get('confidence')
            advice = result.get('advice')

            # Verification 1: Matching crop returned
            self.assertEqual(predicted_crop, expected_crop, f"Prediction mismatch: Expected {expected_crop}, got {predicted_crop}")

            # Verification 2: Confidence score in valid range [0, 100]
            self.assertIsInstance(confidence, (int, float))
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 100.0)

            # Verification 3: Soil advice text generated
            self.assertIsInstance(advice, str)
            self.assertGreater(len(advice.strip()), 0)

            # Store result
            self.__class__.crop_test_results.append({
                'crop': expected_crop,
                'inputs': profile,
                'http_status': status_code,
                'predicted_crop': predicted_crop,
                'confidence': confidence,
                'advice': advice,
                'match': predicted_crop == expected_crop,
                'status': 'PASS'
            })

    # -------------------------------------------------------------------------
    # TEST SUITE 2: Boundary Conditions & Edge Cases
    # -------------------------------------------------------------------------
    def test_02_extreme_ph_conditions(self):
        """Test extreme pH values (<0 or >14) and valid boundary extremes (0, 14)."""
        edge_cases = [
            ("Extreme Low pH (< 0)", {'n': 50, 'p': 50, 'k': 50, 'temperature': 25, 'humidity': 50, 'ph': -1.5, 'rainfall': 100}, 400, "pH must be between 0 and 14"),
            ("Extreme High pH (> 14)", {'n': 50, 'p': 50, 'k': 50, 'temperature': 25, 'humidity': 50, 'ph': 15.0, 'rainfall': 100}, 400, "pH must be between 0 and 14"),
            ("Boundary Lower Bound pH (0.0)", {'n': 50, 'p': 50, 'k': 50, 'temperature': 25, 'humidity': 50, 'ph': 0.0, 'rainfall': 100}, 200, None),
            ("Boundary Upper Bound pH (14.0)", {'n': 50, 'p': 50, 'k': 50, 'temperature': 25, 'humidity': 50, 'ph': 14.0, 'rainfall': 100}, 200, None),
        ]

        for desc, payload, expected_status, expected_err in edge_cases:
            resp = self.client.post('/api/predict-crop', json=payload)
            self.assertEqual(resp.status_code, expected_status, f"Failed for {desc}")
            data = resp.get_json()
            if expected_status == 400:
                self.assertFalse(data.get('success'))
                self.assertIn(expected_err, data.get('error', ''))
            else:
                self.assertTrue(data.get('success'))
            
            self.__class__.boundary_test_results.append({
                'category': 'pH Range Validation',
                'description': desc,
                'payload': payload,
                'expected_status': expected_status,
                'actual_status': resp.status_code,
                'response': data,
                'status': 'PASS'
            })

    def test_03_extreme_humidity_conditions(self):
        """Test extreme humidity values (<0 or >100) and valid boundary extremes (0, 100)."""
        edge_cases = [
            ("Extreme Low Humidity (< 0)", {'n': 50, 'p': 50, 'k': 50, 'temperature': 25, 'humidity': -10.0, 'ph': 6.5, 'rainfall': 100}, 400, "Humidity must be between 0 and 100"),
            ("Extreme High Humidity (> 100)", {'n': 50, 'p': 50, 'k': 50, 'temperature': 25, 'humidity': 110.0, 'ph': 6.5, 'rainfall': 100}, 400, "Humidity must be between 0 and 100"),
            ("Boundary Lower Bound Humidity (0.0)", {'n': 50, 'p': 50, 'k': 50, 'temperature': 25, 'humidity': 0.0, 'ph': 6.5, 'rainfall': 100}, 200, None),
            ("Boundary Upper Bound Humidity (100.0)", {'n': 50, 'p': 50, 'k': 50, 'temperature': 25, 'humidity': 100.0, 'ph': 6.5, 'rainfall': 100}, 200, None),
        ]

        for desc, payload, expected_status, expected_err in edge_cases:
            resp = self.client.post('/api/predict-crop', json=payload)
            self.assertEqual(resp.status_code, expected_status, f"Failed for {desc}")
            data = resp.get_json()
            if expected_status == 400:
                self.assertFalse(data.get('success'))
                self.assertIn(expected_err, data.get('error', ''))
            else:
                self.assertTrue(data.get('success'))
            
            self.__class__.boundary_test_results.append({
                'category': 'Humidity Range Validation',
                'description': desc,
                'payload': payload,
                'expected_status': expected_status,
                'actual_status': resp.status_code,
                'response': data,
                'status': 'PASS'
            })

    def test_04_negative_input_values(self):
        """Test negative values for N, P, K, rainfall for graceful handling or rejection."""
        edge_cases = [
            ("Negative Nitrogen (N = -25)", {'n': -25, 'p': 50, 'k': 50, 'temperature': 25, 'humidity': 50, 'ph': 6.5, 'rainfall': 100}),
            ("Negative Phosphorus (P = -15)", {'n': 50, 'p': -15, 'k': 50, 'temperature': 25, 'humidity': 50, 'ph': 6.5, 'rainfall': 100}),
            ("Negative Potassium (K = -30)", {'n': 50, 'p': 50, 'k': -30, 'temperature': 25, 'humidity': 50, 'ph': 6.5, 'rainfall': 100}),
            ("Negative Rainfall (Rainfall = -50)", {'n': 50, 'p': 50, 'k': 50, 'temperature': 25, 'humidity': 50, 'ph': 6.5, 'rainfall': -50}),
            ("All Negative NPK + Rainfall", {'n': -40, 'p': -40, 'k': -40, 'temperature': 25, 'humidity': 50, 'ph': 6.5, 'rainfall': -40}),
        ]

        for desc, payload in edge_cases:
            resp = self.client.post('/api/predict-crop', json=payload)
            # Must not crash with 500 internal server error
            self.assertIn(resp.status_code, [200, 400], f"Unhandled server error ({resp.status_code}) on {desc}")
            data = resp.get_json()
            
            self.__class__.boundary_test_results.append({
                'category': 'Negative Values Handling',
                'description': desc,
                'payload': payload,
                'expected_status': '200 or 400',
                'actual_status': resp.status_code,
                'response': data,
                'status': 'PASS'
            })

    def test_05_missing_fields_and_malformed_json(self):
        """Test missing fields, missing body, invalid data types, and malformed JSON syntax."""
        edge_cases = [
            ("Empty Body with JSON Content-Type", "", "application/json", 400, "Bad Request"),
            ("Malformed JSON Syntax", "{\"n\": 50, \"p\": 50, malformed", "application/json", 400, "Bad Request"),
            ("String Type for Numeric N", json.dumps({'n': 'invalid_string', 'p': 50, 'k': 50, 'temperature': 25, 'humidity': 50, 'ph': 6.5, 'rainfall': 100}), "application/json", 400, "Invalid input"),
            ("Empty JSON Object ({})", json.dumps({}), "application/json", 400, "No JSON data provided"),
            ("Partial Payload (Only N & P)", json.dumps({'n': 80, 'p': 40}), "application/json", 200, None),
        ]

        for desc, data_str, content_type, expected_status, expected_err in edge_cases:
            resp = self.client.post('/api/predict-crop', data=data_str, content_type=content_type)
            self.assertEqual(resp.status_code, expected_status, f"Status code mismatch for {desc}")
            data = resp.get_json()
            if expected_status == 400:
                self.assertFalse(data.get('success'), f"Expected success=False for {desc}")
                if expected_err:
                    self.assertIn(expected_err.lower(), str(data).lower())
            else:
                self.assertTrue(data.get('success'), f"Expected success=True for {desc}")

            self.__class__.boundary_test_results.append({
                'category': 'Missing Fields & Malformed JSON',
                'description': desc,
                'payload': data_str[:40],
                'expected_status': expected_status,
                'actual_status': resp.status_code,
                'response': data,
                'status': 'PASS'
            })

    @classmethod
    def tearDownClass(cls):
        # Print summary reports
        print("\n" + "="*115)
        print(f"{'Crop':<15} | {'N':>3} {'P':>3} {'K':>3} {'Temp':>5} {'Hum':>5} {'pH':>4} {'Rain':>5} | {'Status':<6} | {'Predicted':<15} | {'Conf':>7} | {'Result'}")
        print("="*115)
        for r in cls.crop_test_results:
            inp = r['inputs']
            print(f"{r['crop']:<15} | {inp['n']:>3} {inp['p']:>3} {inp['k']:>3} {inp['temperature']:>5.1f} {inp['humidity']:>5.1f} {inp['ph']:>4.1f} {inp['rainfall']:>5.1f} | {r['http_status']:<6} | {r['predicted_crop']:<15} | {r['confidence']:>6.2f}% | {r['status']}")

        print("\n" + "="*115)
        print("STAGE 1: INPUT BOUNDARY & EDGE CASE EVALUATION SUMMARY")
        print("="*115)
        print(f"{'Category':<28} | {'Description':<36} | {'Expected':<10} | {'Actual':<8} | {'Status'}")
        print("-" * 115)
        for b in cls.boundary_test_results:
            print(f"{b['category']:<28} | {b['description']:<36} | {str(b['expected_status']):<10} | {str(b['actual_status']):<8} | {b['status']}")
        print("="*115)

        # Save machine-readable report to json
        report = {
            'crop_tests': cls.crop_test_results,
            'boundary_tests': cls.boundary_test_results,
            'total_crops_tested': len(cls.crop_test_results),
            'total_boundary_cases_tested': len(cls.boundary_test_results),
            'all_crops_matched': all(r['match'] for r in cls.crop_test_results)
        }
        with open('stage1_crop_qa_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n[OK] Detailed QA test report successfully generated: stage1_crop_qa_report.json")


if __name__ == '__main__':
    unittest.main()
