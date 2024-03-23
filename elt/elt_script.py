import subprocess
import time

def wait_for_postgres(host, max_retries=5, delay_seconds=5):
  retries = 0
  while retries < max_retries:
    try:
      result = subprocess.run(
        ['pg_is_ready', '-h', host], check=True, capture_output=True, text=True
      )
      if 'accepting connections ' in result.stdout:
        print('successfully connected to postgres')
        return True
    except subprocess.CalledProcessError as e:
      print(f'error connecting to postgres : {e}')
      retries += 1
      print(
        f'retrying in {delay_seconds} seconds ... (Attempt {retries}/{max_retries})'
      )
      time.sleep(delay_seconds)
  print('Max retries reached . Exiting...')
  return False

if not wait_for_postgres(host='source_postgres'):
  exit(1)
  
print('STARTING THE ELT SCRIPT... ')

source_config = {
  'dbname':'source_db',
  'user':'postgres',
  'password':'secret',
  'host':'source_postgres'
}

destination_config = {
  'dbname':'destination_db',
  'user':'postgres',
  'password':'secret',
  'host':'destination_postgres'
}

dump_command = [
  'pg_dump',
  '-h', source_config['host'],
  '-U', source_config['user'],
  '-d', source_config['dbname'],
  '-f', 'data_dump.sql',
  '-w'
]

subprocess_env = dict(PASSWORD=source_config['password'])

subprocess.run(dump_command, env=subprocess_env , check=True)

load_command = [
  'psql',
  '-h', destination_config['host'],
  '-U', destination_config['user'],
  '-d', destination_config['dbname'],
  '-a','-f', 'data_dump.sql',
]

subprocess_env = dict(PASSWORD=destination_config['password'])

subprocess.run(load_command, env=subprocess_env , check=True)

print('ENDING ELT SCRIPT...')