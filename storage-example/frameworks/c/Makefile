
.PHONY: all clean

CC = gcc

# Final target file
TARGET = main

# Compiler flags
CFLAGS = -O3 -Wall -Wextra -std=c11 -march=native

SRCS = $(wildcard *.c)

OBJS = $(SRCS:.c=.o)


all: $(TARGET)


# Link all object files
$(TARGET): $(OBJS)
	@echo "Linking $(TARGET)..."
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

# Compile all .c files into .o files
%.o: %.c
	@echo "Compiling $<..."
	$(CC) $(CFLAGS) -c $< -o $@

# Clean up generated files
clean:
	rm -f $(OBJS) $(TARGET)




