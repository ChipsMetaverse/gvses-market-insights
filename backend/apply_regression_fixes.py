#!/usr/bin/env python3
"""Auto-generated script to apply regression fixes."""

import fileinput
import sys
from pathlib import Path

base_dir = Path(__file__).parent

# Apply fixes
fixes_applied = 0


# Fix: Reduce top_k default from 5 to 3
print("Applying: Reduce top_k default from 5 to 3")
file_path = base_dir / "services/vector_retriever.py"
with fileinput.FileInput(file_path, inplace=True) as file:
    for line in file:
        if "async def search_knowledge(self, query: str, top_k: int = 5" in line:
            print(line.replace("async def search_knowledge(self, query: str, top_k: int = 5", "async def search_knowledge(self, query: str, top_k: int = 3"), end='')
            fixes_applied += 1
        else:
            print(line, end='')

# Fix: Lower min_score from 0.7 to 0.65
print("Applying: Lower min_score from 0.7 to 0.65")
file_path = base_dir / "services/vector_retriever.py"
with fileinput.FileInput(file_path, inplace=True) as file:
    for line in file:
        if "min_score: float = 0.7" in line:
            print(line.replace("min_score: float = 0.7", "min_score: float = 0.65"), end='')
            fixes_applied += 1
        else:
            print(line, end='')

print(f"\n✅ Applied {fixes_applied} fixes")
print("Run tests to verify: python3 test_backward_compatibility.py")
