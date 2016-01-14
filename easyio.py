#!/usr/bin/python
# -*- coding: utf8 -*-
import codecs
import os
import ntpath


def get_files(path, extensions='*'):
    """
    Gets the paths to files in a given path
    """
    if path[-1] is not '/' and path[-1] is not '\\':
        path = path + '/'

    if isinstance(extensions, str) or isinstance(extensions, unicode):
        extensions = [extensions]

    all_files = [os.path.join(root, filename)
                 for root, dirnames, filenames in os.walk(path)
                 for filename in filenames]

    filtered_files = [
        filename for filename in all_files
        if get_extension(filename) in extensions or '*' in extensions
    ]

    return filtered_files


def path_leaf(path):
    """
    Gets the file name (without path) from a full path
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_extension(path):
    """
    Gets the extension of a file

    >>> path = 'dir/file.txt'
    >>> get_extension(path)
    '.txt'
    """
    return os.path.splitext(path)[1]


def write_file(path, content):
    """
    Writes the content to a file
    """
    with codecs.open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def read_file(path):
    """
    Retrieves the content of a file
    """
    with codecs.open(path, encoding='utf-8') as f:
        text = f.read().replace('\r', '')

    return text


def flatten(arr, separator=','):
    """
    Flattens arrays of arrays of arrays.....
    To just comma separated values

    >>> a = [[[1,2,3],5], [1,2,4,7], 9]
    >>> flatten(a)
    u'1,2,3,5,1,2,4,7,9'
    """
    if not isinstance(arr, list):
        return unicode(arr)

    else:
        return separator.join([flatten(x) for x in arr])


def quote(data, separator=','):
    """
    Encloses all values in a CSV in doble quotes.

    >>> d = 'Hello, world'
    >>> quote(d)
    '"Hello"," world"'
    """
    return '"%s"' % data.replace(separator, '"%s"' % separator)


def unquote(data):
    """
    Removes doble quotes enclosing data

    >>> unquote('"Hello World"')
    'Hello World'
    """
    if len(data) > 1:
        if data[0] == '"' and data[-1] == '"':
            data = data[1:-1]

    return data


def _next_term(line, separator=',', quote='"'):
    if line[0] == quote:
        end = line.index(quote, 1)
        term = line[1:end]

        if separator in line[end:]:
            start = line.index(separator, end) + 1
            line = line[start:]
        else:
            line = ''
    else:
        if separator in line:
            end = line.index(separator)
            term = line[0:end]

            start = end + 1
            line = line[start:]
        else:
            term = line
            line = ''

    return term, line


def split(line, separator=','):
    """
    Splits a line of CSV into its values and unquotes it.

    >>> line = 'Hello,"world"'
    >>> split(line)
    ['Hello', 'world']
    """
    data = []
    quote = '"'
    while len(line) > 0:
        term, line = _next_term(line, separator, quote)
        data.append(unquote(term))

    return data


def merge(data, separator=','):
    """
    Merges data into a CSV string and quotes it.

    >>> data = ['Hello', 'wor,ld']
    >>> merge(data)
    u'"Hello","wor,ld"'
    """
    s = separator.join(['"%s"' % unicode(x) for x in data])
    return s


def match(text, possibilities):
    """
    Match a text to one of the possible options
    Accepts minor mismatches such as pluralization with appended 's'
    and lower/upper casing

    Returns -1 if no match is found

    >>> text = 'Penguin'
    >>> possibilities = ['penguin']
    >>> match(text, possibilities)
    0

    >>> possibilities = ['tortoise', 'PENGUINS']
    >>> match(text, possibilities)
    1

    >>> possibilities = ['cats']
    >>> match(text, possibilities)
    -1
    """
    possibilities = [unicode(x.strip().lower()) for x in possibilities]
    text = unicode(text.strip().lower())

    if text in possibilities:
        return possibilities.index(text)

    if len(text) > 0 and text[-1] == u's':
        if(text[:-1] in possibilities):
            return possibilities.index(text[:-1])

    if len(text) > 0 and text[-1] != u's':
        if(text + u's' in possibilities):
            return possibilities.index(text + u's')

    return -1


def remove(paths):
    """
    Removes all files in the given array
    """
    for path in paths:
        os.remove(path)


def test():
    import doctest
    print('Testing...')
    doctest.testmod()
    print('Done')

if __name__ == '__main__':
    test()
