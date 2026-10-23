"""
CropPulse End-to-End Workflow & UI QA Test Suite
Exhaustively tests HTTP GET endpoints, cross-stage redirects, API predictions, and static assets.
Supports both direct CLI execution and `python -m unittest test_e2e_integration.py`.
"""

import subprocess
import sys
import unittest
from bs4 import BeautifulSoup
from web_app import app

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


class TestCropPulseE2EIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    # -------------------------------------------------------------------------
    # 1. HTTP GET Endpoints Verification
    # -------------------------------------------------------------------------
    def test_01_landing_page_structure_and_assets(self):
        """Verify landing page (/), plant growing animation, CTA buttons, and chatbot scripts."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        soup = BeautifulSoup(res.data.decode('utf-8'), 'html.parser')

        # Plant growing opening animation SVG structure
        loader = soup.find(id="plant-intro-loader")
        self.assertIsNotNone(loader, "Plant loader overlay div missing")
        self.assertIn("plant-loader-overlay", loader.get("class", []))

        svg = loader.find("svg", class_="plant-svg")
        self.assertIsNotNone(svg, "Plant SVG container missing")
        self.assertIsNotNone(loader.find("path", class_="plant-stem"), "Plant stem SVG path missing")
        self.assertGreaterEqual(len(loader.find_all("circle", class_="pulse-ring")), 3, "Pulse rings missing")
        self.assertGreaterEqual(len(loader.find_all("g", class_="leaf-group")), 4, "Leaf tiers missing")
        self.assertIsNotNone(loader.find("g", class_="top-canopy"), "Top canopy bud group missing")
        self.assertIsNotNone(loader.find(class_="loader-brand"), "Loader brand typography missing")

        # CTAs to all 3 modules
        hero_cta = soup.find("a", class_="cta-button")
        self.assertIsNotNone(hero_cta)
        self.assertEqual(hero_cta.get("href"), "/crop-recommendation")

        feature_ctas = [a.get("href") for a in soup.find_all("a", class_="cta-button")]
        self.assertIn("/crop-recommendation", feature_ctas)
        self.assertIn("/yield-prediction", feature_ctas)
        self.assertIn("/soil-health", feature_ctas)

        # Chatbot widget and scripts
        self.assertIsNotNone(soup.find(id="chat-widget"))
        self.assertIsNotNone(soup.find(id="chat-window"))
        self.assertIsNotNone(soup.find("script", src=lambda s: s and "chatbot.js" in s))

    def test_02_crop_recommendation_form_inputs_and_placeholders(self):
        """Verify /crop-recommendation inputs, submit CTA, and initial placeholder/disabled states."""
        res = self.client.get('/crop-recommendation')
        self.assertEqual(res.status_code, 200)
        soup = BeautifulSoup(res.data.decode('utf-8'), 'html.parser')

        expected_inputs = ["n", "p", "k", "temperature", "humidity", "ph", "rainfall"]
        for inp_id in expected_inputs:
            elem = soup.find(id=inp_id)
            self.assertIsNotNone(elem, f"Input field {inp_id} missing on crop recommendation page")

        analyze_btn = soup.find(id="analyzeBtn")
        self.assertIsNotNone(analyze_btn)
        self.assertEqual(analyze_btn.get("type"), "submit")

        placeholder = soup.find(id="placeholderContainer")
        results_div = soup.find(id="resultsContainer")
        self.assertIsNotNone(placeholder)
        self.assertIsNotNone(results_div)
        self.assertIn("hidden", results_div.get("class", []))

        # Downstream action buttons initially disabled
        self.assertTrue(soup.find(id="predictYieldBtn").has_attr("disabled"))
        self.assertTrue(soup.find(id="getSoilHealthBtn").has_attr("disabled"))
        self.assertTrue(soup.find(id="askChatbotBtn").has_attr("disabled"))

    def test_03_yield_prediction_dropdowns(self):
        """Verify /yield-prediction states, seasons, and crop dropdown options with friendly labels."""
        res = self.client.get('/yield-prediction')
        self.assertEqual(res.status_code, 200)
        soup = BeautifulSoup(res.data.decode('utf-8'), 'html.parser')

        state_select = soup.find("select", id="state")
        season_select = soup.find("select", id="season")
        crop_select = soup.find("select", id="crop")

        states = [opt.get("value") for opt in state_select.find_all("option") if opt.get("value")]
        seasons = [opt.get("value") for opt in season_select.find_all("option") if opt.get("value")]
        crops_map = {opt.get("value"): opt.text.strip() for opt in crop_select.find_all("option") if opt.get("value")}

        self.assertGreaterEqual(len(states), 30, "Expected at least 30 states")
        self.assertGreaterEqual(len(seasons), 4, "Expected standard cropping seasons")
        self.assertGreaterEqual(len(crops_map), 100, "Expected full yield crop classes")

        # Friendly label overrides verification
        self.assertEqual(crops_map.get("Gram"), "Chickpea (Gram)")
        self.assertEqual(crops_map.get("Water Melon"), "Watermelon / Melons")
        self.assertEqual(crops_map.get("Rice"), "Rice (Paddy)")
        self.assertEqual(crops_map.get("Cotton(lint)"), "Cotton")

    def test_04_soil_health_fields_and_categories(self):
        """Verify /soil-health soil parameters and categorized crop options."""
        res = self.client.get('/soil-health')
        self.assertEqual(res.status_code, 200)
        soup = BeautifulSoup(res.data.decode('utf-8'), 'html.parser')

        expected_fields = ["nitrogen", "phosphorous", "potassium", "temperature", "humidity", "cropType", "soilType", "moisture"]
        for field in expected_fields:
            self.assertIsNotNone(soup.find(id=field), f"Field {field} missing in soil health form")

        fert_crop_select = soup.find("select", id="cropType")
        crop_opts = {opt.get("value"): opt.text.strip() for opt in fert_crop_select.find_all("option") if opt.get("value")}

        expected_classes = ["Paddy", "Wheat", "Maize", "Barley", "Millets", "Pulses", "Ground Nuts", "Oil seeds", "Cotton", "Sugarcane", "Tobacco"]
        for exp_cls in expected_classes:
            self.assertIn(exp_cls, crop_opts, f"Fertilizer crop category {exp_cls} missing in dropdown")

    def test_05_api_health(self):
        """Verify /api/health returns success and all ML models loaded."""
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertTrue(data.get("all_models_loaded"))
        status = data.get("model_status", {})
        self.assertTrue(status.get("crop_model_loaded"))
        self.assertTrue(status.get("yield_model_loaded"))
        self.assertTrue(status.get("fertilizer_model_loaded"))
        self.assertTrue(status.get("crop_scaler_loaded"))
        self.assertTrue(status.get("yield_encoders_loaded"))

    def test_06_api_crop_taxonomy(self):
        """Verify /api/crop-taxonomy returns unified crop metadata."""
        res = self.client.get('/api/crop-taxonomy')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        metadata = data.get("data", {})
        self.assertEqual(len(metadata.get("recommendation_crops", {})), 22)
        self.assertEqual(len(metadata.get("fertilizer_categories", {})), 11)
        self.assertIn("Gram", metadata.get("yield_display_overrides", {}))

    # -------------------------------------------------------------------------
    # 2. Cross-Stage Redirect Workflows
    # -------------------------------------------------------------------------
    def test_07_scenario_a_rice_workflow(self):
        """Scenario A: Recommendation yields `rice` -> redirect to `/yield-prediction?crop=rice` -> 'Rice' selected -> valid yield."""
        # Step 1: Predict crop
        res_rec = self.client.post('/api/predict-crop', json={
            'n': 80, 'p': 40, 'k': 40,
            'temperature': 25.0, 'humidity': 80.0, 'ph': 6.5, 'rainfall': 200.0
        })
        self.assertEqual(res_rec.status_code, 200)
        crop_pred = res_rec.get_json().get("result", {}).get("crop")
        self.assertEqual(crop_pred, "rice")

        # Step 2: GET /yield-prediction?crop=rice
        res_page = self.client.get('/yield-prediction?crop=rice')
        self.assertEqual(res_page.status_code, 200)
        soup = BeautifulSoup(res_page.data.decode('utf-8'), 'html.parser')
        rice_opt = soup.find("option", value="Rice")
        self.assertIsNotNone(rice_opt)
        self.assertTrue(rice_opt.has_attr("selected"), "Option Rice must have selected attribute")

        # Step 3: Call /api/predict-yield
        res_yield = self.client.post('/api/predict-yield', json={
            'state': 'Andhra Pradesh', 'season': 'Kharif     ', 'crop': 'Rice', 'area': 2.5
        })
        self.assertEqual(res_yield.status_code, 200)
        result = res_yield.get_json().get("result", {})
        self.assertGreater(result.get("yield_per_hectare", 0), 0)
        self.assertGreater(result.get("total_yield", 0), 0)

    def test_08_scenario_b_muskmelon_workflow(self):
        """Scenario B: Recommendation yields `muskmelon` -> redirect to `/yield-prediction?crop=muskmelon` -> 'Water Melon' selected ('Watermelon / Melons')."""
        res_page = self.client.get('/yield-prediction?crop=muskmelon')
        self.assertEqual(res_page.status_code, 200)
        soup = BeautifulSoup(res_page.data.decode('utf-8'), 'html.parser')

        musk_opt = soup.find("option", value="Water Melon")
        self.assertIsNotNone(musk_opt)
        self.assertTrue(musk_opt.has_attr("selected"))
        self.assertEqual(musk_opt.text.strip(), "Watermelon / Melons")

        # Prediction test with resolved class
        res_yield = self.client.post('/api/predict-yield', json={
            'state': 'Uttar Pradesh', 'season': 'Summer     ', 'crop': 'Water Melon', 'area': 1.0
        })
        self.assertEqual(res_yield.status_code, 200)
        result = res_yield.get_json().get("result", {})
        self.assertGreater(result.get("yield_per_hectare", 0), 0)

    def test_09_scenario_c_chickpea_yield_workflow(self):
        """Scenario C: Recommendation yields `chickpea` -> redirect to `/yield-prediction?crop=chickpea` -> 'Gram' selected ('Chickpea (Gram)')."""
        res_page = self.client.get('/yield-prediction?crop=chickpea')
        self.assertEqual(res_page.status_code, 200)
        soup = BeautifulSoup(res_page.data.decode('utf-8'), 'html.parser')

        gram_opt = soup.find("option", value="Gram")
        self.assertIsNotNone(gram_opt)
        self.assertTrue(gram_opt.has_attr("selected"))
        self.assertEqual(gram_opt.text.strip(), "Chickpea (Gram)")

        # Prediction test with resolved class
        res_yield = self.client.post('/api/predict-yield', json={
            'state': 'Madhya Pradesh', 'season': 'Rabi       ', 'crop': 'Gram', 'area': 3.0
        })
        self.assertEqual(res_yield.status_code, 200)
        result = res_yield.get_json().get("result", {})
        self.assertGreater(result.get("yield_per_hectare", 0), 0)

    def test_10_scenario_d_chickpea_fertilizer_workflow(self):
        """Scenario D: Recommendation yields `chickpea` (N=40, P=60, K=80) -> redirect to `/soil-health?crop=chickpea...` -> 'Pulses' selected -> valid fertilizer."""
        res_page = self.client.get('/soil-health?crop=chickpea&nitrogen=40&phosphorous=60&potassium=80')
        self.assertEqual(res_page.status_code, 200)
        soup = BeautifulSoup(res_page.data.decode('utf-8'), 'html.parser')

        pulses_opt = soup.find("option", value="Pulses")
        self.assertIsNotNone(pulses_opt)
        self.assertTrue(pulses_opt.has_attr("selected"))

        # Predict fertilizer
        res_fert = self.client.post('/api/predict-fertilizer', json={
            'temperature': 26.0, 'humidity': 52.0, 'moisture': 38.0,
            'soilType': 'Loamy', 'cropType': 'Pulses',
            'nitrogen': 40.0, 'potassium': 80.0, 'phosphorous': 60.0
        })
        self.assertEqual(res_fert.status_code, 200)
        result = res_fert.get_json().get("result", {})
        self.assertTrue(bool(result.get("fertilizer")))
        self.assertGreater(result.get("confidence", 0), 0)

    def test_11_scenario_e_cotton_fertilizer_workflow(self):
        """Scenario E: Recommendation yields `cotton` -> redirect to `/soil-health?crop=cotton` -> 'Cotton' selected."""
        res_page = self.client.get('/soil-health?crop=cotton')
        self.assertEqual(res_page.status_code, 200)
        soup = BeautifulSoup(res_page.data.decode('utf-8'), 'html.parser')

        cotton_opt = soup.find("option", value="Cotton")
        self.assertIsNotNone(cotton_opt)
        self.assertTrue(cotton_opt.has_attr("selected"))

        # Predict fertilizer with Cotton
        res_fert = self.client.post('/api/predict-fertilizer', json={
            'temperature': 28.0, 'humidity': 60.0, 'moisture': 45.0,
            'soilType': 'Black', 'cropType': 'Cotton',
            'nitrogen': 80.0, 'potassium': 40.0, 'phosphorous': 40.0
        })
        self.assertEqual(res_fert.status_code, 200)
        result = res_fert.get_json().get("result", {})
        self.assertTrue(bool(result.get("fertilizer")))

    # -------------------------------------------------------------------------
    # 3. Static Assets Verification
    # -------------------------------------------------------------------------
    def test_12_static_assets_http_and_syntax(self):
        """Verify static CSS and JS assets return HTTP 200 and possess valid syntax."""
        static_assets = [
            "static/css/style.css",
            "static/js/crop_recommendation.js",
            "static/js/yield_prediction.js",
            "static/js/soil_health.js",
            "static/js/chatbot.js"
        ]

        for asset_path in static_assets:
            res = self.client.get(f"/{asset_path}")
            self.assertEqual(res.status_code, 200, f"Asset {asset_path} returned status {res.status_code}")
            self.assertGreater(len(res.data), 500, f"Asset {asset_path} unexpectedly small")
            res.close()

        # Run Node.js syntax check on all JS files
        js_files = [f for f in static_assets if f.endswith(".js")]
        node_cmd = ["node", "-c"] + js_files
        proc = subprocess.run(node_cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node.js syntax errors: {proc.stderr}")


def run_standalone():
    """Run tests with colored visual summary."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCropPulseE2EIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_standalone()
    sys.exit(0 if success else 1)
