#!bin/python

from shelve import open
from deepdiff import DeepDiff
from pprint import PrettyPrinter
from psycopg2 import connect
from argparse import ArgumentParser

pp = PrettyPrinter(indent=2, width=80)
version = '1.0.0'


def run():
    parser = create_parser()

    args = parser.parse_args()
    validate_options(args, parser)

    with connect(database=args.database, user=args.username, password=args.password) as conn:
        with conn.cursor() as cur:
            save_information(args.database, get_schema_information(cur), args.save)


def validate_options(options, parser):
    if not options.username:
        parser.error('username is required')
    if not options.database:
        parser.error('database is required')


def create_parser():
    parser = ArgumentParser()
    parser.add_argument('-u', '--username', help='username for db connection', metavar='USER')
    parser.add_argument('-d', '--database', help='database to use', metavar='DATABASE')
    parser.add_argument('-p', '--password', help='database to use', metavar='PASSWORD')
    parser.add_argument('-s', '--save',     help='store current state of database', action='store_true')
    return parser


def save_information(db_name, schema_information, overwrite=False):
    with open('schema_info') as db:
        try:
            old_data = db[db_name]
            if old_data:
                diff = DeepDiff(old_data, schema_information)
                if len(diff) > 0:
                    pp.pprint(diff)
        finally:
            if overwrite:
                db[db_name] = schema_information


def get_schema_information(cur):
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    table_names = [table[0] for table in cur.fetchall()]

    def table_information(name):
        cur.execute(
            "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = %(name)s;",
            {'name': name})
        columns = {row[0]: {'data_type': row[1], 'nullable': row[2] == 'YES'} for row in cur.fetchall()}
        cur.execute(
            "SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_name = %(name)s;",
            {'name': name})
        constraints = {row[0]: {'type': row[1]} for row in cur.fetchall()}
        return {'constraints': constraints, 'columns': columns}

    return {name: table_information(name) for name in table_names}


def main():
    run()


if __name__ == '__main__':
    main()
