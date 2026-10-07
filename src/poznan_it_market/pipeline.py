import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Import job offers.")
    parser.add_argument(
        "--mode",
        choices=["demo", "live"],
        required=True,
        help="Choose the data source and target database.",
    )
    args = parser.parse_args()

    from poznan_it_market.ingest.loader import run_pipeline

    run_pipeline(mode=args.mode)


if __name__ == "__main__":
    main()
