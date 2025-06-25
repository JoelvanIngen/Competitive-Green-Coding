#!/bin/sh

# Touch all files to prevent errors in Engine
echo "Creating empty files"
touch failed.txt
touch compile_stdout.txt
touch compile_stderr.txt
touch run_stdout.txt
touch run_stderr.txt

# ─── Start energy monitoring ───────────────────────────────────────────────
echo "Starting energy monitor (CodeCarbon)…"
python3 -m codecarbon.cli > energy.log 2>&1 &
CARBON_PID=$!
# Ensure the monitor is killed when this script exits
trap 'echo "Stopping energy monitor…"; kill $CARBON_PID 2>/dev/null || true' EXIT

# Compile
echo "Compiling"
if ! make 1> compile_stdout.txt 2> compile_stderr.txt
then
  echo "compile" > failed.txt
  exit 1
fi

# Run the program with input
echo "Running"
if ! ./program < input.txt > run_stdout.txt 2> run_stderr.txt
then
  echo "runtime" > failed.txt
  exit 1
fi

# Does not actually fail, just so we don't get errors looking for the `failed.txt` file
echo "Completed successfully"
echo "success" > failed.txt

# ─── Stop monitor & show report ────────────────────────────────────────────
echo "Stopping energy monitor…"
kill "$CARBON_PID" 2>/dev/null || true
wait "$CARBON_PID" 2>/dev/null || true

echo
echo "Energy Usage Report"
cat energy.log
