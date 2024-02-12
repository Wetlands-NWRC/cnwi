# Define the number of rows
rows = 5

# Outer loop will handle the number of rows
for i in range(1, rows + 1):
    # Print spaces. The number of spaces is equal to the total rows minus current row number
    for j in range(rows - i):
        print(" ", end="")
    # Print '*'. The number of '*' is equal to the current row number
    for j in range(i):
        print("*", end="")
    print(" ", end="")
    for j in range(i):
        print("*", end="")
    # Change line after each row
    print()


for i in range(1, rows + 1):
    for j in range(rows - i):
        print(" ", end="")
    for j in range(i):
        print("*", end="")
    print()
