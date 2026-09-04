import os
from pathlib import Path
from typing import List, Dict, Any, Optional

SRC_ROOT: str = "src"
TEST_ROOT: str = "tests"

def calculate_coverage_config(
    root: str = SRC_ROOT,
    pattern: str = "__tests__/**",
    base_thresholds: Dict[str, int] = None
) -> Dict[str, Any]:
    """
    Calculates the optimal coverage configuration for Vitest.
    Specifically designed to exclude files nested under a root's __tests__ directory
    to prevent inflating coverage totals by internal test logic.
    """
    if base_thresholds is None:
        base_thresholds = {
            "lines": 85,
            "functions": 75,
            "branches": 70,
            "statements": 85
        }

    # Determine the base glob for source files (typically .ts or .tsx)
    source_includes = [f"{root}/**/*.ts", f"{root}/**/*.tsx"]

    # The core fix: An explicit exclude for the nested __tests__ directory.
    # This targets directories like src/events/__tests__/ specifically.
    nested_test_glob = f"{root}/**/{pattern}"
    # Fallback if __tests__ is at the root level as well
    top_level_test_glob = f"{root}/{pattern}"

    exclude_paths: List[str] = [
        f"{root}/**/node_modules/**",    # Standard cleanup
        f"{root}/**/coverage/**",        # Exclude coverage artifact generation
        nested_test_glob,                # The specific bounty fix
    ]

    # Remove duplicates if root is specific (e.g., src/__tests__ vs src/**/__tests__)
    unique_excludes = list(dict.fromkeys(exclude_paths))

    config = {
        "coverage": {
            "include": source_includes,
            "exclude": unique_excludes,
            "extensions": [".ts", ".tsx", ".js"],
            "thresholds": base_thresholds,
            "reporter": ["text", "json", "html"]
        }
    }

    return config

def apply_config_overrides(config: Dict[str, Any]) -> None:
    """
    Mutates the config to handle edge cases like absolute paths or dynamic
    file extensions.
    """
    root = config.get("coverage", {}).get("include", ["src/**/*.ts"])[0]
    # Ensure the exclude logic matches the include logic
    root_path = Path(root)
    
    if root_path.suffix: # Handles cases where root itself has a suffix
         config["coverage"]["exclude"].append(f"{root_path}/**")
    
    # Re-evaluate the __tests__ exclusion logic
    config["coverage"]["exclude"] = [e for e in config["coverage"]["exclude"] if e]

def load_coverage_config(path: str = "src/coverage_config.py") -> Dict[str, Any]:
    """
    Utility to load or generate the coverage configuration.
    Acts as the bridge between Python logic and Vitest's TS config.
    """
    # In a TS setup, this might be imported dynamically.
    # For standalone Python operation:
    dynamic_config = calculate_coverage_config()
    return dynamic_config

# Main execution block to ensure syntax validity and runnable utility
if __name__ == "__main__":
    # Simulate running the logic to verify the fix
    final_config = load_coverage_config()
    
    # Log output for CI/CD debugging
    import json
    print(json.dumps(final_config, indent=2))

    # Optional: Auto-assign to environment variable for scripts
    import os
    os.environ["VITEST_COVERAGE_EXCLUDE"] = final_config["coverage"]["exclude"][0]