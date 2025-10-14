import json, os
from pathlib import Path
from jsonschema import validate, ValidationError

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology"
SCHEMA_DIR = ROOT / "schemas"
OUTPUT_FILE = ROOT / "ontology_index.json"

def load_schema(schema_name):
    with open(SCHEMA_DIR / schema_name, "r") as f:
        return json.load(f)

def validate_entity(entity, schema):
    try:
        validate(instance=entity, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)

def build_index():
    index = {"entities": [], "relations": []}
    for layer_dir in ONTOLOGY_DIR.iterdir():
        if not layer_dir.is_dir():
            continue
        schema_file = f"{layer_dir.name}.schema.json"
        schema_path = SCHEMA_DIR / schema_file
        if not schema_path.exists():
            print(f"⚠️  No schema for {layer_dir.name}, skipping.")
            continue
        schema = load_schema(schema_file)
        for file in layer_dir.glob("*.json"):
            try:
                data = json.load(open(file))
            except Exception as e:
                print(f"❌ Error reading {file}: {e}")
                continue
            valid, err = validate_entity(data, schema)
            if not valid:
                print(f"❌ Validation error in {file}: {err}")
                continue
            index["entities"].append({
                "id": data["id"],
                "name": data["name"],
                "ontology": data["ontology"],
                "path": str(file.relative_to(ROOT))
            })
            # Collect symbolic and relational data
            if "synergies" in data:
                for target in data["synergies"]:
                    index["relations"].append({
                        "source": data["id"],
                        "target": target,
                        "relation": "synergy"
                    })
            if "relations" in data:
                for target in data["relations"]:
                    index["relations"].append({
                        "source": data["id"],
                        "target": target,
                        "relation": "link"
                    })
    with open(OUTPUT_FILE, "w") as f:
        json.dump(index, f, indent=2)
    print(f"✅ ontology_index.json built with {len(index['entities'])} entities.")

if __name__ == "__main__":
    build_index()
