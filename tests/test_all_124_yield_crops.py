"""Test all 124 crops in the Yield Prediction model individually."""
import json
import pickle
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_app import app

def test_all_124_crops():
    client = app.test_client()
    yc = pickle.load(open('final_model/yield_crop_encoder.pkl', 'rb'))
    all_crops = list(yc.classes_)

    results = []
    failures = []

    print(f"Executing prediction for all {len(all_crops)} crops...")

    for idx, crop in enumerate(all_crops, 1):
        payload = {
            "state": "Maharashtra",
            "district": "PUNE",
            "season": "Kharif",
            "crop": crop,
            "area": 2.5
        }
        res = client.post('/api/predict-yield', data=json.dumps(payload), content_type='application/json')
        data = res.get_json()

        if res.status_code == 200 and data.get("success"):
            y_ha = data["result"]["yield_per_hectare"]
            tot = data["result"]["total_yield"]
            results.append((crop, y_ha, tot))
        else:
            failures.append((crop, res.status_code, data))

    print(f"Completed: {len(results)}/{len(all_crops)} passed.")
    if failures:
        print("Failures:", failures)
        assert False, f"{len(failures)} crops failed prediction!"
    else:
        print("100% of all 124 crops passed!")

if __name__ == '__main__':
    test_all_124_crops()
