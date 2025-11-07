import csv
import json
import sys

def convert_value(key, value):
    if value is None:
        return None
    v = value.strip()
    if v == "\\N":
        return None
    # numeric fields to convert
    int_fields = {"startYear", "endYear", "runtimeMinutes", "numVotes"}
    float_fields = {"averageRating", "weightedRating"}
    if key in int_fields:
        try:
            return int(v)
        except Exception:
            return None
    if key in float_fields:
        try:
            return float(v)
        except Exception:
            return None
    return v


def tsv_to_json(in_path, out_path):
    with open(in_path, "r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in, delimiter="\t")
        rows = []
        for i, row in enumerate(reader, start=1):
            new_row = {}
            for k, v in row.items():
                new_row[k] = convert_value(k, v)
            rows.append(new_row)

    with open(out_path, "w", encoding="utf-8") as f_out:
        json.dump(rows, f_out, ensure_ascii=False, indent=2)

    print(f"Wrote {len(rows)} records to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tsv_to_json.py <input.tsv> <output.json>")
        sys.exit(1)
    tsv_to_json(sys.argv[1], sys.argv[2])
