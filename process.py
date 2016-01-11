#!/usr/bin/python
# -*- coding: utf8 -*-
import splitter
import merger
import editor
import os


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--folders',
                        dest='folders',
                        help='Folders to process',
                        default=u'')

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

    args = parser.parse_args()
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
    # [c.strip() for c in args.fixed_columns.split(',')]
    # [c.strip() for c in args.ignore.split(',')]

    folders = args.folders.split(',')

    ed = editor.Editor()
    sp = splitter.Splitter(u',')
    mg = merger.Merger(separator=args.separator,
                       fixed_columns=fixed_columns,
                       ignore_columns=ignore_columns,
                       merge_columns=merge_columns)

    ed.remove_content_in_processing([u'Y = RETIRADO',
                                     u'S = SITUACION PENDIENTE',
                                     u'R = REPROBADOS',
                                     u'P = APROBADO',
                                     u'NOTA',
                                     u'% ASISTENCIA',
                                     u'LA SERENA',
                                     u'Observaciones:'])
    ed.remove_empty_columns_in_processing()
    ed.trim_in_processing()
    ed.expand_rows_in_processing()
    ed.set_headers_in_processing({0: u'Nº',
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
                                  -1: u'?'})
    ed.add_columns_in_processing(u'year', '(?<=[a-zA-Z]{3}\d)\d{4}')
    ed.add_columns_in_processing(u'semester', '(?<=[a-zA-Z]{3})\d{1}')
    ed.add_columns_in_processing(u'sheet', '\d+(?=.csv)')
    ed.add_columns_in_processing(u'career', '[a-zA-Z]{3}')
    ed.collapse_headers_in_processing(fixed_columns,
                                      merge_columns,
                                      ignore_columns)

    for folder in folders:
        csvs = sp.split_folder(folder)
        ed.process(folder)
        mg.merge_folder(folder, os.path.join(folder, 'resultado.csv'))

        import easyio
        for files in csvs:
            easyio.remove(csvs[files])
