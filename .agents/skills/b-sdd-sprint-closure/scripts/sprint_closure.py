#!/usr/bin/env python3
"""
B-SDD Discrete Sprint Closure & Distillation Lifecycle Engine.
Executable runner for the @skill: b-sdd-sprint-closure.
"""
import sys
from pathlib import Path

# Locate b-sdd repository root
ROOT = Path("/home/vokov/projects/b-sdd")
sys.path.insert(0, str(ROOT))

from scripts.b_sdd_sprint_closure import main

if __name__ == "__main__":
    main()
