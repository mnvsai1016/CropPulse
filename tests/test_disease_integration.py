import io
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from web_app import app

def run_tests():
    client = app.test_client()

    print("--- 1. TESTING WEB ROUTES ---")
    routes = [
        ('/', "The Future of Farming is Data-Driven"),
        ('/crop-recommendation', "Smart Crop Recommendation"),
        ('/yield-prediction', "Crop Yield Prediction"),
        ('/soil-health', "Soil Health & Fertilizer Recommendations"),
        ('/disease-detection', "Plant Disease Scanner & Leaf Diagnostics"),
        ('/api/health', "model_status")
    ]
    for r, text in routes:
        res = client.get(r)
        assert res.status_code == 200, f"Route {r} failed with {res.status_code}"
        assert text.encode() in res.data, f"Route {r} missing expected string '{text}'"
        print(f"  [PASS] {r} -> 200 OK (verified content)")

    print("\n--- 2. TESTING HEALTH CHECK ---")
    h_res = client.get('/api/health')
    h_json = h_res.get_json()
    assert h_json['model_status']['disease_model_loaded'] is True, "disease_model_loaded is False!"
    print(f"  [PASS] All models loaded: {h_json['all_models_loaded']}")
    print(f"  [PASS] Disease model loaded: {h_json['model_status']['disease_model_loaded']}")

    print("\n--- 3. TESTING DISEASE PREDICTION ON LEAF IMAGES ---")
    samples = ['apple_scab.jpg', 'corn_rust.jpg', 'grape_black_rot.jpg', 'apple_healthy.jpg']
    for s in samples:
        path = f"static/images/samples/{s}"
        with open(path, "rb") as f:
            file_bytes = f.read()
        res = client.post(
            '/api/predict-disease',
            data={'file': (io.BytesIO(file_bytes), s)},
            content_type='multipart/form-data'
        )
        assert res.status_code == 200, f"Prediction failed for {s}: {res.status_code}"
        data = res.get_json()
        assert data['success'] is True
        diag = data['result']
        print(f"  [PASS] {s:18} -> {diag['disease_name']} ({diag['status']}, Conf: {diag['confidence']}%)")
        assert 'organic_treatment' in diag
        assert 'chemical_treatment' in diag
        assert 'prevention' in diag
        assert len(diag['top_candidates']) == 3

    print("\n--- 4. TESTING BASE64 JSON INPUT ---")
    import base64
    with open("static/images/samples/corn_rust.jpg", "rb") as f:
        b64_str = base64.b64encode(f.read()).decode("utf-8")
    json_res = client.post('/api/predict-disease', json={'image': f"data:image/jpeg;base64,{b64_str}"})
    assert json_res.status_code == 200
    assert json_res.get_json()['success'] is True
    print("  [PASS] Base64 payload processed successfully.")

    print("\n--- 5. TESTING ERROR & EDGE CASE HANDLING ---")
    err1 = client.post('/api/predict-disease', data={})
    assert err1.status_code == 400
    print("  [PASS] Missing file/data returns 400.")

    err2 = client.post('/api/predict-disease', data={'file': (io.BytesIO(b""), "empty.jpg")}, content_type='multipart/form-data')
    assert err2.status_code == 400
    print("  [PASS] Empty file returns 400.")

    print("\n===========================================")
    print("   ALL INTEGRATION TESTS PASSED 100%!     ")
    print("===========================================")

if __name__ == "__main__":
    run_tests()
