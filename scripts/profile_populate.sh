# scripts/profile_populate.sh
#!/bin/bash

if ! docker exec db_handler python -m scripts.profile_populator; then
  echo "ERROR: profile_populator exited with non-zero status"
  exit 1
fi

echo "INFO: Populated DB for profile endpoint."
