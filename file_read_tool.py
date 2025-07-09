""" 
File reading utlility module.

This module provided funcitonality to read contentn from text files with 
proper error handling and logging.
"""

#configure Logging

logger = logging.getlogger(__name__)

def read-file(file_path: Str) -> str:
"""
 Read content from a text file .

Args:
   file_path (str) : Path to the file to read

Returns:
  str: Content of the file 

Raises:
    FileNotFoundError: if the file does.nt exist
    Exception: for Other file reading errors
"""
try:
    logger.info("Reading file:%s", file_path)
    with open(file_path,'r',encoding='utf-8') as f:
      Content = f.read()
    logger.error("File not found : %s", file_path)
     raise
   except Exception as e:
      logger.error("Error reading file %s:%s",file_path,str9e))
       raise
