try:
    import argparse
except ModuleNotFoundError as e:
    print(f"Import error in the utils module: {e}")
    exit(1)


def cli():
    parser = argparse.ArgumentParser(
        description='Socket and HTTP servers demo')
    parser.add_argument('--dotenv', type=str, default='.env',
                        help='Path to the .env file (default: %(default)s)')

    return parser.parse_args()
