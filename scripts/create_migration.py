#!/usr/bin/env python
import sys
import os
from alembic import command
from alembic.config import Config

def create_migration(message):
    """Create a new migration with the given message"""
    # Get the directory containing this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Navigate to project root
    os.chdir(os.path.join(dir_path, '..'))
    
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    # Create the migration
    command.revision(alembic_cfg, 
                    message=message, 
                    autogenerate=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_migration.py \"migration message\"")
        sys.exit(1)
    
    create_migration(sys.argv[1]) 