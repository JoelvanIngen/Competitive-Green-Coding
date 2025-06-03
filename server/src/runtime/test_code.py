import subprocess

# submitted_code.c is the code that user submitted
output_compile = subprocess.run(
    ["gcc", "-o", "program", "submitted_code.c"],
    stderr=subprocess.PIPE,
)

if output_compile.returncode != 0:
    raise RuntimeError(output_compile.stderr)

# Time the program
output_time = subprocess.run(
    ["/usr/bin/time", "./program"],
    capture_output=True,
    stderr=subprocess.PIPE,
    text=True
)

if output_time.returncode != 0:
    raise RuntimeError(output_time.stderr)

print("Timing info:")
print(output_time.stderr)
