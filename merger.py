#!/usr/bin/python
# -*- coding: utf8 -*-
import easyio


class Merger:
    def __init__(self,
                 separator=',',
                 fixed_columns=[],
                 ignore_columns=[]):
        """
        Initializes an instance of Merger
        """
        self.separator = separator
        self.fixed_columns = fixed_columns
        self.ignore_columns = ignore_columns

    def merge_folder(self, folder_path, output_path):
        """
        Merges them according to fixed_columns
        """
        # Create CSVs for each sheet in the directory
        files = easyio.get_files(folder_path, '.csv')
        self.merge_files(files, output_path)

    def get_columns_and_data(self, file):
        """
        Gets the column names, the remaining data and the indices
        for each column
        """
        content = easyio.read_file(file)
        lines = content.split('\n')

        headers = easyio.split(lines[0], self.separator)
        lines = [easyio.split(line, self.separator)
                 for line in lines[1:] if line != '']

        fixed_column_indices = [easyio.match(c, headers)
                                for c in self.fixed_columns]
        return headers, lines, fixed_column_indices

    def merge_files(self, files, output):
        """
        Processess all csv files given
        Matches them according to the fixed_columns
        Leaves output csv at output argument
        """
        data = {}
        columns = []

        # For each file
        for idx in range(len(files)):
            # Get columns, lines and indices
            file_columns, lines, fixed_column_indices =\
                self.get_columns_and_data(files[idx])

            # Get indices for new data
            new_column_indices = [i for i in range(len(file_columns))
                                  if i not in fixed_column_indices]

            # Get headers for new data
            new_columns = ["%s - %s" %
                           (unicode(idx + 1), unicode(file_columns[i]))
                           for i in new_column_indices]

            # Append to the definition of all headers
            columns.append(new_columns)

            # For each line of data
            for line in lines:
                # Get the unique identifier (append all fixed columns)
                identifier = ",".join([line[i] if i >= 0 else ""
                                       for i in fixed_column_indices])
                new_data = [line[i] for i in new_column_indices]

                if identifier not in data:
                    data[identifier] = []

                # Add the new data
                data[identifier].append(new_data)

        # Build content for CSV
        lines = []
        lines.append(easyio.quote(
                     easyio.flatten(
                         [self.fixed_columns, columns], self.separator),
                     self.separator))

        for key in data:
            lines.append(easyio.quote(
                key + ',' + easyio.flatten(data[identifier], self.separator),
                self.separator))

        content = '\n'.join(lines)

        # Write the CSV file
        easyio.write_file(output, content)


def test():
    print('Testing...')
    import doctest
    doctest.testmod()
    print('Done')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--test',
                        dest='test',
                        help='Wether to do Testing and Exit',
                        default=False)

    parser.add_argument('--folders',
                        dest='folders',
                        help='Folders to process',
                        default='')

    parser.add_argument('--fixed_columns',
                        dest='fixed_columns',
                        help='Columns to use to match data across sheets',
                        default='')

    parser.add_argument('--ignore_columns',
                        dest='ignore_columns',
                        help='Columns to step over. Not implemented yet',
                        default='')

    parser.add_argument('--separator',
                        dest='separator',
                        help='Separator character for CSV',
                        default=',')

    parser.add_argument('--termination',
                        dest='termination',
                        help='Regexp for termination line',
                        default='^,*$')

    args = parser.parse_args()
    if args.test:
        test()
        exit()

    fixed_columns = [c.strip() for c in args.fixed_columns.split(',')]
    ignore_columns = [c.strip() for c in args.ignore_columns.split(',')]
    m = Merger(separator=args.separator,
               fixed_columns=fixed_columns,
               ignore_columns=ignore_columns,
               termination=args.termination)

    folders = args.folders.split(',')

    for folder in folders:
        m.merge_folder(folder)

    # SAMPLE:
    # python csvsheet.py --folders files --fixed_columns
    # "RUT, DV, PATERNO, MATERNO, NOMBRES, CARRERA, JORNADA, SECCION"
