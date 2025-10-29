"""Placeholder self-heal preflight that reuses security smoke tests."""

import preflight_security


def main() -> None:
    print("SELF_HEAL_PREFLIGHT_START")
    preflight_security.main()
    print("SELF_HEAL_PREFLIGHT_OK")


if __name__ == "__main__":
    main()
