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
codecarbon monitor > energy.log 2>&1 &
CARBON_PID=$!

# Ensure the monitor is always stopped on exit
trap 'kill -INT "$CARBON_PID" 2>/dev/null || true' EXIT

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

# Done
echo "Completed successfully"
echo "success" > failed.txt

# ─── Stop monitor & show report ────────────────────────────────────────────
# Send SIGINT so CodeCarbon flushes its log
kill -INT "$CARBON_PID" 2>/dev/null || true
wait "$CARBON_PID" 2>/dev/null || true

echo
echo "=== Energy Usage Report ==="
cat energy.log

exit 0

