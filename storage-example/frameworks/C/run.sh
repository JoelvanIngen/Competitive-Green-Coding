#!/bin/sh
echo "Creating empty files"
touch failed.txt compile_stdout.txt compile_stderr.txt run_stdout.txt run_stderr.txt

echo "Compiling"
if ! make > compile_stdout.txt 2> compile_stderr.txt; then
  echo "compile" > failed.txt
  exit 1
fi

echo "Running 500 iterations with offline tracker"
python3 - <<'PYCODE'
import subprocess, shlex
from codecarbon import OfflineEmissionsTracker

tracker = OfflineEmissionsTracker(country_iso_code="NLD",
                                  tracking_mode="process",
                                  output_file="emissions.csv")
tracker.start()
for i in range(5000):
    subprocess.run("./main < input.txt", shell=True)
tracker.stop()
PYCODE

if [ $? -ne 0 ]; then
  echo "runtime" > failed.txt
  exit 1
fi

echo "Completed successfully"
echo "success" > failed.txt
exit 0

