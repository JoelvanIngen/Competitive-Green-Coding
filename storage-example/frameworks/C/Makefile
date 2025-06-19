
.PHONY: all clean

CC = gcc

# Final target file
TARGET = main

# Object files
OBJS = main.o submitted_code.o

# Compiler flags
CFLAGS = -O3 -Wall -Wextra -std=c11 -march=native


all: $(TARGET)


$(TARGET): $(OBJS)
	$(CC) -o $(TARGET) $(OBJS)


main.o: main.c submitted_code.h
	$(CC) $(CFLAGS) -c main.c -o main.o


submitted_code.o: submitted_code.c
	$(CC) $(CFLAGS) -c submitted_code.c -o submitted_code.o

# Clean up generated files
clean:
	rm -f $(OBJS) $(TARGET)




