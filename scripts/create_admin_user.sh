# In case the script is called from different folder, finds own folder
OWN_DIR=$(dirname "$(readlink -f "$0")")

PROJECT_ROOT=$(dirname "$OWN_DIR")

cd "$PROJECT_ROOT" || { echo "ERROR: 'cd' failed"; exit 1; }

# TODO: Call correct file when it exists
if ! docker exec db_handler python create_admin.py
then
  echo "ERROR: Docker compose exited with non-zero exit code";
  exit 1;
fi

echo "INFO: Created admin user, done."
