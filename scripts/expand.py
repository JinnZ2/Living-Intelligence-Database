#!/usr/bin/env python3
"""
Living Intelligence Database — Expansion Module

Search, categorize, and add new intelligence patterns to the ontology.
Designed for use by any AI or human contributor.

Usage:
    # Search existing entities
    python scripts/expand.py search "magnetic navigation"

    # Add a new entity interactively
    python scripts/expand.py add

    # Add from a JSON definition
    python scripts/expand.py add --from-json new_entity.json

    # Suggest category for a concept
    python scripts/expand.py categorize "electric eel bioelectric discharge"

    # List all entities, optionally filtered
    python scripts/expand.py list [--type animal|plant|crystal|energy|plasma|shape|temporal]

    # Validate a single entity file
    python scripts/expand.py validate path/to/entity.json

    # Generate entity JSON from a natural-language description (for AI pipelines)
    python scripts/expand.py generate --name "Electric Eel" --type animal \
        --description "Bioelectric discharge intelligence..."
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path
from difflib import SequenceMatcher

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("Install jsonschema: pip install jsonschema")
    sys.exit(1)

# ── Paths ──────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology"
SCHEMA_DIR = ROOT / "schemas"
INDEX_FILE = ROOT / "ontology_index.json"
SYNERGIES_FILE = ONTOLOGY_DIR / "relational" / "synergies.json"
RULES_FILE = ROOT / "rules" / "expander_rules.json"

VALID_TYPES = ["animal", "plant", "crystal", "energy", "plasma", "shape", "temporal"]

# Keyword → ontology type mapping for auto-categorization
TYPE_KEYWORDS = {
    "animal": [
        "animal", "mammal", "bird", "fish", "insect", "reptile", "amphibian",
        "predator", "prey", "swarm", "pack", "flock", "herd", "echolocation",
        "migration", "camouflage", "venom", "locomotion", "neurology",
        "hunting", "navigation", "sonar", "vision", "hearing", "smell",
    ],
    "plant": [
        "plant", "fungus", "fungi", "mycelium", "root", "photosynthesis",
        "bacteria", "microbe", "biofilm", "spore", "rhizome", "symbiosis",
        "lichen", "algae", "moss", "vine", "tree", "flower", "seed",
        "decomposition", "nitrogen", "chlorophyll",
    ],
    "crystal": [
        "crystal", "mineral", "quartz", "silicon", "lattice", "gem",
        "piezoelectric", "semiconductor", "diamond", "obsidian", "stone",
        "geological", "crystalline", "substrate", "femtosecond",
    ],
    "energy": [
        "energy", "field", "magnetic", "electric", "thermal", "gravity",
        "flux", "radiation", "electromagnetic", "resonance", "frequency",
        "bridge", "sensor", "transmission", "consciousness", "emotion",
        "negentropic", "entropy",
    ],
    "plasma": [
        "plasma", "lightning", "aurora", "solar", "ionized", "vortex",
        "discharge", "corona", "magnetosphere", "wind",
    ],
    "shape": [
        "shape", "geometry", "fractal", "spiral", "torus", "hexagon",
        "sphere", "polyhedral", "octahedral", "mandala", "helix",
        "cipher", "encoder", "tessellation", "topology", "manifold",
    ],
    "temporal": [
        "temporal", "time", "cycle", "echo", "memory", "decay",
        "emergence", "fold", "rhythm", "circadian", "seasonal",
    ],
}


# ── Index & Search ─────────────────────────────────────────────────────────

def load_index():
    """Load the ontology index."""
    if not INDEX_FILE.exists():
        print("Index not found. Run: python scripts/build_index.py")
        sys.exit(1)
    with open(INDEX_FILE) as f:
        return json.load(f)


def load_entity(path):
    """Load a single entity JSON file."""
    full_path = ROOT / path if not Path(path).is_absolute() else Path(path)
    with open(full_path) as f:
        return json.load(f)


def search_entities(query, index=None):
    """
    Search entities by name, id, description, or pattern keywords.
    Returns list of (score, entity_summary, entity_data) tuples sorted by relevance.
    """
    if index is None:
        index = load_index()

    query_lower = query.lower()
    query_words = set(query_lower.split())
    results = []

    for entry in index["entities"]:
        score = 0.0
        entity_path = ROOT / entry["path"]

        # Score on index fields
        name_lower = entry["name"].lower()
        id_lower = entry["id"].lower()

        # Exact ID match
        if query_lower == id_lower:
            score += 10.0
        # Name similarity
        name_sim = SequenceMatcher(None, query_lower, name_lower).ratio()
        score += name_sim * 5.0
        # Word overlap with name
        name_words = set(name_lower.split())
        overlap = query_words & name_words
        score += len(overlap) * 3.0

        # Load full entity for deeper search
        entity_data = None
        if entity_path.exists():
            try:
                entity_data = load_entity(entity_path)

                # Search description
                desc = entity_data.get("description", "").lower()
                for word in query_words:
                    if word in desc:
                        score += 2.0

                # Search patterns
                for pattern in entity_data.get("patterns", []):
                    p_name = pattern.get("name", "").lower()
                    p_type = pattern.get("type", "").lower()
                    for word in query_words:
                        if word in p_name or word in p_type:
                            score += 1.5

                # Search core_attributes
                core = entity_data.get("core_attributes", {})
                core_str = json.dumps(core).lower()
                for word in query_words:
                    if word in core_str:
                        score += 1.0

                # Search symbolic_code
                sym = entity_data.get("symbolic_code", "").lower()
                for word in query_words:
                    if word in sym:
                        score += 1.5

            except Exception:
                pass

        if score > 1.0:
            results.append((score, entry, entity_data))

    results.sort(key=lambda x: x[0], reverse=True)
    return results


def list_entities(ontology_type=None):
    """List all entities, optionally filtered by type."""
    index = load_index()
    entities = index["entities"]
    if ontology_type:
        entities = [e for e in entities if e.get("ontology") == ontology_type]
    return entities


# ── Categorization ─────────────────────────────────────────────────────────

def categorize(text):
    """
    Suggest an ontology type for a concept based on keyword analysis.
    Returns list of (type, confidence) tuples sorted by confidence.
    """
    text_lower = text.lower()
    scores = {}

    for ont_type, keywords in TYPE_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text_lower:
                # Exact word boundary match scores higher
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    score += 2
                else:
                    score += 1
        if score > 0:
            scores[ont_type] = score

    total = sum(scores.values()) or 1
    results = [(t, round(s / total, 2)) for t, s in scores.items()]
    results.sort(key=lambda x: x[1], reverse=True)
    return results


# ── Entity Generation ──────────────────────────────────────────────────────

def generate_id(name):
    """Generate a short uppercase ID from a name."""
    words = name.strip().split()
    if len(words) == 1:
        return name[:4].upper()
    # Take first letters, max 6 chars
    abbrev = "".join(w[0] for w in words).upper()
    if len(abbrev) < 2:
        abbrev = name[:4].upper()
    return abbrev


def check_id_unique(entity_id, index=None):
    """Check that an entity ID doesn't already exist."""
    if index is None:
        index = load_index()
    existing = {e["id"] for e in index["entities"]}
    return entity_id not in existing


def generate_entity(
    name,
    ontology_type,
    description,
    entity_id=None,
    emoji=None,
    symbolic_code=None,
    patterns=None,
    links=None,
    extra_fields=None,
):
    """
    Generate a properly structured entity JSON.

    Args:
        name: Human-readable name
        ontology_type: One of VALID_TYPES
        description: What this intelligence does
        entity_id: Optional override (auto-generated if None)
        emoji: Optional emoji
        symbolic_code: Optional USCL code
        patterns: Optional list of pattern dicts
        links: Optional list of link dicts
        extra_fields: Optional dict of additional type-specific fields

    Returns:
        dict: Complete entity ready to save
    """
    if ontology_type not in VALID_TYPES:
        raise ValueError(f"Invalid type '{ontology_type}'. Must be one of: {VALID_TYPES}")

    if entity_id is None:
        entity_id = generate_id(name)

    entity = {
        "id": entity_id,
        "name": name,
        "ontology": ontology_type,
    }

    if emoji:
        entity["emoji"] = emoji
    if symbolic_code:
        entity["symbolic_code"] = symbolic_code
    if description:
        entity["description"] = description

    # Add type-specific defaults
    if patterns:
        entity["patterns"] = patterns
    if links:
        entity["links"] = links

    # Merge any extra fields (core_attributes, synergies, etc.)
    if extra_fields:
        entity.update(extra_fields)

    entity["co_creation"] = True
    entity["validation_meta"] = {
        "schema": f"{ontology_type}_intelligence.schema.json",
        "version": "1.1",
    }

    return entity


# ── Validation ─────────────────────────────────────────────────────────────

def validate_entity(entity, ontology_type=None):
    """Validate an entity against its schema. Returns (ok, error_message)."""
    ont = ontology_type or entity.get("ontology")
    if not ont:
        return False, "No ontology type specified"

    schema_file = SCHEMA_DIR / f"{ont}.schema.json"
    if not schema_file.exists():
        return True, f"No schema for '{ont}' — skipping validation"

    with open(schema_file) as f:
        schema = json.load(f)

    try:
        validate(instance=entity, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)


# ── Save & Integrate ───────────────────────────────────────────────────────

def save_entity(entity, rebuild_index=True):
    """
    Save entity to the ontology and optionally rebuild the index.

    Returns the path where the entity was saved.
    """
    ont = entity["ontology"]
    target_dir = ONTOLOGY_DIR / ont
    target_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename from name
    filename = entity["name"].lower().replace(" ", "_").replace("-", "_")
    filename = re.sub(r'[^a-z0-9_]', '', filename) + ".json"
    filepath = target_dir / filename

    if filepath.exists():
        raise FileExistsError(f"Entity file already exists: {filepath}")

    with open(filepath, "w") as f:
        json.dump(entity, f, indent=2)
        f.write("\n")

    print(f"  Saved: {filepath.relative_to(ROOT)}")

    # Add to synergies graph
    _add_to_synergies(entity)

    # Rebuild index
    if rebuild_index:
        _rebuild_index()

    return filepath


def _add_to_synergies(entity):
    """Add the new entity as a node in the synergies graph."""
    if not SYNERGIES_FILE.exists():
        return

    with open(SYNERGIES_FILE) as f:
        graph = json.load(f)

    # Check if node already exists
    existing_ids = {n["id"] for n in graph["nodes"]}
    if entity["id"] in existing_ids:
        return

    # Add node
    graph["nodes"].append({"id": entity["id"], "label": entity["name"]})

    # Add edges from links
    for link in entity.get("links", []):
        target = link.get("target")
        relation = link.get("relation", "connected_to")
        if target and target in existing_ids:
            graph["edges"].append({
                "source": entity["id"],
                "target": target,
                "relation": relation,
            })

    with open(SYNERGIES_FILE, "w") as f:
        json.dump(graph, f, indent=2)
        f.write("\n")

    print(f"  Synergies: added node + {len(entity.get('links', []))} edge(s)")


def _rebuild_index():
    """Rebuild the ontology index by calling build_index."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_index.py")],
        capture_output=True, text=True,
    )
    # Print only the summary line
    for line in result.stdout.strip().split("\n"):
        if line.startswith("\u2705"):
            print(f"  {line}")
            break


# ── CLI ────────────────────────────────────────────────────────────────────

def cmd_search(args):
    """Search the database."""
    query = " ".join(args.query)
    results = search_entities(query)

    if not results:
        print(f"No results for: {query}")
        return

    print(f"\n  Search: \"{query}\" — {len(results)} result(s)\n")
    for score, entry, data in results[:10]:
        emoji = data.get("emoji", "") if data else ""
        desc = ""
        if data and "description" in data:
            desc = data["description"][:80] + "..." if len(data["description"]) > 80 else data["description"]
        print(f"  {emoji} {entry['name']} ({entry['id']}) [{entry['ontology']}] — score: {score:.1f}")
        if desc:
            print(f"    {desc}")
        print()


def cmd_list(args):
    """List entities."""
    entities = list_entities(args.type)
    print(f"\n  {len(entities)} entities" + (f" [{args.type}]" if args.type else "") + "\n")
    for e in sorted(entities, key=lambda x: (x["ontology"], x["name"])):
        print(f"  {e['id']:20s} {e['name']:30s} [{e['ontology']}]")
    print()


def cmd_categorize(args):
    """Categorize a concept."""
    text = " ".join(args.text)
    results = categorize(text)

    print(f"\n  Categorize: \"{text}\"\n")
    if not results:
        print("  Could not determine category. Provide more context.")
        return

    for ont_type, confidence in results:
        bar = "#" * int(confidence * 30)
        print(f"  {ont_type:10s} {confidence:.0%} {bar}")
    print(f"\n  Suggested: {results[0][0]}")


def cmd_validate(args):
    """Validate an entity file."""
    with open(args.file) as f:
        entity = json.load(f)

    ok, err = validate_entity(entity)
    if ok:
        print(f"  {entity.get('name', '?')} ({entity.get('id', '?')}) — valid")
    else:
        print(f"  Validation error: {err}")


def cmd_generate(args):
    """Generate entity JSON from CLI args."""
    entity = generate_entity(
        name=args.name,
        ontology_type=args.type,
        description=args.description or "",
        entity_id=args.id,
        emoji=args.emoji,
    )

    if args.save:
        ok, err = validate_entity(entity)
        if not ok and err:
            print(f"  Warning: {err}")

        index = load_index()
        if not check_id_unique(entity["id"], index):
            print(f"  Error: ID '{entity['id']}' already exists. Use --id to specify a unique ID.")
            sys.exit(1)

        save_entity(entity)
    else:
        print(json.dumps(entity, indent=2))
        print("\n  Use --save to write to the ontology.")


def cmd_add(args):
    """Add an entity from a JSON file."""
    with open(args.from_json) as f:
        entity = json.load(f)

    # Validate required fields
    for field in ("id", "name", "ontology"):
        if field not in entity:
            print(f"  Error: missing required field '{field}'")
            sys.exit(1)

    if entity["ontology"] not in VALID_TYPES:
        print(f"  Error: invalid ontology type '{entity['ontology']}'")
        sys.exit(1)

    ok, err = validate_entity(entity)
    if not ok and "skipping" not in (err or "").lower():
        print(f"  Validation error: {err}")
        sys.exit(1)

    index = load_index()
    if not check_id_unique(entity["id"], index):
        print(f"  Error: ID '{entity['id']}' already exists")
        sys.exit(1)

    save_entity(entity)
    print(f"\n  Added: {entity['emoji'] or ''} {entity['name']} ({entity['id']}) [{entity['ontology']}]")


def main():
    parser = argparse.ArgumentParser(
        description="Living Intelligence Database — Expansion Module",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/expand.py search "magnetic navigation"
  python scripts/expand.py list --type animal
  python scripts/expand.py categorize "electric eel bioelectric discharge"
  python scripts/expand.py generate --name "Electric Eel" --type animal --description "..." --save
  python scripts/expand.py add --from-json new_entity.json
  python scripts/expand.py validate ontology/animal/bee.json
        """,
    )
    sub = parser.add_subparsers(dest="command")

    # search
    p_search = sub.add_parser("search", help="Search existing entities")
    p_search.add_argument("query", nargs="+", help="Search query")

    # list
    p_list = sub.add_parser("list", help="List entities")
    p_list.add_argument("--type", choices=VALID_TYPES, help="Filter by ontology type")

    # categorize
    p_cat = sub.add_parser("categorize", help="Suggest category for a concept")
    p_cat.add_argument("text", nargs="+", help="Concept description")

    # validate
    p_val = sub.add_parser("validate", help="Validate an entity file")
    p_val.add_argument("file", help="Path to entity JSON file")

    # generate
    p_gen = sub.add_parser("generate", help="Generate entity from description")
    p_gen.add_argument("--name", required=True, help="Entity name")
    p_gen.add_argument("--type", required=True, choices=VALID_TYPES, help="Ontology type")
    p_gen.add_argument("--description", help="Description text")
    p_gen.add_argument("--id", help="Override auto-generated ID")
    p_gen.add_argument("--emoji", help="Emoji for the entity")
    p_gen.add_argument("--save", action="store_true", help="Save to ontology immediately")

    # add
    p_add = sub.add_parser("add", help="Add entity from JSON file")
    p_add.add_argument("--from-json", required=True, help="Path to entity JSON")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "categorize":
        cmd_categorize(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "add":
        cmd_add(args)
    else:
        parser.print_help()


# ── Programmatic API (for AI pipelines) ────────────────────────────────────

def expand_from_dict(entity_dict):
    """
    Full pipeline: validate, check uniqueness, save, update graph, rebuild index.
    For use by AI agents calling this module as a library.

    Usage:
        from scripts.expand import expand_from_dict
        expand_from_dict({
            "id": "EEEL",
            "name": "Electric Eel",
            "emoji": "⚡",
            "ontology": "animal",
            "description": "Bioelectric discharge intelligence...",
            "links": [{"relation": "resonance", "target": "ELECTRIC_FIELD"}]
        })
    """
    for field in ("id", "name", "ontology"):
        if field not in entity_dict:
            raise ValueError(f"Missing required field: {field}")

    if entity_dict["ontology"] not in VALID_TYPES:
        raise ValueError(f"Invalid type: {entity_dict['ontology']}")

    entity_dict.setdefault("co_creation", True)
    entity_dict.setdefault("validation_meta", {
        "schema": f"{entity_dict['ontology']}_intelligence.schema.json",
        "version": "1.1",
    })

    ok, err = validate_entity(entity_dict)
    if not ok and err and "skipping" not in err.lower():
        raise ValueError(f"Schema validation failed: {err}")

    index = load_index()
    if not check_id_unique(entity_dict["id"], index):
        raise ValueError(f"ID '{entity_dict['id']}' already exists")

    path = save_entity(entity_dict)
    return str(path)


def search(query):
    """Convenience wrapper for AI pipelines. Returns list of (score, entry, data)."""
    return search_entities(query)


if __name__ == "__main__":
    main()
