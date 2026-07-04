"""
Unit tests for the password_manager module.

Run with:  python -m pytest tests/ -v
"""

import pytest
from password_manager.manager import generate_password, password_strength


class TestGeneratePassword:
    def test_default_length(self):
        pw = generate_password()
        assert len(pw) == 16

    def test_custom_length(self):
        for length in [8, 12, 24, 64]:
            assert len(generate_password(length=length)) == length

    def test_too_short_raises(self):
        with pytest.raises(ValueError, match="at least 8"):
            generate_password(length=4)

    def test_no_character_sets_raises(self):
        with pytest.raises(ValueError, match="At least one"):
            generate_password(use_letters=False, use_digits=False, use_symbols=False)

    def test_letters_only(self):
        import string
        pw = generate_password(use_letters=True, use_digits=False, use_symbols=False)
        assert all(c in string.ascii_letters for c in pw)

    def test_digits_only(self):
        import string
        pw = generate_password(use_letters=False, use_digits=True, use_symbols=False)
        assert all(c in string.digits for c in pw)

    def test_no_ambiguous_chars(self):
        ambiguous = set("0O1lI|`")
        for _ in range(50):
            pw = generate_password(exclude_ambiguous=True)
            assert not any(c in ambiguous for c in pw), f"Ambiguous char in: {pw}"

    def test_uniqueness(self):
        """Two consecutive passwords should (almost) never be equal."""
        passwords = {generate_password() for _ in range(20)}
        assert len(passwords) > 1


class TestPasswordStrength:
    def test_very_strong(self):
        result = password_strength("Tr0ub4dor&3xamplePass!")
        assert result["score"] == 4
        assert result["label"] == "Very Strong"
        assert result["suggestions"] == []

    def test_weak_short(self):
        result = password_strength("abc")
        assert result["score"] < 3

    def test_all_lowercase_no_digits_no_symbols(self):
        result = password_strength("averylongpasswordwithnodigitssymbols")
        assert result["score"] < 4
        assert any("uppercase" in s.lower() or "number" in s.lower() for s in result["suggestions"])

    def test_suggestions_non_empty_for_weak(self):
        result = password_strength("password")
        assert len(result["suggestions"]) > 0

    def test_score_range(self):
        for pw in ["a", "abc123", "Abc123!", "Tr0ub4dor&3!"]:
            result = password_strength(pw)
            assert 0 <= result["score"] <= 4
