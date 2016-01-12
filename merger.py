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
        """
        matches = {}
        for i, header in enumerate(headers):
            match = easyio.match(header, lookups)
            if match != -1:
                matches[match] = i

        return matches

    def merge_files(self, files, output):
        """
        Processess all csv files given
        Matches them according to the fixed_columns
        Leaves output csv at output argument
        """
        data = {}
        merged_data = {}
        columns = []

        # For each file
        for idx, path in enumerate(files):
            print(str(int(idx * 100 / len(files))) + '%')
            # Split content in headers and data
            headers, rows = self.get_headers_and_data(path)

            # Indices (fixed -> header index)
            fixed_column_indices =\
                self.build_indices(headers, self.fixed_columns)
            merge_column_indices =\
                self.build_indices(headers, self.merge_columns)
            ignore_column_indices =\
                self.build_indices(headers, self.ignore_columns)

            fixed_indices = fixed_column_indices.values()
            merge_indices = merge_column_indices.values()
            ignore_indices = ignore_column_indices.values()

            # Indices (header -> fixed index)
            new_column_indices = [i for i, x in enumerate(headers)
                                  if i not in fixed_indices
                                  and i not in merge_indices
                                  and i not in ignore_indices]

            if any([i == -1 for i in new_column_indices]):
                if not self.expect_new_columns:
                    print('ERROR EN FORMATO',
                          'NO SE ESPERAN NUEVAS COLUMNAS:', path)

            regex_match = self.new_columns_regex.search(path)
            for i in new_column_indices:
                new_column_name =\
                    u' '.join([regex_match.group(),
                               unicode(headers[i])])\
                    if regex_match else headers[i]

                headers[i] = new_column_name.strip()

                if easyio.match(headers[i], columns) == -1:
                    columns.append(new_column_name.strip())

            column_match = [easyio.match(c, headers) for c in columns]

            # For each row of data
            for row in rows:
                # Get the unique identifier (append all fixed columns)
                identifier = self.separator.join(
                    [row[fixed_column_indices[i]]
                     if i in fixed_column_indices else u''
                     for i, x in enumerate(self.fixed_columns)])

                merge =\
                    [row[merge_column_indices[i]]
                     if i in merge_column_indices else u''
                     for i, x in enumerate(self.merge_columns)]

                new_data = [row[i] if i != -1 else u'' for i in column_match]

                if identifier not in data:
                    data[identifier] = []
                    merged_data[identifier] = []

                if len(data[identifier]) < len(columns):
                    data[identifier].extend(
                        [u''] * (len(columns) -
                                 len(data[identifier])))

                if len(merged_data[identifier]) < len(self.merge_columns):
                    merged_data[identifier].extend(
                        [u''] * (len(self.merge_columns) -
                                 len(merged_data[identifier])))

                # Add the new data
                for i, x in enumerate(new_data):
                    if len(x) > 0:
                        data[identifier][i] = x

                for i, x in enumerate(merge):
                    if len(x) > 0:
                        merged_data[identifier][i] = x

        # Build content for CSV
        lines = []

        headers = []
        if len(self.fixed_columns) > 0:
            headers.extend(self.fixed_columns)
        if len(self.merge_columns) > 0:
            headers.extend(self.merge_columns)
        if len(columns) > 0:
            headers.extend(columns)

        lines.append(easyio.quote(self.separator.join(headers),
                                  self.separator))

        for key in data:
            row_data = [key]
            if len(merged_data[key]) > 0:
                row_data.extend(merged_data[key])
            if len(data[key]) > 0:
                row_data.extend(data[key])

            lines.append(
                easyio.quote(self.separator.join(row_data),
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
