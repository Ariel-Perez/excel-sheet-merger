#!/usr/bin/python
# -*- coding: utf8 -*-
import easyio
import xlrd


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
        Transforms an excel sheet into separate csv files
        """
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

            if len(content) > 0:
                csv_path = path.\
                    replace('.xlsx', ' - %s.csv' % i).\
                    replace('.xls', ' - %s.csv' % i)

                easyio.write_file(csv_path, content)
                output_file_names.append(csv_path)

        return output_file_names
