#!/usr/bin/python
# -*- coding: utf8 -*-
import splitter
import merger
import editor
import os
import easyio


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--folders',
                        dest='folders',
                        help='Folders to process',
                        default='')

    parser.add_argument('--fixed_columns',
                        dest='fixed_columns',
                        help='Columns to use to match data across sheets',
                        default='')

    parser.add_argument('--ignore_columns',
                        dest='ignore_columns',
                        help='Columns to step over. Not implemented yet',
                        default='')

    parser.add_argument('--separator',
                        dest='separator',
                        help='Separator character for CSV',
                        default=',')

    parser.add_argument('--termination',
                        dest='termination',
                        help='Regexp for termination line',
                        default='^,*$')

    args = parser.parse_args()
    fixed_columns = ['RUT',
                     'APELLIDO PATERNO',
                     'APELLIDO MATERNO',
                     'NOMBRE',
                     'YEAR',
                     'SEMESTER',
                     'SHEET',
                     '?']
    # [c.strip() for c in args.fixed_columns.split(',')]
    ignore_columns = [c.strip() for c in args.ignore_columns.split(',')]

    folders = args.folders.split(',')

    # SAMPLE:
    # python csvsheet.py --folders files --fixed_columns
    # "RUT, DV, PATERNO, MATERNO, NOMBRES, CARRERA, JORNADA, SECCION"
    ed = editor.Editor()
    sp = splitter.Splitter(',')
    mg = merger.Merger(separator=args.separator,
                       fixed_columns=fixed_columns,
                       ignore_columns=ignore_columns)

    ed.remove_content_in_processing(['Y = RETIRADO',
                                     'S = SITUACION PENDIENTE',
                                     'R = REPROBADOS',
                                     'P = APROBADO'])
    ed.trim_in_processing()
    ed.expand_rows_in_processing()
    ed.set_headers_in_processing({1: 'APELLIDO PATERNO',
                                  2: 'APELLIDO MATERNO',
                                  -1: '?'})
    ed.add_columns_in_processing('year', '(?<=[a-zA-Z]{3}\d)\d{4}')
    ed.add_columns_in_processing('semester', '(?<=[a-zA-Z]{3})\d{1}')
    ed.add_columns_in_processing('sheet', '\d+(?=.csv)')
    ed.collapse_headers_in_processing(fixed_columns)

    for folder in folders:
        csvs = sp.split_folder(folder)
        ed.process(folder)
        # mg.merge_folder(folder, os.path.join(folder, 'resultado.csv'))

        # for files in csvs:
        #     easyio.remove(csvs[files])
