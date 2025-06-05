.PHONY: all clean

CC = gcc

TARGET = main

OBJS = main.o submitted_code.o

CFLAGS = -Wall -Wextra


all: $(TARGET)


$(TARGET): $(OBJS)
	$(CC) -o $(TARGET) $(OBJS)


main.o: main.c submitted_code.h
	$(CC) $(CFLAGS) -c main.c -o main.o


submitted_code.o: submitted_code.c
	$(CC) $(CFLAGS) -c submitted_code.c -o submitted_code.o


clean:
	rm -f $(OBJS) $(TARGET)
