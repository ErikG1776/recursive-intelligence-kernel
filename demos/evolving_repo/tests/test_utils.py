"""
Test suite for utility library.
The evolution agent uses these tests to validate improvements.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_email, slugify, truncate, parse_int, unique


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failures = []

    def record(self, name, passed, error=None):
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            self.failures.append({"name": name, "error": error})


def run_tests():
    """Run all tests and return results."""
    results = TestResults()

    # Email validation tests
    try:
        assert validate_email("test@example.com") == True
        results.record("email_valid_basic", True)
    except Exception as e:
        results.record("email_valid_basic", False, str(e))

    try:
        assert validate_email("invalid") == False
        results.record("email_invalid_no_at", True)
    except Exception as e:
        results.record("email_invalid_no_at", False, str(e))

    try:
        assert validate_email("test@example") == False
        results.record("email_invalid_no_dot", True)
    except Exception as e:
        results.record("email_invalid_no_dot", False, str(e))

    try:
        assert validate_email("user.name+tag@example.co.uk") == True
        results.record("email_valid_complex", True)
    except Exception as e:
        results.record("email_valid_complex", False, str(e))

    try:
        assert validate_email("") == False
        results.record("email_empty", True)
    except Exception as e:
        results.record("email_empty", False, str(e))

    try:
        assert validate_email("@.") == False
        results.record("email_just_symbols", True)
    except Exception as e:
        results.record("email_just_symbols", False, str(e))

    # Slugify tests
    try:
        assert slugify("Hello World") == "hello-world"
        results.record("slugify_basic", True)
    except Exception as e:
        results.record("slugify_basic", False, str(e))

    try:
        assert slugify("  Multiple   Spaces  ") == "--multiple---spaces--"
        results.record("slugify_multiple_spaces", True)
    except Exception as e:
        results.record("slugify_multiple_spaces", False, str(e))

    try:
        result = slugify("Special!@#Characters")
        assert result == "specialcharacters"
        results.record("slugify_special_chars", True)
    except Exception as e:
        results.record("slugify_special_chars", False, str(e))

    try:
        assert slugify("") == ""
        results.record("slugify_empty", True)
    except Exception as e:
        results.record("slugify_empty", False, str(e))

    # Truncate tests
    try:
        assert truncate("Hello World", 5) == "Hello..."
        results.record("truncate_basic", True)
    except Exception as e:
        results.record("truncate_basic", False, str(e))

    try:
        assert truncate("Hi", 10) == "Hi"
        results.record("truncate_no_change", True)
    except Exception as e:
        results.record("truncate_no_change", False, str(e))

    try:
        assert truncate("", 5) == ""
        results.record("truncate_empty", True)
    except Exception as e:
        results.record("truncate_empty", False, str(e))

    # Parse int tests
    try:
        assert parse_int("42") == 42
        results.record("parse_int_valid", True)
    except Exception as e:
        results.record("parse_int_valid", False, str(e))

    try:
        assert parse_int("invalid") == None
        results.record("parse_int_invalid", True)
    except Exception as e:
        results.record("parse_int_invalid", False, str(e))

    try:
        assert parse_int(3.14) == 3
        results.record("parse_int_float", True)
    except Exception as e:
        results.record("parse_int_float", False, str(e))

    try:
        assert parse_int("  42  ") == 42
        results.record("parse_int_whitespace", True)
    except Exception as e:
        results.record("parse_int_whitespace", False, str(e))

    # Unique tests
    try:
        assert unique([1, 2, 2, 3, 3, 3]) == [1, 2, 3]
        results.record("unique_basic", True)
    except Exception as e:
        results.record("unique_basic", False, str(e))

    try:
        assert unique([]) == []
        results.record("unique_empty", True)
    except Exception as e:
        results.record("unique_empty", False, str(e))

    try:
        assert unique([1, 1, 1]) == [1]
        results.record("unique_all_same", True)
    except Exception as e:
        results.record("unique_all_same", False, str(e))

    try:
        # Should preserve order
        assert unique([3, 1, 2, 1, 3]) == [3, 1, 2]
        results.record("unique_preserve_order", True)
    except Exception as e:
        results.record("unique_preserve_order", False, str(e))

    return results


if __name__ == "__main__":
    results = run_tests()
    print(f"Passed: {results.passed}")
    print(f"Failed: {results.failed}")
    if results.failures:
        print("Failures:")
        for f in results.failures:
            print(f"  - {f['name']}: {f['error']}")
