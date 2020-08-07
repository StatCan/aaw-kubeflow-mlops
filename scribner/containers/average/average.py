import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Returns the average of one or more numbers as a JSON file")
    parser.add_argument(
        "numbers",
        type=float,
        nargs="+",
        help="One or more numbers",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="out.txt",
        help="Filename to write output number to",
    )
    return parser.parse_args()


def main(output_file, numbers):
    print(f"Averaging numbers: {numbers}")
    avg = sum(numbers) / len(numbers)
    print(f"Result = {avg}")

    print(f"Writing output to {output_file}")
    with open(output_file, 'w') as fout:
        fout.write(str(avg))


if __name__ == '__main__':
    args = parse_args()
    main(output_file=args.output_file, numbers=args.numbers)
    print("Done")