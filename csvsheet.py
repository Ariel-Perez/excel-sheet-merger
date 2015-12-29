#!/usr/bin/python
# -*- coding: utf8 -*-
import xlrd
import os
import easyio


class Splitter:
    def __init__(self, separator=','):
        """
        Initializes an instance of Splitter with the given separator
        """
        self.separator = separator

    def split_folder(self, path):
        """
        Transforms all excel sheets into separate csv files
        """
        files = easyio.get_files(path, ['.xls', '.xlsx'])

        csv_files = {}
        for file_path in files:
            csv_files[file_path] = self.split_file(file_path)

        return csv_files

    def split_file(self, path):
        """
        Transforms all excel sheets into separate csv files
        """
        print('Creating CSV files for %s') % path
        wb = xlrd.open_workbook(path)
        sheet_names = wb.sheet_names()
        output_file_names = []

        for i in range(len(sheet_names)):
            sheet = wb.sheet_by_index(i)
            nrows = sheet.nrows
            lines = []

            for j in range(nrows):
                row = sheet.row(j)
                data = ['"%s"' % unicode(cell.value) for cell in row]
                lines.append(self.separator.join(data))

            content = '\n'.join(lines)
            csv_path = path.\
                replace('.xlsx', ' - %s.csv' % i).\
                replace('.xls', ' - %s.csv' % i)

            easyio.write_file(csv_path, content)
            output_file_names.append(csv_path)

        return output_file_names


class Merger:
    def __init__(self, separator=','):
        """
        Initializes an instance of Merger with the given separator
        """
        self.separator = separator
        self.splitter = Splitter(separator)

    def merge_folder(self, path, fixed_columns):
        """
        Converts sheets into separate CSV documents
        Then merges them according to fixed_columns
        """
        # Create CSVs for each sheet in the directory
        files = self.splitter.split_folder(path)
        for file_name in files:
            print('Processing %s') % file_name
            # Merge CSV sheets
            self.merge_file(files[file_name],
                            file_name
                            .replace('.xlsx', '.csv')
                            .replace('.xls', '.csv'),
                            fixed_columns)

            # Clean the directory removing unnecesary files
            self.remove(files[file_name])

    def get_columns_and_data(self, sheet, fixed_columns):
        """
        Gets the column names, the remaining data and the indices
        for each column
        """
        content = easyio.read_file(sheet)
        lines = content.split('\n')

        upper_level_headers = []
        sheet_columns = easyio.split(lines[0])
        lines = [easyio.split(line) for line in lines[1:] if line != '']

        # When multi-row headers: add rows to upper_level_headers
        while True:
            verified = True
            fixed_column_indices = []

            for c in fixed_columns:
                fixed_column_indices.append(easyio.match(c, sheet_columns))
                # The bottom-most row will contain all fixed columns
                # If not: Append to upper_level and continue
                if fixed_column_indices[-1] == -1:

                    upper_level_headers.append(sheet_columns)
                    sheet_columns = lines[0]
                    lines = lines[1:]
                    verified = False
                    break

            if verified:
                break

        # If there are multi-row headers:
        # Append upper level headers name to the column name
        # When there are empty columns on the upper levels,
        # append previous header if there is one
        if len(upper_level_headers) > 0:
            previous_headers = [''] * len(upper_level_headers)

            definite_columns = []
            for i in range(len(sheet_columns)):
                header_data = []
                for j in range(len(upper_level_headers)):
                    if upper_level_headers[j][i] != '':
                        previous_headers[j] = upper_level_headers[j][i]

                    if previous_headers[j] != '':
                        header_data.append(previous_headers[j])

                if sheet_columns[i]:
                    header_data.append(sheet_columns[i])

                definite_columns.append(' - '.join(header_data))

            sheet_columns = definite_columns

        return sheet_columns, lines, fixed_column_indices

    def merge_file(self, sheets, output, fixed_columns):
        """
        Processess all csv sheets given
        Matches them according to the fixed_columns
        Leaves output csv at output argument
        """
        data = {}
        columns = []

        # For each sheet
        for idx in range(len(sheets)):
            # Get columns, lines and indices
            sheet_columns, lines, fixed_column_indices =\
                self.get_columns_and_data(sheets[idx], fixed_columns)

            # Get indices for new data
            new_column_indices = [i for i in range(len(sheet_columns))
                                  if i not in fixed_column_indices]

            # Get headers for new data
            new_columns = ["%s - %s" %
                           (unicode(idx + 1), unicode(sheet_columns[i]))
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
        lines.append(easyio.quote(easyio.flatten([fixed_columns, columns])))

        for key in data:
            lines.append(easyio.quote(
                key + ',' + easyio.flatten(data[identifier])))

        content = '\n'.join(lines)

        # Write the CSV file
        easyio.write_file(output, content)

    def remove(self, paths):
        """
        Removes all files in the given array
        """
        for path in paths:
            os.remove(path)


def test():
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    test()
    m = Merger(separator=',')
    m.merge_folder('./files', ['RUT',
                               'DV',
                               'PATERNO',
                               'MATERNO',
                               'NOMBRES',
                               'CARRERA',
                               'JORNADA',
                               'SECCION'])
