# Compile the program with all warnings and optimisations
# TODO: Create makefile and include skeleton code in compilation when we decide on skeleton code format
make 1> compile_stdout.txt 2> compile_stderr.txt

# Check for compilation errors
if [ $? -ne 0 ]
then
    echo "Compilation failed." >> compile_stderr.txt
    exit 1
fi

# Run the program with input
timeout 2s /usr/bin/time -v ./program < input.txt > run_stdout.txt 2> run_stderr.txt

# Check for timeout
if [ $? -eq 124 ]
then
    echo "Program timed out." >> run_stderr.txt
    exit 1
fi

exit 0