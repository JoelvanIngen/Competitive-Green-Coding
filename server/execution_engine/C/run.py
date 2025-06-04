import subprocess

# Read the submitted code from a file named 'submitted_code.c'
output_compile = subprocess.run(
    ["gcc", "-o", "program", "submitted_code.c"],
    stderr=subprocess.PIPE,
    text=True
)

# Check if the compilation was successful
if output_compile.returncode != 0:
    with open("stderr.txt", "w") as f:
        f.write("Compilation failed:\n" + output_compile.stderr)
    exit(1)


# If compilation is successful, run the program with input from input.txt
# and measure the CPU time using the /usr/bin/time command
try:
    with open("input.txt", "r") as stdin, \
         open("stdout.txt", "w") as stdout, \
         open("stderr.txt", "w") as stderr:

        subprocess.run(
            ["/usr/bin/time", "-v", "./program"],
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            text=True,
            timeout=2
        )

# Handle timeout exception
except subprocess.TimeoutExpired:
    with open("stderr.txt", "a") as f:
        f.write("Program timed out.\n")
    exit(1)
    
# Handle other exceptions
except Exception as e:
    with open("stderr.txt", "a") as f:
        f.write(f"Unexpected error: {e}\n")
    exit(1)