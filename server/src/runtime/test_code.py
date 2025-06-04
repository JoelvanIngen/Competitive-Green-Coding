import subprocess

# Read the submitted code from a file named 'submitted_code.c'
output_compile = subprocess.run(
    ["gcc", "-o", "program", "submitted_code.c"],
    stderr=subprocess.PIPE,
    text=True
)

# Check if the compilation was successful
if output_compile.returncode != 0:
    print(f"Compilation failed:\n{output_compile.stderr}")
    exit(1)

# If compilation is successful, run the program with input from input.txt
# and measure the CPU time using the /usr/bin/time command
try:
    with open("input.txt", "r") as stdin:
        output_time = subprocess.run(
            ["/usr/bin/time", "-f", "%U", "./program"],
            stdin=stdin,
            capture_output=True,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2
        )

# Handle exceptions
except Exception as e:
    print(f"Unexpected error: {e}")
    exit(1)

# Check if the program ran successfully
if output_time.returncode != 0:
    print(
        "Program execution failed with return code "
        + f"{output_time.returncode}:\n{output_time.stderr}"
    )
    exit(1)

# Extract CPU time from the stderr output of the time command
cpu_time = output_time.stderr.strip()

# Print output and CPU time
print("Program Output:")
print(output_time.stdout.strip())
print("CPU Time (user):", cpu_time)
