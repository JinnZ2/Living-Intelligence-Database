#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
# pipeline.sh — Living Intelligence Database Pipeline
# Validates entities, rebuilds the index, and provides utility commands
# for adding new intelligences safely.
#
# Usage:
#   ./pipeline.sh              # Run full pipeline (validate + build index)
#   ./pipeline.sh validate     # Validate all entities against schemas
#   ./pipeline.sh build        # Rebuild ontology_index.json
#   ./pipeline.sh add <type>   # Scaffold a new entity (interactive)
#   ./pipeline.sh check <file> # Validate a single entity file
#   ./pipeline.sh list         # List all registered entities
#   ./pipeline.sh help         # Show this help message
# ─────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
ONTOLOGY_DIR="$ROOT/ontology"
SCHEMAS_DIR="$ROOT/schemas"
SCRIPTS_DIR="$ROOT/scripts"
INDEX_FILE="$ROOT/ontology_index.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ─── Helpers ────────────────────────────────────────────────────────

print_header() {
  echo ""
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${CYAN}  $1${NC}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

check_python() {
  if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is required but not found.${NC}"
    echo "Install Python 3 and try again."
    exit 1
  fi
}

check_jsonschema() {
  if ! python3 -c "import jsonschema" 2>/dev/null; then
    echo -e "${YELLOW}jsonschema not installed. Installing...${NC}"
    pip install jsonschema
  fi
}

# ─── Commands ───────────────────────────────────────────────────────

cmd_validate() {
  print_header "Validating all entities"
  check_python
  check_jsonschema

  local errors=0
  local valid=0
  local skipped=0

  for type_dir in "$ONTOLOGY_DIR"/*/; do
    [ -d "$type_dir" ] || continue
    local type_name
    type_name="$(basename "$type_dir")"
    local schema_file="$SCHEMAS_DIR/${type_name}.schema.json"

    if [ ! -f "$schema_file" ]; then
      echo -e "  ${YELLOW}[SKIP]${NC} No schema for '${type_name}'"
      skipped=$((skipped + 1))
      continue
    fi

    for entity_file in "$type_dir"*.json; do
      [ -f "$entity_file" ] || continue
      local filename
      filename="$(basename "$entity_file")"

      # Validate JSON syntax
      if ! python3 -c "import json; json.load(open('$entity_file'))" 2>/dev/null; then
        echo -e "  ${RED}[FAIL]${NC} ${type_name}/${filename} — invalid JSON"
        errors=$((errors + 1))
        continue
      fi

      # Validate against schema
      result=$(python3 -c "
import json, sys
from jsonschema import validate, ValidationError
with open('$entity_file') as f:
    data = json.load(f)
with open('$schema_file') as f:
    schema = json.load(f)
try:
    validate(instance=data, schema=schema)
    print('OK')
except ValidationError as e:
    print(f'FAIL: {e.message}')
" 2>&1)

      if [ "$result" = "OK" ]; then
        echo -e "  ${GREEN}[PASS]${NC} ${type_name}/${filename}"
        valid=$((valid + 1))
      else
        echo -e "  ${RED}[FAIL]${NC} ${type_name}/${filename}"
        echo -e "         ${result}"
        errors=$((errors + 1))
      fi
    done
  done

  echo ""
  echo -e "Results: ${GREEN}${valid} passed${NC}, ${RED}${errors} failed${NC}, ${YELLOW}${skipped} skipped${NC}"

  if [ "$errors" -gt 0 ]; then
    return 1
  fi
  return 0
}

cmd_build() {
  print_header "Building ontology index"
  check_python
  check_jsonschema

  python3 "$SCRIPTS_DIR/build_index.py"

  local count
  count=$(python3 -c "import json; print(len(json.load(open('$INDEX_FILE'))['entities']))")
  echo -e "${GREEN}Index rebuilt with ${count} entities.${NC}"
}

cmd_check() {
  local file="$1"

  if [ ! -f "$file" ]; then
    echo -e "${RED}Error: File not found: $file${NC}"
    exit 1
  fi

  print_header "Checking single entity"

  # Determine type from path
  local type_name
  type_name="$(basename "$(dirname "$file")")"
  local schema_file="$SCHEMAS_DIR/${type_name}.schema.json"

  if [ ! -f "$schema_file" ]; then
    echo -e "${RED}Error: No schema found for type '${type_name}'${NC}"
    echo "Expected schema at: $schema_file"
    exit 1
  fi

  # Validate
  python3 -c "
import json, sys
from jsonschema import validate, ValidationError
with open('$file') as f:
    data = json.load(f)
with open('$schema_file') as f:
    schema = json.load(f)

# Check required fields
for field in ['id', 'name', 'ontology']:
    if field not in data:
        print(f'Missing required field: {field}')
        sys.exit(1)

try:
    validate(instance=data, schema=schema)
    print('Entity is valid!')
    print(f'  ID:       {data[\"id\"]}')
    print(f'  Name:     {data[\"name\"]}')
    print(f'  Ontology: {data[\"ontology\"]}')
    links = data.get('links', [])
    print(f'  Links:    {len(links)} connection(s)')
except ValidationError as e:
    print(f'Validation failed: {e.message}')
    sys.exit(1)
"
}

cmd_add() {
  local type_name="${1:-}"

  # Show available types
  local valid_types=()
  for schema in "$SCHEMAS_DIR"/*.schema.json; do
    [ -f "$schema" ] || continue
    local t
    t="$(basename "$schema" .schema.json)"
    valid_types+=("$t")
  done

  if [ -z "$type_name" ]; then
    print_header "Add a new intelligence entity"
    echo ""
    echo "Available ontology types:"
    for t in "${valid_types[@]}"; do
      local count
      count=$(find "$ONTOLOGY_DIR/$t" -name "*.json" 2>/dev/null | wc -l)
      echo -e "  ${BLUE}${t}${NC} (${count} entities)"
    done
    echo ""
    echo -e "Usage: ${CYAN}./pipeline.sh add <type>${NC}"
    echo ""
    echo "Then create a JSON file in ontology/<type>/ with at minimum:"
    echo ""
    echo '  {'
    echo '    "id": "UNIQUE_ID",'
    echo '    "name": "Human-Readable Name",'
    echo '    "ontology": "<type>"'
    echo '  }'
    echo ""
    echo "Run './pipeline.sh check <file>' to validate before committing."
    return 0
  fi

  # Check type is valid
  local found=false
  for t in "${valid_types[@]}"; do
    if [ "$t" = "$type_name" ]; then
      found=true
      break
    fi
  done

  if [ "$found" = false ]; then
    echo -e "${RED}Error: Unknown type '${type_name}'${NC}"
    echo "Valid types: ${valid_types[*]}"
    exit 1
  fi

  # Interactive scaffold
  print_header "Scaffolding new ${type_name} entity"

  local target_dir="$ONTOLOGY_DIR/$type_name"
  mkdir -p "$target_dir"

  echo ""
  read -rp "Entity ID (UPPERCASE, e.g. WOLF): " entity_id
  read -rp "Entity name (e.g. Wolf Pack): " entity_name
  read -rp "Filename (snake_case, no .json): " filename
  read -rp "Description (one line): " entity_desc

  local filepath="$target_dir/${filename}.json"

  if [ -f "$filepath" ]; then
    echo -e "${RED}Error: File already exists: $filepath${NC}"
    exit 1
  fi

  cat > "$filepath" << ENTITY_EOF
{
  "id": "${entity_id}",
  "name": "${entity_name}",
  "ontology": "${type_name}",
  "description": "${entity_desc}",
  "core_attributes": {},
  "links": [],
  "co_creation": true,
  "validation_meta": {
    "schema": "${type_name}.schema.json",
    "version": "1.0"
  }
}
ENTITY_EOF

  echo ""
  echo -e "${GREEN}Created: $filepath${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Edit the file to add type-specific fields"
  echo "  2. Run: ./pipeline.sh check $filepath"
  echo "  3. Run: ./pipeline.sh build"
}

cmd_list() {
  print_header "All registered entities"
  check_python

  if [ ! -f "$INDEX_FILE" ]; then
    echo -e "${YELLOW}No index file found. Run './pipeline.sh build' first.${NC}"
    return 1
  fi

  python3 -c "
import json
with open('$INDEX_FILE') as f:
    data = json.load(f)

entities = data.get('entities', [])
by_type = {}
for e in entities:
    t = e.get('ontology', 'unknown')
    by_type.setdefault(t, []).append(e)

for t in sorted(by_type.keys()):
    items = by_type[t]
    print(f'\n  {t.upper()} ({len(items)} entities)')
    print('  ' + '-' * 40)
    for e in sorted(items, key=lambda x: x['name']):
        print(f'    {e[\"id\"]:20s} {e[\"name\"]}')

print(f'\n  Total: {len(entities)} entities')
"
}

cmd_help() {
  print_header "Living Intelligence Database Pipeline"
  echo ""
  echo "Commands:"
  echo ""
  echo -e "  ${CYAN}./pipeline.sh${NC}              Run full pipeline (validate + build)"
  echo -e "  ${CYAN}./pipeline.sh validate${NC}     Validate all entities against schemas"
  echo -e "  ${CYAN}./pipeline.sh build${NC}        Rebuild ontology_index.json"
  echo -e "  ${CYAN}./pipeline.sh add [type]${NC}   Scaffold a new entity interactively"
  echo -e "  ${CYAN}./pipeline.sh check <file>${NC} Validate a single entity file"
  echo -e "  ${CYAN}./pipeline.sh list${NC}         List all registered entities"
  echo -e "  ${CYAN}./pipeline.sh help${NC}         Show this help message"
  echo ""
  echo "Quick start — add a new intelligence:"
  echo ""
  echo "  1. ./pipeline.sh add ai"
  echo "  2. Edit the generated file with your entity data"
  echo "  3. ./pipeline.sh check ontology/ai/your_entity.json"
  echo "  4. ./pipeline.sh build"
  echo ""
}

# ─── Main ───────────────────────────────────────────────────────────

case "${1:-}" in
  validate)
    cmd_validate
    ;;
  build)
    cmd_build
    ;;
  check)
    if [ -z "${2:-}" ]; then
      echo -e "${RED}Usage: ./pipeline.sh check <file>${NC}"
      exit 1
    fi
    cmd_check "$2"
    ;;
  add)
    cmd_add "${2:-}"
    ;;
  list)
    cmd_list
    ;;
  help|--help|-h)
    cmd_help
    ;;
  "")
    # Full pipeline: validate then build
    cmd_validate && cmd_build
    ;;
  *)
    echo -e "${RED}Unknown command: $1${NC}"
    cmd_help
    exit 1
    ;;
esac
