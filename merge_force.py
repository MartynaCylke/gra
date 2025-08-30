import json
import glob

def merge_force_records(output_file="force.json"):
    # znajdź wszystkie pliki force_record_*.json
    files = glob.glob("force_record_*.json")

    merged = []
    for file in files:
        with open(file, "r") as f:
            data = json.load(f)
            merged.extend(data)

    # zapisz połączone dane do force.json
    with open(output_file, "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f"Scalono {len(files)} plików do {output_file} (łącznie {len(merged)} zdarzeń).")

if __name__ == "__main__":
    merge_force_records()
