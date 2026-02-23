#!/usr/bin/env python3
"""Update import paths for Poetry Workspace restructuring."""

import re
from pathlib import Path

# Define import replacements
REPLACEMENTS = [
    # Core library imports (CLI and GUI packages)
    (r'from resource_fetcher\badapters', 'from resource_fetcher_core.adapters'),
    (r'from resource_fetcher\b\.core', 'from resource_fetcher_core.core'),
    (r'from resource_fetcher\b\.utils', 'from resource_fetcher_core.utils'),
    (r'import resource_fetcher\badapters', 'import resource_fetcher_core.adapters'),
    (r'import resource_fetcher\b\.core', 'import resource_fetcher_core.core'),
    (r'import resource_fetcher\b\.utils', 'import resource_fetcher_core.utils'),
    # Internal GUI imports
    (r'from resource_fetcher\.gui', 'from resource_fetcher_gui.gui'),
    (r'import resource_fetcher\.gui', 'import resource_fetcher_gui.gui'),
]

# Files to update (from agent analysis)
FILES_TO_UPDATE = [
    # CLI Package
    'packages/resource-fetcher-cli/src/resource_fetcher_cli/cli/main.py',
    'packages/resource-fetcher-cli/src/resource_fetcher_cli/__init__.py',
    # GUI Package
    'packages/resource-fetcher-gui/src/resource_fetcher_gui/gui/main.py',
    'packages/resource-fetcher-gui/src/resource_fetcher_gui/__init__.py',
    'packages/resource-fetcher-gui/src/resource_fetcher_gui/gui/core/cli_wrapper.py',
    'packages/resource-fetcher-gui/src/resource_fetcher_gui/gui/widgets/config_widget.py',
    'packages/resource-fetcher-gui/src/resource_fetcher_gui/gui/widgets/main_window.py',
    'packages/resource-fetcher-gui/src/resource_fetcher_gui/gui/widgets/progress_widget.py',
    'packages/resource-fetcher-gui/src/resource_fetcher_gui/gui/widgets/__init__.py',
]

def update_imports_in_file(file_path: Path) -> int:
    """Update imports in a single file. Returns number of changes made."""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return 0

    content = file_path.read_text(encoding='utf-8')
    original_content = content
    changes = 0

    for pattern, replacement in REPLACEMENTS:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            matches = len(re.findall(pattern, content))
            changes += matches
            print(f"  ✓ Applied: {pattern} → {replacement} ({matches} matches)")
            content = new_content

    if changes > 0:
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ Updated {file_path} ({changes} changes)")
    else:
        print(f"ℹ️  No changes needed for {file_path}")

    return changes

def main():
    """Update all import paths."""
    root = Path.cwd()
    total_changes = 0

    print("🔧 Updating import paths for Poetry Workspace restructuring...\n")

    for file_path_str in FILES_TO_UPDATE:
        file_path = root / file_path_str
        changes = update_imports_in_file(file_path)
        total_changes += changes

    print(f"\n✨ Complete! Total {total_changes} import paths updated.")

if __name__ == '__main__':
    main()
