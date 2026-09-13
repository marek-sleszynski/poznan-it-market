import json
from pathlib import Path
from pydantic import ValidationError
from poznan_it_market.ingest.models import RawOffer

file_path = Path("tmp/offers.json")
with open(file_path, encoding = "utf-8") as f:
  raw_data = json.load(f)
offers = raw_data.get("data", raw_data) if isinstance(raw_data, dict) else raw_data
accepted, rejected = 0, []
for item in offers:
  try:
    RawOffer.model_validate(item)
    accepted += 1
  except ValidationError as exc:
    rejected.append((item, exc))
    if len(rejected)<=5:
      print(exc.errors())
print(f"Total: {len(offers)} | Accepted: {accepted} | Rejected:{len(rejected)}")
if len(rejected)>0:
  print(f"{(len(rejected)/len(offers))*100:.2f}% rejected")
