import json
from pathlib import Path

DATA_DIR = '/data/'
JSON_END_TAG = '.json'
READ_TAG = 'r'
WRITE_TAG = 'w'

def get_path():

  """
    Gets current path of json file
  """

  cwd = Path( __file__ ).parents[1]
  cwd = str( cwd )

  return cwd

def read_json( filename ):

  """
    A function to read json file and return data

    Parameters:
     - filename (string): name of file to open
    
    Returns:
     - data (dict): A dictionary of the data in the file
  """
  cwd = get_path()

  with open( cwd + DATA_DIR + filename + JSON_END_TAG, READ_TAG ) as json_file:
    data = json.load( json_file )

  return data

def write_json( data, filename ):

  """
    A function to write data to specified json file
  """
  cwd = get_path()

  with open( cwd + DATA_DIR + filename + JSON_END_TAG, WRITE_TAG ) as json_file:
    json.dump( data, json_file, indent = 4 )
