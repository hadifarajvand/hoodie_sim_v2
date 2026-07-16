from .cli_v2 import build_parser, dispatch, main

__all__ = ["build_parser", "dispatch", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
