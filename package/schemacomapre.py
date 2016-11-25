#!bin/python

import psycopg2, pprint, deepdiff, shelve
from optparse import OptionParser
pp = pprint.PrettyPrinter(indent=2, width=80)

def run():
  version = '1.0.0'
  parser = OptionParser(version=version)
  parser.add_option('-u', '--username', help='username for db connection', metavar='USER')
  parser.add_option('-d', '--database', help='database to use', metavar='DATABASE')
  parser.add_option('-p', '--password', help='database to use', metavar='PASSWORD')

  options, args = parser.parse_args()

  if not options.username:
    parser.error('username is required')
  if not options.database:
    parser.error('database is required')

  with psycopg2.connect(database=options.database, user=options.username, password=options.password) as conn:
    with conn.cursor() as cur:
      schema_information = get_schema_information(cur)
      save_information(options.database, schema_information)


def save_information(db_name, schema_information):
  with shelve.open('schema_info') as db:
    old_data = db[db_name]
    if old_data:
      diff = deepdiff.DeepDiff(old_data, schema_information)
      if len(diff) > 0:
        pp.pprint(diff)
    db[db_name] = schema_information

def get_schema_information(cur):
  cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
  table_names = [table[0] for table in cur.fetchall()]

  def table_information(name):
    cur.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = %(name)s;", {'name':name})
    columns = {row[0] : {'data_type' : row[1], 'nullable': row[2] == 'YES'} for row in cur.fetchall()}
    cur.execute("SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_name = %(name)s;", {'name':name})
    constraints = {row[0]: {'type': row[1]} for row in cur.fetchall()}
    return {'constraints' : constraints, 'columns' : columns}
  return {name: table_information(name) for name in table_names}

def main():
  run()

if __name__ == '__main__':
  main()