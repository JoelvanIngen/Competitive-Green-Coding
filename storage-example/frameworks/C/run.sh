# Compile the program with all warnings and optimisations and check for compilation errors
if ! make 1> compile_stdout.txt 2> compile_stderr.txt
then
  echo "compile" > failed.txt
  exit 1
fi

# Run the program with input
if ! ./program < input.txt > run_stdout.txt 2> run_stderr.txt
then
  echo "runtime" > failed.txt
  exit 1
fi

# Does not actually fail, just so we don't get errors looking for the `failed.txt` file
echo "success" > failed.txt

exit 0