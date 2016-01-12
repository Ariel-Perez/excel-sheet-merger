#!/usr/bin/python
# -*- coding: utf8 -*-
import splitter
import merger
import editor
import easyio


def juan_bohon(folders, output):
    fixed_columns = [u'RUT',
                     u'APELLIDO PATERNO',
                     u'APELLIDO MATERNO',
                     u'NOMBRE',
                     u'CAREER',
                     u'YEAR',
                     u'SEMESTER',
                     u'SHEET',
                     u'?']

    merge_columns = [u'1 NOTA',
                     u'1 % ASISTENCIA',
                     u'2 NOTA',
                     u'2 % ASISTENCIA',
                     u'3 NOTA',
                     u'3 % ASISTENCIA',
                     u'4 NOTA',
                     u'4 % ASISTENCIA',
                     u'5 NOTA',
                     u'5 % ASISTENCIA',
                     u'6 NOTA',
                     u'6 % ASISTENCIA',
                     u'7 NOTA',
                     u'7 % ASISTENCIA']

    ignore_columns = [u'Nº']

    remove_content = [u'Y = RETIRADO',
                      u'S = SITUACION PENDIENTE',
                      u'R = REPROBADOS',
                      u'P = APROBADO',
                      u'NOTA',
                      u'% ASISTENCIA',
                      u'LA SERENA',
                      u'Observaciones:']

    custom_headers = {0: u'Nº',
                      1: u'APELLIDO PATERNO',
                      2: u'APELLIDO MATERNO',
                      5: u'1 NOTA',
                      6: u'1 % ASISTENCIA',
                      7: u'2 NOTA',
                      8: u'2 % ASISTENCIA',
                      9: u'3 NOTA',
                      10: u'3 % ASISTENCIA',
                      11: u'4 NOTA',
                      12: u'4 % ASISTENCIA',
                      13: u'5 NOTA',
                      14: u'5 % ASISTENCIA',
                      15: u'6 NOTA',
                      16: u'6 % ASISTENCIA',
                      17: u'7 NOTA',
                      18: u'7 % ASISTENCIA',
                      -1: u'?'}

    custom_columns = [(u'year', '(?<=[a-zA-Z]{3}\d)\d{4}'),
                      (u'semester', '(?<=[a-zA-Z]{3})\d{1}'),
                      (u'sheet', '\d+(?=.csv)'),
                      (u'career', '[a-zA-Z]{3}')]

    expect_new_columns = False
    new_columns_regex = ''

    process(folders, output,
            fixed_columns, merge_columns, ignore_columns,
            remove_content, custom_headers, custom_columns,
            expect_new_columns, new_columns_regex, separator=u',')


def process(folders, output,
            fixed_columns, merge_columns, ignore_columns,
            remove_content, custom_headers, custom_columns,
            expect_new_columns, new_columns_regex, separator=u','):
    ed = editor.Editor()
    sp = splitter.Splitter(separator)
    mg = merger.Merger(separator=separator,
                       fixed_columns=fixed_columns,
                       ignore_columns=ignore_columns,
                       merge_columns=merge_columns,
                       expect_new_columns=expect_new_columns,
                       new_columns_regex=new_columns_regex)

    ed.remove_content_in_processing(remove_content)
    ed.remove_empty_columns_in_processing()
    ed.trim_in_processing()
    ed.expand_rows_in_processing()
    ed.skip_files_in_processing(output)
    ed.set_headers_in_processing(custom_headers)

    for column in custom_columns:
        ed.add_columns_in_processing(*column)

    ed.collapse_headers_in_processing(
        fixed_columns, merge_columns, ignore_columns)

    for folder in folders:
        # csvs = sp.split_folder(folder)
        # ed.process(folder)
        mg.merge_folder(folder, output)
        # for files in csvs:
        #     easyio.remove(csvs[files])


def tryout(folder, output):
    fixed_columns = [u'RUT']
    merge_columns = []
    ignore_columns = []
    remove_content = []
    custom_headers = {}
    custom_columns = []
    expect_new_columns = True
    new_columns_regex = '(?<=- )\d+(?=.csv)'

    process(folders, output,
            fixed_columns, merge_columns, ignore_columns,
            remove_content, custom_headers, custom_columns,
            expect_new_columns, new_columns_regex, separator=u',')


def test(folder, output):
    fixed_columns = [u'RUT',
                     u'DV',
                     u'PATERNO',
                     u'MATERNO',
                     u'NOMBRE',
                     u'CARRERA',
                     u'YEAR']

    merge_columns = [u'JORNADA',
                     u'SECCION',
                     u'IDJORNADA']

    ignore_columns = [u'INSTITUCION',
                      u'SEDE']

    remove_content = []

    custom_headers = {}

    custom_columns = [(u'year', '(?<=TEST )\d{4}(?=-\d+)')]

    expect_new_columns = True
    new_columns_regex = '(?<=- )\d+(?=.csv)'

    process(folders, output,
            fixed_columns, merge_columns, ignore_columns,
            remove_content, custom_headers, custom_columns,
            expect_new_columns, new_columns_regex, separator=u',')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--folders',
                        dest='folders',
                        help='Folders to process',
                        required=True)

    parser.add_argument('--output',
                        dest='output',
                        help='Output file',
                        required=True)

    parser.add_argument('--fixed_columns',
                        dest='fixed_columns',
                        help='Columns to use to match data across sheets',
                        default=u'')

    parser.add_argument('--ignore',
                        dest='ignore',
                        help='Columns to step over. Not implemented yet',
                        default=u'')

    parser.add_argument('--separator',
                        dest='separator',
                        help='Separator character for CSV',
                        default=u',')

    parser.add_argument('--juan_bohon',
                        dest='juan_bohon',
                        help='Whether to run the script for Juan Bohon data',
                        default=False)

    parser.add_argument('--test',
                        dest='test',
                        help='Whether to run the script for TEST data',
                        default=False)

    args = parser.parse_args()
    # [c.strip() for c in args.fixed_columns.split(',')]
    # [c.strip() for c in args.ignore.split(',')]

    folders = args.folders.split(',')
    output = args.output

    if args.juan_bohon:
        juan_bohon(folders, output)

    elif args.test:
        test(folders, output)

    else:
        tryout(folders, output)
