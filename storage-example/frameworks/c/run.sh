#!/bin/sh

# Touch all files to prevent errors in Engine
echo "Creating empty files"
touch failed.txt compile_stdout.txt compile_stderr.txt run_stdout.txt run_stderr.txt

# Compile
echo "Compiling"
if ! make > compile_stdout.txt 2> compile_stderr.txt
then
  echo "compile" > failed.txt
  exit 1
fi

# Run the program with input
echo "Running"
if ! ./main < input.txt > run_stdout.txt 2> run_stderr.txt
then
  echo "runtime" > failed.txt
  exit 1
fi


# Running measurements
echo "Measuring"
python3 - <<'PYCODE'
import subprocess, shlex, time
from codecarbon import OfflineEmissionsTracker

tracker = OfflineEmissionsTracker(country_iso_code="NLD",
                                  tracking_mode="process",
                                  output_file="emissions.csv")

# Measurement
tracker.start()
for i in range(1000):
    subprocess.run("./main < input.txt", shell=True)
tracker.stop()
PYCODE




# Does not actually fail, just so we don't get errors looking for the `failed.txt` file
echo "Completed successfully"
echo "success" > failed.txt

exit 0