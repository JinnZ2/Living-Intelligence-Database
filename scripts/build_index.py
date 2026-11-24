import json, os, sys
from pathlib import Path
from jsonschema import validate, ValidationError

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology"
SCHEMA_DIR = ROOT / "schemas"
OUTPUT_FILE = ROOT / "ontology_index.json"

# Schemas referenced by file name from the per-type schemas ($ref: "<name>").
SHARED_SCHEMAS = ("coordination.schema.json", "gate_sensing.schema.json",
                  "functional_intelligence.schema.json", "observation_context.schema.json",
                  "provenance.schema.json")

def load_schema(schema_name):
    schema_path = SCHEMA_DIR / schema_name
    with open(schema_path, "r") as f:
        return json.load(f)

def _shared_registry():
    """Registry for the shared schemas referenced by file name."""
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT7
    registry = Registry()
    for name in SHARED_SCHEMAS:
        registry = registry.with_resource(name, Resource(contents=load_schema(name), specification=DRAFT7))
    return registry

def validate_entity(entity, schema):
    try:
        from jsonschema import validators
        cls = validators.validator_for(schema)
        cls(schema, registry=_shared_registry()).validate(entity)
        return True, None
    except ValidationError as e:
        return False, str(e)

def build_index():
    index = {"entities": [], "relations": []}
    seen_ids = {}
    errors = 0

    for layer_dir in sorted(ONTOLOGY_DIR.iterdir()):
        if not layer_dir.is_dir():
            continue
        schema_file = f"{layer_dir.name}.schema.json"
        schema_path = SCHEMA_DIR / schema_file
        if not schema_path.exists():
            print(f"⚠️  No schema for '{layer_dir.name}', skipping validation for this directory.")
            continue
        schema = load_schema(schema_file)
        for file in sorted(layer_dir.glob("*.json")):
            try:
                with open(file, "r") as fh:
                    data = json.load(fh)
            except Exception as e:
                print(f"❌ Error reading {file}: {e}")
                errors += 1
                continue
            if not isinstance(data, dict):
                print(f"⚠️  Skipping {file}: root is not an object")
                continue
            if "id" not in data or "name" not in data:
                print(f"⚠️  Skipping {file}: missing required 'id' or 'name' field")
                continue

            # Check for duplicate IDs
            entity_id = data["id"]
            if entity_id in seen_ids:
                print(f"❌ Duplicate ID '{entity_id}' in {file} (first seen in {seen_ids[entity_id]})")
                errors += 1
                continue
            seen_ids[entity_id] = str(file.relative_to(ROOT))

            valid, err = validate_entity(data, schema)
            if not valid:
                print(f"❌ Validation error in {file}: {err}")
                errors += 1
                continue

            entry = {
                "id": data["id"],
                "name": data["name"],
                "ontology": data["ontology"],
                "path": str(file.relative_to(ROOT))
            }
            # Include description in index for AI navigability
            if "description" in data:
                entry["description"] = data["description"]
            # Include entropy_profile and substrate_layer for tool use
            if "entropy_profile" in data:
                entry["entropy_profile"] = data["entropy_profile"]
            if "substrate_layer" in data:
                entry["substrate_layer"] = data["substrate_layer"]

            index["entities"].append(entry)

            # Collect relational data from links array
            # Two link shapes exist: {relation, target} and {rel, to}. Read both.
            for link in data.get("links", []):
                target = link.get("target", link.get("to"))
                if target is not None:
                    index["relations"].append({
                        "source": data["id"],
                        "target": target,
                        "relation": link.get("relation", link.get("rel", "connected_to"))
                    })

    # Link integrity check
    all_ids = {e["id"] for e in index["entities"]}
    broken_links = []
    for rel in index["relations"]:
        if rel["target"] not in all_ids:
            broken_links.append(rel)

    if broken_links:
        print(f"\n⚠️  {len(broken_links)} broken link(s) (target not in index):")
        for bl in broken_links:
            print(f"   {bl['source']} --{bl['relation']}--> {bl['target']} (missing)")

    # Write index
    with open(OUTPUT_FILE, "w") as f:
        json.dump(index, f, indent=2)

    print(f"\n✅ ontology_index.json built with {len(index['entities'])} entities and {len(index['relations'])} relations.")

    if errors > 0:
        print(f"⚠️  {errors} error(s) encountered during build.")
        sys.exit(1)

if __name__ == "__main__":
    build_index()
