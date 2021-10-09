from argparse import ArgumentParser

def get_args_from_Parser():
    parser = ArgumentParser(description='Argument parser for Database settings')

    parser.add_argument('--database', metavar ='DATABASE PATH', type=str, dest='DATABASE_PATH',
                        default=None, required=True, help='Path of the Database')

    parser.add_argument('--table', metavar ='TABLE NAME', type=str, dest='TABLE_NAME', default=None,
                        required=True, help='Name of the table')


    parser.add_argument('--csv', metavar ='CSV file', type=str, dest='CSV_PATH', default=None,
                        required=True, help='CSV file with data to push to database table')

    parsed_args = parser.parse_args()

    args = parser.parse_args()
    
    return args

if __name__ == "__main__":
    print(f'args {args}')