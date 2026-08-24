with open('src/main.cpp', 'r', encoding='utf-8') as f:
    lines = f.readlines()

if lines[49].strip() == '}':
    del lines[49]

with open('src/main.cpp', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Bracket fixed.")
