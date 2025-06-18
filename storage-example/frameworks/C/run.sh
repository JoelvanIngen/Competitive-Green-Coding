# Compile the program with all warnings and optimisations and check for compilation errors
if ! make 1> compile_stdout.txt 2> compile_stderr.txt
then
  echo "Compilation failed." >> compile_stderr.txt
  exit 1
fi

# Run the program with input
./program < input.txt > run_stdout.txt 2> run_stderr.txt

exit 0