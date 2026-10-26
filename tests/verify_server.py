import urllib.request
import json

def test_url(url, method='GET', data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read()

print("=" * 65)
print("     ThreatText AI - Localhost Server Integration Verification")
print("=" * 65)

# 1. Test Static Assets
assets = [
    '/',
    '/css/style.css',
    '/js/app.js',
    '/results/confusion_matrix.png',
    '/results/model_comparison_bar.png',
    '/results/roc_curves.png',
    '/data/sample_batch.csv'
]
for path in assets:
    status, content = test_url(f'http://127.0.0.1:8000{path}')
    print(f"Asset {path:<32} -> Status {status} ({len(content):,} bytes)")

# 2. Test JSON APIs
apis = [
    '/api/status',
    '/api/dataset-stats',
    '/api/samples',
    '/api/benchmarks',
    '/api/global-features',
    '/api/report'
]
for api in apis:
    status, content = test_url(f'http://127.0.0.1:8000{api}')
    if api == '/api/report':
        print(f"API {api:<34} -> Status {status} (Report text: {len(content):,} bytes)")
    else:
        data = json.loads(content.decode('utf-8'))
        if isinstance(data, list):
            print(f"API {api:<34} -> Status {status} (List of {len(data)} items)")
        else:
            print(f"API {api:<34} -> Status {status} (Keys: {list(data.keys())[:4]})")

# 3. Test POST /api/analyze
analyze_payload = json.dumps({
    'subject': 'URGENT: Suspicious activity on your bank portal',
    'body': 'Dear customer, your bank account access has been restricted. Click here to verify password immediately.',
    'model': 'logistic_regression'
}).encode('utf-8')
status, content = test_url(
    'http://127.0.0.1:8000/api/analyze',
    method='POST',
    data=analyze_payload,
    headers={'Content-Type': 'application/json'}
)
res = json.loads(content.decode('utf-8'))
triggers = [t['phrase'] for t in res['top_phishing_indicators'][:4]]
print(f"POST /api/analyze                 -> Status {status} | Prediction: {res['prediction']} | Score: {res['risk_score_percent']}% | Triggers: {triggers}")

# 4. Test POST /api/batch
batch_payload = json.dumps({
    'csv_data': 'id,email_text\n1,"Urgent: your account is suspended. Verify password at http://fake.com"\n2,"Team, attached is the meeting agenda for our architecture review."\n',
    'model': 'logistic_regression'
}).encode('utf-8')
status, content = test_url(
    'http://127.0.0.1:8000/api/batch',
    method='POST',
    data=batch_payload,
    headers={'Content-Type': 'application/json'}
)
batch_res = json.loads(content.decode('utf-8'))
print(f"POST /api/batch                   -> Status {status} | Analyzed: {batch_res['total_analyzed']} | Phishing: {batch_res['phishing_detected']} | Legit: {batch_res['legitimate_detected']}")

print("\n" + "=" * 65)
print("  >>> ALL HTTP ENDPOINTS AND STATIC ASSETS 100% OPERATIONAL! <<<")
print("=" * 65)
