import base64
import hashlib
import hmac
import json
import requests

data_to_hash = "49577026-146d-45d5-9dec-2745f4cab09d"
key = "ed2e7ba5-4f99-4007-83a2-dbff82621e8e"

def calculate_hmac(data, key):
    hashed_object = hmac.new(key, data, hashlib.sha256).digest()
    return base64.b64encode(hashed_object)


hmac_hash = calculate_hmac(data_to_hash.encode(), key.encode())
# Example structure from API doc


def new_payment(data, myuuid):
    data = json.dumps(data)
    s = requests.Session()
    print(key)
    print(data)
    print(data_to_hash)
    req = requests.Request('POST', "https://api.sandbox.paynow.pl/v1/payments",
                           {'Api-key': key, "Signature": calculate_hmac(data.encode(), data_to_hash.encode()),
                            'Idempotency-Key': str(myuuid), 'Accept': '*/*', 'Content-Type': 'application/json'},
                           data=data).prepare()
    r = s.send(req)
    return (json.loads(r.text))


def check_payment(payment_id):
    s = requests.Session()
    req = requests.Request('GET', "https://api.sandbox.paynow.pl/v1/payments/{}/status".format(payment_id),
                           {'Api-key': key, 'Accept': '*/*', 'Content-Type': 'application/json'}).prepare()
    r = s.send(req)
    return (json.loads(r.text))

# def check_payment(payment_id):
#     s = requests.Session()
#     req = requests.Request('GET', f"https://api.sandbox.paynow.pl/v1/payments/{payment_id}/status",
#                            headers={
#                                'Api-key': key,
#                                'Accept': '*/*',
#                                'Content-Type': 'application/json'
#                            }).prepare()
#     r = s.send(req)
    
#     print("STATUS CODE:", r.status_code)
#     print("RESPONSE TEXT:", r.text)

#     try:
#         return json.loads(r.text)
#     except json.JSONDecodeError:
#         return {"status": "ERROR", "raw": r.text, "error": "Nieprawidłowy JSON"}
