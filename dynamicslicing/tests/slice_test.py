from utils import remove_lines

# Define a simple code as a string

code = """def slice_me():
    x = 5
    print("Hello World")
    if x < 10:
        x += 5
    y = 0
    return y

slice_me()
"""


print(code)
modified_code = remove_lines(code, [3, 6, 7, 8])

print(modified_code)

