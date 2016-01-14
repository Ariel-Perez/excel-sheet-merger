#!/usr/bin/python
# -*- coding: utf8 -*-
import easyio
import re


class Editor:
    def __init__(self, separator=','):
        self.separator = separator
        self.empty = re.compile('^("")?(%s("")?)*$' % separator)
        self.processing_steps = []
        self.skip_files = []

    def process(self, folder_path):
        """
        Does all the processing on all files on a given folder,
        except for those explicitly skipped
        """
        # All files
        files = easyio.get_files(folder_path, '.csv')
        for path in files:
            # No-skip files
            if path not in self.skip_files:
                # Each processing step takes as input path and content
                # and returns the modified content
                content = easyio.read_file(path)
                for step in self.processing_steps:
                    content = step(path, content)

                # The content is written back to the file
                # at the end of processing
                easyio.write_file(path, content)

    def skip_files_in_processing(self, files):
        """
        Sets files to skip during processing
        """
        if not isinstance(files, list):
            files = [files]

        self.skip_files.extend(files)

    def add_columns_in_processing(self, header, regex_pattern):
        """
        Adds a column at the end of every file.
        The header is given by argument, and the value is extracted
        from the file name using the given regex pattern.
        """
        regex = re.compile(regex_pattern)
        value = lambda path: regex.search(easyio.path_leaf(path)).group()

        self.processing_steps.append(
            lambda path, content:
                self._add_column(path, content, header, value(path)))

    def remove_empty_columns_in_processing(self):
        """
        Remove all empty collumns
        """
        self.processing_steps.append(self._remove_empty_columns)

    def trim_in_processing(self):
        """
        Remove empty rows
        """
        self.processing_steps.append(self._trim)

    def set_headers_in_processing(self, headers_dict):
        """
        Override the document headers.
        Receives a dictionary (int, str) with indices and headers
        """
        self.processing_steps.append(
            lambda path, content:
                self._set_headers(path, content, headers_dict))

    def collapse_headers_in_processing(self,
                                       fixed_columns,
                                       optional_columns,
                                       ignore_columns):
        """
        Collapse headers into one row.
        Will keep collapsing headers until all fixed_columns are found.
        Every column has its cells merged until either it matches a
        fixed/optional column or every fixed_column is found.

        If a header matches an ignore_column it is also no longer processed.
        """
        self.processing_steps.append(
            lambda path, content:
                self._collapse_headers(path,
                                       content,
                                       fixed_columns,
                                       optional_columns,
                                       ignore_columns))

    def expand_rows_in_processing(self):
        """
        Expand rows with empty spaces until they all are the same length
        """
        self.processing_steps.append(self._expand_rows)

    def remove_content_in_processing(self, unwanted_content):
        """
        Remove specific content from cells
        """
        self.processing_steps.append(
            lambda path, content:
                self._remove_content(path, content, unwanted_content))

    def _add_column(self, path, content, header, value):
        """
        Internal function to add column
        """
        lines = content.split('\n')
        if len(lines) > 0:
            lines[0] = self.separator.join([lines[0],
                                           easyio.quote(header,
                                                        self.separator)])

        for i in range(1, len(lines)):
            if not self.empty.match(lines[i]):
                lines[i] = self.separator.join([lines[i],
                                               easyio.quote(value,
                                                            self.separator)])

        content = '\n'.join(lines)
        return content

    def _trim(self, path, content):
        """
        Internal function to trim
        """
        lines = content.split('\n')

        new_lines = []
        for line in lines:
            if not self.empty.match(line):
                new_lines.append(line)

        lines = new_lines
        content = '\n'.join(lines)
        return content

    def _set_headers(self, path, content, headers_dict):
        """
        Internal function to set headers
        """
        lines = content.split('\n')
        current_headers = easyio.split(lines[0], self.separator)
        for key in headers_dict:
            if key < len(current_headers):
                current_headers[key] = headers_dict[key]

        lines[0] = easyio.merge(current_headers, self.separator)
        content = '\n'.join(lines)
        return content

    def _collapse_headers(self, path, content,
                          fixed_columns, optional_columns, ignore_columns):
        """
        Internal function to collapse headers
        """
        lines = content.split('\n')

        current_headers = ['' for header in
                           easyio.split(lines[0], self.separator)]

        columns = fixed_columns[:] + optional_columns[:]

        column_lock = [False] * len(current_headers)
        header_ok = [False] * len(fixed_columns) +\
            [True] * len(optional_columns)

        while not all(header_ok):
            if len(lines) == 0:
                break

            new_headers = easyio.split(lines[0], self.separator)
            lines = lines[1:]

            for i, header in enumerate(new_headers):
                if column_lock[i]:
                    continue

                # Propagation
                # if i > 0 and new_headers[i] == '':
                #     new_headers[i] = new_headers[i - 1]

                match = easyio.match(header, columns)
                if match != -1:
                    current_headers[i] = header
                    header_ok[match] = True
                    column_lock[i] = True
                elif easyio.match(current_headers[i], ignore_columns) != -1:
                        column_lock[i] = True
                else:
                    current_headers[i] =\
                        (current_headers[i] + ' ' + header).strip()

                    match = easyio.match(current_headers[i], columns)
                    if match != -1:
                        header_ok[match] = True
                        column_lock[i] = True
                    if easyio.match(current_headers[i], ignore_columns) != -1:
                        column_lock[i] = True

        lines.insert(0, easyio.merge(current_headers, self.separator))
        content = '\n'.join(lines)
        return content

    def _expand_rows(self, path, content):
        """
        Internal function to expand rows
        """
        lines = content.split('\n')
        data = []
        max_columns = 0
        for line in lines:
            columns = easyio.split(line, self.separator)
            max_columns = max(len(columns), max_columns)
            data.append(columns)

        for i in range(len(lines)):
            extra = max_columns - len(data[i])
            data[i].extend([''] * extra)
            lines[i] = easyio.merge(data[i], self.separator)

        content = '\n'.join(lines)
        return content

    def _remove_content(self, path, content, unwanted_content):
        """
        Internal function to remove content
        """
        lines = content.split('\n')
        for i in range(len(lines)):
            data = easyio.split(lines[i], self.separator)
            for j in range(len(data)):
                if easyio.match(data[j], unwanted_content) != -1:
                    data[j] = ''
            lines[i] = easyio.merge(data, self.separator)

        content = '\n'.join(lines)
        return content

    def _remove_empty_columns(self, path, content):
        """
        Internal function to remove empty columns

        >>> content='a,b,,,e\\n1,2,,,5'
        >>> e = Editor()
        >>> e._remove_empty_columns('', content)
        '"a","b","e"\\n"1","2","5"'
        """
        lines = content.split('\n')
        all_data = [easyio.split(line, self.separator) for line in lines]
        has_content = set()
        for data in all_data:
            for i, x in enumerate(data):
                if len(x.strip()) > 0:
                    has_content.add(i)

        new_lines = []
        for data in all_data:
            new_data = [x for i, x in enumerate(data) if i in has_content]
            new_lines.append(easyio.merge(new_data, self.separator))

        content = '\n'.join(new_lines)
        return content


def test():
    print('Testing...')
    import doctest
    doctest.testmod()
    print('Done')


if __name__ == '__main__':
    test()
