import argparse
from transliterator import transliterate_text

def process_file(input_path, output_path, no_diacritics=False):
    with open(input_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    transliterated_lines = [transliterate_text(line.strip(), no_diacritics=no_diacritics) for line in lines]

    with open(output_path, 'w', encoding='utf-8') as outfile:
        for line in transliterated_lines:
            outfile.write(line + '\n')

def main():
    parser = argparse.ArgumentParser(description="English to Arabic phonetic transliterator (Arabic-only letters)")
    parser.add_argument("text", nargs="?", help="Text to transliterate (if no --input provided)")
    parser.add_argument("--input", "-i", help="Input file path (line-by-line transliteration)")
    parser.add_argument("--output", "-o", help="Output file path (required if --input is used)")
    parser.add_argument("--no-diacritics", action="store_true", help="Suppress diacritics in the output")

    args = parser.parse_args()

    if args.input:
        if not args.output:
            raise ValueError("Output file must be specified with --output when using --input")
        process_file(args.input, args.output, no_diacritics=args.no_diacritics)
    elif args.text:
        print(transliterate_text(args.text, no_diacritics=args.no_diacritics))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
