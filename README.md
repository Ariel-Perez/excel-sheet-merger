# excel-sheet-merger
A small piece of code in Python which allows to merge multiple excel sheets according to matching columns

Say for instance, you have a number of sheets in your excel files with data for the same people.
All of which have a column named SSN, which serves as an identifier.

You can then do the following:
```python
  import csvsheet

  path = ...  # Path to your files folder

  merger = csvsheet.Merger(separator=',')
  merger.merge_folder(path, ['SSN'])
```

If there are more fixed columns on your sheets, you would add them after SSN on the array so as not to have the data repeated on your output file.

The output file will concatenate all columns from your sheets which are not in the 'fixed_column' section.
To be able to easily tell them apart, it will prepend the sheet's number on each column.