#!/bin/sh

# Touch all files to prevent errors in Engine
echo "Creating empty files"
touch failed.txt compile_stdout.txt compile_stderr.txt run_stdout.txt run_stderr.txt

# ─── Start energy monitoring ───────────────────────────────────────────────
echo "Starting energy monitor (CodeCarbon)…"
codecarbon monitor &
CARBON_PID=$!

# Ensure CodeCarbon is stopped on exit
trap 'kill -INT "$CARBON_PID" 2>/dev/null || true' EXIT

# ─── Compile ────────────────────────────────────────────────────────────────
echo "Compiling"
if ! make 1> compile_stdout.txt 2> compile_stderr.txt; then
  echo "compile" > failed.txt
  exit 1
fi

# ─── Run the program 100 times under the same monitor ───────────────────────
echo "Running 100 iterations"
i=0
while [ $i -lt 100 ]; do
  i=$((i+1))
  echo "  Iteration #$i"
  if ! ./main < input.txt > run_stdout.txt 2> run_stderr.txt; then
    echo "runtime" > failed.txt
    exit 1
  fi
done

# ─── Mark success ──────────────────────────────────────────────────────────
echo "Completed successfully"
echo "success" > failed.txt

# ─── Stop the monitor and exit ─────────────────────────────────────────────
kill -INT "$CARBON_PID" 2>/dev/null || true
wait "$CARBON_PID" 2>/dev/null || true

exit 0

