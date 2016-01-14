#!/usr/bin/python
# -*- coding: utf8 -*-
import easyio
import re


class Merger:
    def __init__(self,
                 separator=',',
                 fixed_columns=[],
                 ignore_columns=[],
                 merge_columns=[],
                 expect_new_columns=False,
                 new_columns_regex=''):
        """
        Initializes an instance of Merger
        """
        self.separator = separator
        self.fixed_columns = fixed_columns
        self.ignore_columns = ignore_columns
        self.merge_columns = merge_columns
        self.expect_new_columns = expect_new_columns
        self.new_columns_regex = re.compile(new_columns_regex)

    def merge_folder(self, folder_path, output_path):
        """
        Merges them according to fixed_columns
        """
        # Create CSVs for each sheet in the directory
        files = easyio.get_files(folder_path, '.csv')
        if output_path in files:
            files.remove(output_path)

        self.merge_files(files, output_path)

    def get_headers_and_data(self, file):
        """
        Gets the column names and the remaining data
        """
        content = easyio.read_file(file)
        lines = content.split('\n')

        headers = easyio.split(lines[0], self.separator)
        lines = [easyio.split(line, self.separator)
                 for line in lines[1:] if line != '']

        return headers, lines

    def build_indices(self, headers, lookups):
        """
        Gets a dictionary (column: match_id)
        for all columns with a match (!= -1)

        >>> m = Merger()
        >>> headers = ['Id', 'Rut', 'Column1', 'Column2']
        >>> lookups = ['ID', 'RUT', 'COLUMN2']
        >>> expected_result = {0: 0, 1: 1, 2: -1, 3: 2}
        >>> m.build_indices(headers, lookups) == expected_result
        True
        """
        matches = {i: easyio.match(header, lookups)
                   for i, header in enumerate(headers)}
        return matches

    def build_column_indices(self, headers, columns, prepend):
        """
        Gets a dictionary for all columns
        (Output Column Index -> File Column Index)

        Adds new columns to the definition if need be

        >>> fc = ['A', 'B']
        >>> columns = ['A', 'B']
        >>> m = Merger(fixed_columns=fc, expect_new_columns=True)
        >>> indices = m.build_column_indices(['A', 'B', 'C'], columns, '1')
        >>> expected_result = {0:0, 1:1, 2:2}
        >>> indices == expected_result
        True

        >>> indices = m.build_column_indices(['C', 'B', 'A', 'C'],\
         columns, '1')
        >>> expected_result = {0:2, 1:1, 2:0, 3:2}
        >>> indices == expected_result
        True

        >>> columns
        ['A', 'B', '1 C']
        """
        indices = self.build_indices(headers, columns)

        for i, header in enumerate(headers):
            if indices[i] == -1:
                if easyio.match(header, self.ignore_columns) != -1:
                    continue

                column_name = (' '.join([prepend, headers[i]])).strip()
                match = easyio.match(column_name, columns)
                if match != -1:
                    indices[i] = match
                else:
                    if not self.expect_new_columns:
                        print('ERROR EN FORMATO',
                              'NO SE ESPERAN NUEVAS COLUMNAS:')
                    indices[i] = len(columns)
                    columns.append(column_name)

        return indices

    def build_data(self, row, indices, columns):
        """
        Build data from a row and indices and columns

        >>> row = ['1', '2', 'D']
        >>> indices = {0: 1, 1: 2, 2:0}
        >>> columns = ['A', 'B', 'C', 'D']
        >>> m = Merger()
        >>> m.build_data(row, indices, columns)
        ['D', '1', '2', u'']
        """
        data = [u''] * len(columns)
        for i in indices:
            if indices[i] != -1 and len(row[i]) > 0:
                data[indices[i]] = row[i]

        return data

    def merge_files(self, files, output):
        """
        Processess all csv files given
        Matches them according to the fixed_columns
        Leaves output csv at output argument
        """
        columns = self.fixed_columns[:] + self.merge_columns[:]
        data = {}

        # For each file
        for idx, path in enumerate(files):
            print(str(int(idx * 100 / len(files))) + '%')
            # Split content in headers and data
            headers, rows = self.get_headers_and_data(path)

            # Indices (fixed -> header index)
            regex_match = self.new_columns_regex.search(path)
            prepend = regex_match.group() if regex_match else u''
            indices = self.build_column_indices(headers, columns, prepend)

            # print(columns)
            # For each row of data
            for row in rows:
                # Get the data for each column
                new_data = self.build_data(row, indices, columns)

                # Get the unique identifier
                identifier_data = new_data[0:len(self.fixed_columns)]
                identifier = easyio.merge(identifier_data, self.separator)

                if identifier not in data:
                    data[identifier] = new_data

                else:
                    if len(new_data) > len(data[identifier]):
                        data[identifier].extend([u''] *
                                                (len(new_data) -
                                                 len(data[identifier])))
                    for i, x in enumerate(new_data):
                        if len(x) > 0:
                            data[identifier][i] = x

        # Build content for CSV
        lines = []

        headers = columns[:]
        lines.append(easyio.merge(headers, self.separator))

        for key in data:
            lines.append(easyio.merge(data[key], self.separator))

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
                        help='Whether to do Testing and Exit',
                        default=False)

    parser.add_argument('--folders',
                        dest='folders',
                        help='Folders to process',
                        default=u'')

    parser.add_argument('--fixed_columns',
                        dest='fixed_columns',
                        help='Columns to use to match data across sheets',
                        default=u'')

    parser.add_argument('--ignore_columns',
                        dest='ignore_columns',
                        help='Columns to step over. Not implemented yet',
                        default=u'')

    parser.add_argument('--separator',
                        dest='separator',
                        help='Separator character for CSV',
                        default=u',')

    args = parser.parse_args()
    if args.test:
        test()
        exit()

    fixed_columns = [unicode(c.strip()) for c in args.fixed_columns.split(',')]
    ignore_columns = [unicode(c.strip())
                      for c in args.ignore_columns.split(',')]
    m = Merger(separator=args.separator,
               fixed_columns=fixed_columns,
               ignore_columns=ignore_columns)

    folders = args.folders.split(',')

    for folder in folders:
        m.merge_folder(folder)

    # SAMPLE:
    # python csvsheet.py --folders files --fixed_columns
    # "RUT, DV, PATERNO, MATERNO, NOMBRES, CARRERA, JORNADA, SECCION"
