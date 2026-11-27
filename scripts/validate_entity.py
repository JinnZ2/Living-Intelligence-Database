#!/usr/bin/env python3
"""validate_entity.py -- validate one entity file against one schema, for pipeline.sh.

    python3 scripts/validate_entity.py <entity.json> <schema.json>            print OK, or FAIL: <reason>
    python3 scripts/validate_entity.py --report <entity.json> <schema.json>   pipeline.sh check output

Added 2026-11-24 (fixture F7 in validation/fixtures/DECLARED.json). $refs by bare file name
(coordination.schema.json, ...) are resolved with the same registry scripts/build_index.py uses,
so pipeline.sh and the index build validate the same way.

Exit 0 = valid. Exit 1 = invalid, with every error printed (path and message). Exit 2 = the
validator could not run (unresolvable $ref, unreadable file, ...), with the exception type and text.
Nothing is skipped and nothing is normalised.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main(argv):
    report = argv[:1] == ["--report"]
    if report:
        argv = argv[1:]
    if len(argv) != 2:
        print("FAIL: usage: validate_entity.py [--report] <entity.json> <schema.json>")
        return 2
    entity_path, schema_path = argv
    try:
        from jsonschema import validators
        from build_index import _shared_registry
        data = json.loads(Path(entity_path).read_text())
        schema = json.loads(Path(schema_path).read_text())
        if report:
            for field in ("id", "name", "ontology"):
                if field not in data:
                    print(f"Missing required field: {field}")
                    return 1
        cls = validators.validator_for(schema)
        errors = sorted(cls(schema, registry=_shared_registry()).iter_errors(data),
                        key=lambda e: [str(p) for p in e.absolute_path])
    except Exception as e:  # the validator could not run: say what and why
        print(f"FAIL: {type(e).__name__}: {e}")
        return 2
    if errors:
        print(f"FAIL: {len(errors)} validation error(s)")
        for e in errors:
            where = "/".join(str(p) for p in e.absolute_path) or "(root)"
            print(f"  at {where}: {e.message}")
        return 1
    if report:
        print("Entity is valid!")
        print(f"  ID:       {data['id']}")
        print(f"  Name:     {data['name']}")
        print(f"  Ontology: {data['ontology']}")
        print(f"  Links:    {len(data.get('links', []))} connection(s)")
    else:
        print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
