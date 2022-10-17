import json

with open("./api_rahasia/api_konfig.json", "r") as file_json:
    data = json.load(file_json)
    KUNCI_API = data["EXCHANGE"]["BINANCE"]["KUNCI_API"]
    RAHASIA_API = data["EXCHANGE"]["BINANCE"]["RAHASIA_API"]
    
print(f"KUNCI_API: {KUNCI_API}")
print(f"RAHASIA_API: {RAHASIA_API}")

