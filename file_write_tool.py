import logging
from typong import Union


logger = logging.getLogger(__name__)

def write_file(file_path: str, content: str) -> bool:
    """Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        mode = 'wb' if isinstance(content,bytes) else 'w'
        encoding = None if isinstance(content,bytes) else 'utf-8'

        with open(file_path,mode,encoding=encoding) as f:
            f.write(content)
       logger.info("Successfully wrote to file :%s", file_path)
       return True

  except Exception as e:
      logger.error(f"Error writing to file {file_path}:{str(e)}")
      return False
