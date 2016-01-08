#!/usr/bin/python
# -*- coding: utf8 -*-
import easyio
import re


class Editor:
    def __init__(self, separator=','):
        self.separator = separator
        self.empty = re.compile('^("")?(%s("")?)*$' % separator)
        self.processing_steps = []

    def process(self, folder_path):
        files = easyio.get_files(folder_path, '.csv')
        for path in files:
            content = easyio.read_file(path)
            for step in self.processing_steps:
                content = step(path, content)

            easyio.write_file(path, content)

    def add_columns_in_processing(self, header, regex_pattern):
        regex = re.compile(regex_pattern)
        value = lambda path: regex.search(easyio.path_leaf(path)).group()

        self.processing_steps.append(
            lambda path, content:
                self._add_column(path, content, header, value(path)))

    def trim_in_processing(self):
        self.processing_steps.append(self._trim)

    def set_headers_in_processing(self, headers_dict):
        self.processing_steps.append(
            lambda path, content:
                self._set_headers(path, content, headers_dict))

    def collapse_headers_in_processing(self, fixed_columns):
        self.processing_steps.append(
            lambda path, content:
                self._collapse_headers(path, content, fixed_columns))

    def expand_rows_in_processing(self):
        self.processing_steps.append(self._expand_rows)

    def remove_content_in_processing(self, unwanted_content):
        self.processing_steps.append(
            lambda path, content:
                self._remove_content(path, content, unwanted_content))

    def _add_column(self, path, content, header, value):
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
        lines = content.split('\n')
        content_start = -1
        content_length = 0

        for i in range(len(lines)):
            if not self.empty.match(lines[i]):
                if content_length == 0:
                    content_start = i
                content_length += 1

            if self.empty.match(lines[i]):
                if content_length > 1:
                    break
                content_length = 0

        lines = lines[content_start:content_start + content_length]
        content = '\n'.join(lines)
        return content

    def _set_headers(self, path, content, headers_dict):
        lines = content.split('\n')
        current_headers = easyio.split(lines[0], self.separator)
        for key in headers_dict:
            while key >= len(current_headers):
                current_headers.append('')

            current_headers[key] = headers_dict[key]

        lines[0] = easyio.quote(self.separator.join(current_headers),
                                self.separator)
        content = '\n'.join(lines)
        return content

    def _collapse_headers(self, path, content, fixed_columns):
        lines = content.split('\n')

        current_headers = ['' for header in
                           easyio.split(lines[0], self.separator)]
        column_lock = [False] * len(current_headers)
        header_ok = [False] * len(fixed_columns)

        while not all(header_ok):
            if len(lines) == 0:
                break

            new_headers = easyio.split(lines[0], self.separator)
            lines = lines[1:]

            for i in range(len(new_headers)):
                if column_lock[i]:
                    continue

                # Propagation
                # if i > 0 and new_headers[i] == '':
                #     new_headers[i] = new_headers[i - 1]

                match = easyio.match(new_headers[i], fixed_columns)
                if match != -1:
                    current_headers[i] = new_headers[i]
                    header_ok[match] = True
                    column_lock[i] = True
                else:
                    current_headers[i] =\
                        (current_headers[i] + ' ' + new_headers[i]).strip()

                    match = easyio.match(current_headers[i], fixed_columns)
                    if match != -1:
                        header_ok[match] = True
                        column_lock[i] = True

        lines.insert(0, easyio.quote(self.separator.join(current_headers),
                                     self.separator))
        content = '\n'.join(lines)
        return content

    def _expand_rows(self, path, content):
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
            lines[i] = easyio.quote(self.separator.join(data[i]),
                                    self.separator)

        content = '\n'.join(lines)
        return content

    def _remove_content(self, path, content, unwanted_content):
        lines = content.split('\n')
        for i in range(len(lines)):
            data = easyio.split(lines[i], self.separator)
            for j in range(len(data)):
                if easyio.match(data[j], unwanted_content) != -1:
                    data[j] = ''
            lines[i] = easyio.quote(self.separator.join(data), self.separator)

        content = '\n'.join(lines)
        return content
