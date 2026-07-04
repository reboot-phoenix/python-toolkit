"""Unit tests for utils.helpers."""

import pytest
from utils.helpers import slugify, clamp, truncate, chunk, flatten


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello, World!") == "hello-world"

    def test_spaces_become_hyphens(self):
        assert slugify("foo bar baz") == "foo-bar-baz"

    def test_multiple_spaces(self):
        assert slugify("foo   bar") == "foo-bar"

    def test_already_slug(self):
        assert slugify("already-fine") == "already-fine"


class TestClamp:
    def test_within_range(self):
        assert clamp(5, 0, 10) == 5

    def test_below_min(self):
        assert clamp(-3, 0, 10) == 0

    def test_above_max(self):
        assert clamp(15, 0, 10) == 10

    def test_at_boundary(self):
        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10


class TestTruncate:
    def test_short_string_unchanged(self):
        assert truncate("hi", 80) == "hi"

    def test_truncation(self):
        result = truncate("hello world", max_length=8)
        assert len(result) == 8
        assert result.endswith("…")

    def test_custom_suffix(self):
        result = truncate("hello world", max_length=8, suffix="...")
        assert result.endswith("...")


class TestChunk:
    def test_even(self):
        assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]

    def test_uneven(self):
        assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]

    def test_size_one(self):
        assert chunk([1, 2, 3], 1) == [[1], [2], [3]]

    def test_invalid_size(self):
        with pytest.raises(ValueError):
            chunk([1, 2], 0)


class TestFlatten:
    def test_already_flat(self):
        assert flatten([1, 2, 3]) == [1, 2, 3]

    def test_one_level(self):
        assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]

    def test_deeply_nested(self):
        assert flatten([1, [2, [3, [4]]]]) == [1, 2, 3, 4]

    def test_empty(self):
        assert flatten([]) == []
