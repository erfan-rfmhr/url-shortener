#!/usr/bin/env python3
"""Alembic migration wrapper script."""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Change to the alembic directory
alembic_dir = Path(__file__).parent / "database" / "revisions"
os.chdir(alembic_dir)

# Run alembic with the provided arguments
if __name__ == "__main__":
    from alembic.config import main

    main(argv=sys.argv[1:])
