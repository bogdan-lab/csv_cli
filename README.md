# TableCLI

This repository aggregates CLI implementations for some simple table operations.
It is expected that table is saved csv format with some delimiter.
Currently utility supports the following operations:
- sorting table rows based on the column(s) content


## Sorting utility

One can sort table content using the `sort` sub-command of the utility.
Here are several examples of such sorting.

### Sort according to a single column
You can sort table rows according to the values in certain column.
Values in column will be compared according to column type provided by user.
There are 3 available column types: `time`, `string` and `number`.
For example, let us sort `test.csv` content by the `Date` column.

`test.csv` content:
```
Date;String;Int;Double
2010-01-04;one;1;5.0
2011-05-23;two;2;4.5
2008-03-12;-;3;3.7
2016-12-07;abcd;-4;0.1
```
We can sort table rows with command
```
python3 table.py sort -d ";" --c_index 0 -as time  -t_fmt "%Y-%m-%d" -f test.csv
```
Where,
- `-d` defines a delimiter used in the table
- `--c_index` defines the column index according to which data will be sorted. Column indexing starts with 0.
- `-as` defines type of the column according to which table rows will be sorted
- `-t_fmt` defines the time format which was used in the column of the interest
- `-f` defines the file which contains the table.

The output of the command will be 
```
Date;String;Int;Double
2008-03-12;-;3;3.7
2010-01-04;one;1;5.0
2011-05-23;two;2;4.5
2016-12-07;abcd;-4;0.1
```

### Sort according to multiple columns

One can set several columns as those according to which we want to sort the table.
In such case user has to specify type for each of those columns.
As a result of such sorting, table rows will be sorted by the values in the first column given by user.
If there are rows with the same values in that column, they will be sorted according to the second column given by user.
And so on.

For example, let us sort `test.csv` content by columns `String` and `Int`.
`test.csv` content:
```
Date;String;Int;Double
2010-01-04;two;1;5.0
2011-05-23;one;2;4.5
2008-03-12;two;-14;3.7
2016-12-07;one;-4;0.1
```
The command:
```
python3 table.py sort -d ";" --c_name String -as string --c_name Int -as number --reverse -f test.csv
```
Where,
- `--c_name` refers to the column by its name in header. Note that if there is no header this option is not available.
- `--reverse` defines the order of sorted row sequence as descending.

Note that we define type of each column separately.
The output of the command will be
```
Date;String;Int;Double
2010-01-04;two;1;5.0
2008-03-12;two;-14;3.7
2011-05-23;one;2;4.5
2016-12-07;one;-4;0.1
```

### Sort according to numeric column with NaN values

