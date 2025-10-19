import json

train_data = None
print("loading train data")
with open("rolling-stock.json", "r") as file:
    train_data = json.loads(file.read())