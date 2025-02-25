import sys
import re

def title(line):
    regex = r"^\s*(#{1,6})\s+(.*)$"
    b = re.match(regex, line)

    if b:
        size = len(b.group(1))
        return f"<h{size}>{b.group(2)}</h{size}>"

    return line

def bold(line):
    regex = r"(\*\*)([^\*]*?)\1"
    return re.sub(regex, r"<b>\2</b>", line)

def italic(line):
    regex = r"(\*)(.*?)\1"
    return re.sub(regex, r"<i>\2</i>", line)

def listnumber(line):
    regex = r"^\s*\d\.\s+(.*)$"
    b = re.match(regex, line)
    if b:
        return f"<li>{b.group(1)}</li>"

    return line

def link(line):
    regex = r"\[(.*?)\]\((.*?)\)"
    return re.sub(regex, r'<a href="\2">\1</a>', line)

def image(line):
    regex = r"\!\[(.*?)\]\((.*?)\)"
    return re.sub(regex, r'<img src="\2" alt="\1"/>', line)

def ol(lines):
    result = []
    previous_li = False

    for line in lines:
        li = line.startswith("<li>")

        if li and not previous_li:
            result.append("<ol>")

        result.append(line)

        if not li and previous_li:
            result.append("</ol>")

        previous_li = li

    if previous_li:
        result.append("</ol>")

    return result

def convert(text):
    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        processed_line = line
        processed_line = title(processed_line)
        processed_line = bold(processed_line)
        processed_line = italic(processed_line)
        processed_line = listnumber(processed_line)
        processed_line = link(processed_line)
        processed_line = image(processed_line)
        processed_lines.append(processed_line)

    processed_lines = ol(processed_lines)

    print('\n'.join(processed_lines))

def main():
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as file:
                text = file.read()
                convert(text)
        except FileNotFoundError:
            print(f"Ficheiro {sys.argv[1]} não encontrado.")
    else:
        print("Ficheiro markdown em falta")


if __name__ == "__main__":
    main()
