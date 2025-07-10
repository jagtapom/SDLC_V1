# import pytest
# from unittest import mock
# from file_reader import read_file

# def test_read_file_success():
#     mock_open = mock.mock_open(read_data="test content")
#     with mock.patch("builtins.open", mock_open):
#         result = read_file("dummy.txt")
#         assert result == "test content"
#         mock_open.assert_called_once_with("dummy.txt", "r", encoding="utf-8")

# def test_read_file_file_not_found():
#     with mock.patch("builtins.open", side_effect=FileNotFoundError("file not found")):
#         with pytest.raises(FileNotFoundError):
#             read_file("missing.txt")

# def test_read_file_generic_exception():
#     with mock.patch("builtins.open", side_effect=OSError("disk error")):
#         with pytest.raises(OSError):
#             read_file("error.txt")
import pytest
from unittest import mock
from file_reader import read_file

@mock.patch("file_reader.logger")
def test_read_file_success(mock_logger):
    mock_open = mock.mock_open(read_data="hello world")
    with mock.patch("builtins.open", mock_open):
        result = read_file("sample.txt")
        assert result == "hello world"
        mock_logger.info.assert_called_once_with("Reading file: %s", "sample.txt")

@mock.patch("file_reader.logger")
def test_read_file_file_not_found(mock_logger):
    with mock.patch("builtins.open", side_effect=FileNotFoundError("file missing")):
        with pytest.raises(FileNotFoundError):
            read_file("missing.txt")
        mock_logger.error.assert_called_once_with("File not found: %s", "missing.txt")

@mock.patch("file_reader.logger")
def test_read_file_other_exception(mock_logger):
    with mock.patch("builtins.open", side_effect=OSError("disk read error")):
        with pytest.raises(OSError):
            read_file("bad.txt")
        mock_logger.error.assert_called_once()
        assert "bad.txt" in mock_logger.error.call_args[0][0]
