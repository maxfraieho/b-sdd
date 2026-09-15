#!/usr/bin/env python3
"""
B-SDD Utopia DB Synchronization Script.
Synchronizes all ADRs, System Components, and Procedural Skills to Utopia DB.
"""
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.cli.main import cmd_sync
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize B-SDD intents to Utopia DB")
    parser.add_argument("--kb", default="01a08474-0000-7000-8000-000000000001", help="Target Utopia Knowledge Base UUID")
    args = parser.parse_args()
    cmd_sync(args)
