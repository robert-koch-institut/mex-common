import json
import os
import re
from collections import defaultdict


# Helper function to recursively search for $ref keys in nested JSON
def find_references_in_jsons(ref_pattern, obj):
    """Find References to other models in the jsons by search term."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str):
                match = ref_pattern.search(value)
                if (
                    match
                    and match.group(1) != "concept"
                    and match.group(1) != "concept-scheme"
                ):
                    yield match.group(1)
            else:
                yield from find_references_in_jsons(ref_pattern, value)
    elif isinstance(obj, list):
        for item in obj:
            yield from find_references_in_jsons(ref_pattern, item)


schema_dir = r".venv\Lib\site-packages\mex\model\entities"
references = set()


# helper function to detect circles in references
def detect_and_sort_with_breaking(pairs):
    """Remove circles from references, keeping PrimarySource always first."""
    graph = defaultdict(set)
    nodes = set()
    for a, b in pairs:
        graph[a].add(b)
        nodes.update([a, b])

    visited = {}
    result = []
    cycle = []

    def dfs(node, stack):
        if node in visited:
            return visited[node]  # True if fully processed, False if cycle
        visited[node] = False
        stack.append(node)
        for neighbor in graph[node]:
            # Skip self-referencing edges that don't affect the sorting order
            if neighbor == node:
                continue
            if neighbor in stack:
                cycle.extend(stack[stack.index(neighbor) :] + [neighbor])
                return False
            if not dfs(neighbor, stack):
                return False
        visited[node] = True
        result.append(node)
        stack.pop()
        return True

    # First run through to detect cycles
    for node in nodes:
        if node not in visited and not dfs(node, []):
            break  # Cycle detected

    # Now break cycles (we remove edges that caused cycles)
    if cycle:
        print("Cycle detected:", " → ".join(cycle))

        # Remove the first edge that created the cycle
        cycle_set = set(cycle)
        for a, b in pairs:
            if a in cycle_set and b in cycle_set:
                # Skip edges where "primary-source" is the first node in the edge
                if a == "primary-source":
                    continue
                # Remove edges with "primary-source" as the second node
                if b == "primary-source":
                    pairs.remove((a, b))
                    print(f"Removed edge: ({a}, {b}) to break the cycle")
                    break  # Break after removing one edge

        # Retry sorting with the removed edge
        return detect_and_sort_with_breaking(pairs)  # Retry after breaking the cycle

    return result[::-1], None  # Return sorted order if no cycle


def get_models_in_order_of_dependency():
    """Get model order such that models with no dependencies come first."""
    ref_pattern = re.compile(r"\/schema\/entities\/(.+?)#")

    # Walk through each JSON file (source) and find References (Targets)
    for filename in os.listdir(schema_dir):
        if (
            filename.endswith(".json")
            and filename != "concept.json"
            and filename != "concept-scheme.json"
        ):
            source = os.path.splitext(filename)[0]
            with open(os.path.join(schema_dir, filename), encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for target in find_references_in_jsons(ref_pattern, data):
                        references.add((target, source))
                except json.JSONDecodeError as e:
                    print(f"Error parsing {filename}: {e}")

    # remove circles of dependencies
    ordered_dependencies = detect_and_sort_with_breaking(list(references))[0]

    # return list of Model classes in order of dependencies (no dependencies = first)
    return [
        "Extracted" + "".join(part.capitalize() for part in s.split("-"))
        for s in ordered_dependencies
    ]
