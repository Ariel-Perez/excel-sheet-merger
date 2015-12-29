#!/usr/bin/python
# -*- coding: utf8 -*-
import glob
import codecs


def get_files(path, extensions=None):
    """
    Gets the paths to files in a given path
    """
    if path[-1] is not '/' and path[-1] is not '\\':
        path = path + '/'

    return glob.glob('%s*%s' % (path, ('[%s]' % '||'.join(extensions))
                     if extensions is not None else ''))


def write_file(path, content):
    """
    Writes the content to a file
    """
    with open(path, 'w') as f:
        encoded_content = content.encode('utf-8')
        f.write(encoded_content)


def read_file(path):
    """
    Retrieves the content of a file
    """
    with codecs.open(path, encoding='utf-8') as f:
        text = f.read()

    return text


def flatten(arr):
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
        return ','.join([flatten(x) for x in arr])


def quote(data):
    """
    Encloses all values in a CSV in doble quotes.

    >>> d = 'Hello, world'
    >>> quote(d)
    '"Hello"," world"'
    """
    return '"%s"' % data.replace(',', '","')


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


def split(line):
    """
    Splits a line of CSV into its values and unquotes it.

    >>> line = 'Hello,"world"'
    >>> split(line)
    ['Hello', 'world']
    """
    data = line.split(',')
    return [unquote(x) for x in data]


def match(text, possibilities):
    """
    Match a text to one of the possible options
    Accepts minor mismatches such as pluralization with appended 's'
    and lower/upper casing

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
    lower_poss = [x.lower() for x in possibilities]
    lower_text = text.lower()

    if lower_text in lower_poss:
        return lower_poss.index(lower_text)

    if len(lower_text) > 0 and lower_text[-1] == 's':
        if(lower_text[:-1] in lower_poss):
            return lower_poss.index(lower_text[:-1])

    if len(lower_text) > 0 and lower_text[-1] != 's':
        if(lower_text + 's' in lower_poss):
            return lower_poss.index(lower_text + 's')

    return -1


def test():
    import doctest
    print('Testing...')
    doctest.testmod()
    print('Done')
