import pytest
from unittest import mock
from file_reader import read_file

def test_read_file_success():
    mock_open = mock.mock_open(read_data="test content")
    with mock.patch("builtins.open", mock_open):
        result = read_file("dummy.txt")
        assert result == "test content"
        mock_open.assert_called_once_with("dummy.txt", "r", encoding="utf-8")

def test_read_file_file_not_found():
    with mock.patch("builtins.open", side_effect=FileNotFoundError("file not found")):
        with pytest.raises(FileNotFoundError):
            read_file("missing.txt")

def test_read_file_generic_exception():
    with mock.patch("builtins.open", side_effect=OSError("disk error")):
        with pytest.raises(OSError):
            read_file("error.txt")
