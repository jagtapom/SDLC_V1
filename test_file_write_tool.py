import pytest
from unittest import mock
from file_writer import write_file

def test_write_file_text_success():
    mock_open = mock.mock_open()
    with mock.patch("builtins.open", mock_open):
        result = write_file("dummy.txt", "some text content")
        assert result is True
        mock_open.assert_called_once_with("dummy.txt", "w", encoding="utf-8")
        mock_open().write.assert_called_once_with("some text content")

def test_write_file_binary_success():
    mock_open = mock.mock_open()
    with mock.patch("builtins.open", mock_open):
        result = write_file("dummy.bin", b"binary content")
        assert result is True
        mock_open.assert_called_once_with("dummy.bin", "wb", encoding=None)
        mock_open().write.assert_called_once_with(b"binary content")

def test_write_file_exception():
    with mock.patch("builtins.open", side_effect=IOError("disk error")):
        result = write_file("fail.txt", "text")
        assert result is False
