try:
    import argparse
except ModuleNotFoundError as e:
    print(f"Import error in the cli module: {e}")
    exit(1)


def cli(base_dir):
    parser = argparse.ArgumentParser(
        description='Socket and HTTP servers demo')
    parser.add_argument('--dotenv', type=str, default=f'{base_dir}/.env',
                        help='Path to the .env file (default: %(default)s)')

    return parser.parse_args()
