#!/usr/bin/env python3
# ...existing code...
import json, urllib.request, urllib.error, argparse, sys

def get_json(url):
    with urllib.request.urlopen(url) as r:
        return json.load(r)

def post_json(url, obj):
    data = json.dumps(obj).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read().decode('utf-8')
            return r.getcode(), body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        return e.code, body

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--core', default='media_intermediate')
    p.add_argument('--file', default='intermediate_schema.json')
    p.add_argument('--solr', default='http://localhost:8983/solr')
    args = p.parse_args()

    try:
        schema_json = json.load(open(args.file))
    except Exception as e:
        print("Failed to read schema file:", e, file=sys.stderr)
        sys.exit(2)

    base = args.solr.rstrip('/') + '/' + args.core
    try:
        ft_resp = get_json(f'{base}/schema/fieldtypes?wt=json')
        existing_types = {ft['name'] for ft in ft_resp.get('fieldTypes', [])}
        f_resp = get_json(f'{base}/schema/fields?wt=json')
        existing_fields = {f['name'] for f in f_resp.get('fields', [])}
    except Exception as e:
        print("Failed to fetch existing schema info:", e, file=sys.stderr)
        sys.exit(2)

    def send(cmd_name, payload):
        code, body = post_json(f'{base}/schema', {cmd_name: payload})
        print(f'-> {cmd_name} {payload.get("name","(no-name)")} HTTP={code}')
        print(body[:2000])
        return code

    for ft in schema_json.get('add-field-type', []):
        name = ft.get('name')
        if not name:
            print("Skipping field-type without name", ft)
            continue
        if name in existing_types:
            print("Replacing field type:", name)
            send('replace-field-type', ft)
        else:
            print("Adding field type:", name)
            send('add-field-type', ft)

    for fld in schema_json.get('add-field', []):
        name = fld.get('name')
        if not name:
            print("Skipping field without name", fld)
            continue
        if 'type' not in fld:
            print(f"Field '{name}' missing 'type' — Solr requires a type. Skipping.", file=sys.stderr)
            continue
        if name in existing_fields:
            print("Replacing field:", name)
            send('replace-field', fld)
        else:
            print("Adding field:", name)
            send('add-field', fld)

    for key in ('add-copy-field','add-dynamic-field'):
        for item in schema_json.get(key, []):
            print(f"Posting {key}: {item}")
            post_json(f'{base}/schema', {key: item})

    print("Done.")

if __name__ == '__main__':
    main()