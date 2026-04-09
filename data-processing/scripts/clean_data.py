import os

def clean_text(text):
    return text.strip().replace("\n\n", "\n")

def process_files(input_dir, output_dir):
    for file in os.listdir(input_dir):
        with open(f"{input_dir}/{file}", "r") as f:
            content = clean_text(f.read())

        with open(f"{output_dir}/{file}", "w") as f:
            f.write(content)

process_files("raw", "processed")