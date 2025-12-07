#!/usr/bin/env python3
import json, ast, pathlib, re

IN = pathlib.Path(__file__).resolve().parents[1] / "final_data_solr" / "movies_series.json"
OUT = pathlib.Path(__file__).resolve().parents[1] / "final_data_solr" / "movies_series_fixed.json"

def parse_cast(val):
    names = []
    if isinstance(val, list):
        for item in val:
            if isinstance(item, (list, tuple)) and item:
                actor = str(item[0]).strip()
                role = str(item[1]).strip() if len(item) > 1 else ""
            elif isinstance(item, str):
                # try to parse "Actor - Role" or tuple-like strings
                m = re.match(r"^\s*['\"]?(?P<a>[^'\",]+?)['\"]?\s*(?:,|\-|\(|:)\s*['\"]?(?P<r>.+?)['\"]?\s*$", item)
                if m:
                    actor = m.group("a").strip(); role = m.group("r").strip()
                else:
                    actor = item.strip(); role = ""
            else:
                continue
            if actor:
                names.append(actor)
                if role:
                    names.append(f"{actor} - {role}")
    elif isinstance(val, str):
        # try to eval python-like list of tuples
        try:
            parsed = ast.literal_eval(val)
            for item in parsed:
                if isinstance(item, (list, tuple)) and item:
                    actor = str(item[0]).strip()
                    role = str(item[1]).strip() if len(item) > 1 else ""
                else:
                    actor = str(item).strip(); role = ""
                if actor:
                    names.append(actor)
                    if role:
                        names.append(f"{actor} - {role}")
        except Exception:
            # fallback: split on '),'
            s = val.strip().strip('[]')
            parts = [p.strip() for p in s.split("),") if p.strip()]
            for p in parts:
                m = re.findall(r"'([^']*)'|\"([^\"]*)\"", p)
                extracted = [t[0] if t[0] else t[1] for t in m]
                if extracted:
                    actor = extracted[0].strip()
                    role = extracted[1].strip() if len(extracted) > 1 else ""
                    names.append(actor)
                    if role:
                        names.append(f"{actor} - {role}")
    return names

def split_genres(g):
    if g is None:
        return []
    if isinstance(g, list):
        out = []
        for e in g:
            out += [x.strip() for x in str(e).split(",") if x.strip()]
        return out
    if isinstance(g, str):
        return [x.strip() for x in g.split(",") if x.strip()]
    return []

def main():
    docs = json.loads(IN.read_text())
    out = []
    for d in docs:
        if "top_3_cast" in d:
            d["top_3_cast"] = parse_cast(d["top_3_cast"])
        if "genres" in d:
            d["genres"] = split_genres(d["genres"])
        out.append(d)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print("Wrote", OUT)

if __name__ == "__main__":
    main()