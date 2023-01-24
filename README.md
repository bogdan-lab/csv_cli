# TableCLI

This repository aggregates CLI implementations for some simple table operations.
It is expected that table is saved csv format with some delimiter.
Currently utility supports the following operations:
- sorting table rows based on the column(s) content


## Sorting utility

One can sort table content using the `sort` sub-command of the utility.
The utility sorts the table content in a stable way.
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
./csv sort -d ";" --c_index 0 -as time  -t_fmt "%Y-%m-%d" -f test.csv
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
./csv sort -d ";" --c_name String -as string --c_name Int -as number --reverse -f test.csv
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

If some values in the column according to which we are trying to sort the table rows is not convertible to the requested type it will be pushed to the bottom of the sorted table in the stable way.
The same will happen with the NaN values in the numeric column according to which table is being sorted.
For example, let us sort `test.csv` content by column 0.
`test.csv` content:
```
5; a
-; b
; d
0; v
nan; and
definetely not a number; num
```
The command:
```
./csv sort -d ";" --no_header -ci 0 -f test.csv
```
Where,
- `--no_header` indicates that table does not have any header
- `-ci` shortcut argument name for column index
- we do not set column type explicitly since by default it will be `number`

The output of the command will be:
```
0; v
5; a
-; b
; d
nan; and
definetely not a number; num
```
Note that relative order of rows with not convertible values is preserved.

## Show utility

This utility allows to selectively display certain column and rows from the table.
It will not modify the existing table in any way.
In order make the output handy, utility will display updated header (if one exists) by default for any kind of selection.

### Show selected columns
In order to select columns from the table user has to provide the correct column delimiter.
Also if one expects the utility to process the table header correctly one has to keep `--no_header` flag value valid.
There are three ways to select columns which are needed to be displayed:

1. User can select the number of first or last columns to display using arguments `-c_head` and `-c_tail` respectively.
The first columns are calculated from the leftmost column and last - from the rightmost.
2. User can select the range of columns.
It can be done using arguments `--from_col` (`-fc`) and `--to_col` (`-tc`).
The first argument sets the index of the first column in the range.
This column will be included.
The second argument sets the column index which corresponds to the end of the range and which will be excluded.
Note that column numeration starts from `0`.
User can set several ranges by defining them one after another in the command line 
(`.... -fc 3 -tc 10 -fc 20 -tc 40 ....`)
3. User can select particular columns to be displayed. 
This can be done by arguments `-c_name`(`-cn`) and `-c_index`(`-ci`).
The first argument allows to select columns by name, when the secnd one defines indexes of columns which will be displayed.
One can mix these arguments and use each of them several times in order to select several columns.
Column indexing starts from `0`.

User can mix all three ways for selecting columns in one queue, the utility will guarantee that even if defined ranges intersect each column will be displayed only once.
If one does not set any restriction for column selection - all columns will be displayed.
The order of all selected columns will be the same as it is in the original table.

Let's look at few examples.
Let `test.csv` content be the following:
```
Date;String;Int;Double
2010-01-04;two;1;5.0
2011-05-23;one;2;4.5
2008-03-12;two;-14;3.7
2016-12-07;one;-4;0.1
2010-01-01;hello;2;9.8
2011-07-11;world;3;2.56
2001-04-28;!;3;13.2
```
Then the following commands will have results listed below
```
./csv show --c_head 1 --c_tail 1 -d ';' -f test.csv
```
```
Date;Double
2010-01-04;5.0
2011-05-23;4.5
2008-03-12;3.7
2016-12-07;0.1
2010-01-01;9.8
2011-07-11;2.56
2001-04-28;13.2
```
```
./csv show -fc 1 -tc 3 -d ';' -f test.csv
```
```
String;Int
two;1
one;2
two;-14
one;-4
hello;2
world;3
!;3
```
```
./csv show --c_head 1 -cn Int -d ';' -f test.csv
```
```
Date;Int
2010-01-04;1
2011-05-23;2
2008-03-12;-14
2016-12-07;-4
2010-01-01;2
2011-07-11;3
2001-04-28;3
```

### Show selected rows
Similarly to the column interface user can select rows which will be displayed.
Note that if table has header (and `--no_header` flag is set correctly) then header will not take part in row selection process and it will be present in all outputs, unless user requests to hide it, using `--hide_header`.
There are also three ways to select rows which will be displayed:

1. User can select the number of top and bottom rows to display using arguments `-r_head` and `-c_tail`.
Note that header, if one exists, will not be considered as a row.
2.User can select the of rows.
It can be done using arguments `--from_row` (`-fr`) and `--to_row` (`-tr`).
The first argument sets the index of the first row in the range, which will be included in the output.
The second argument defines the last row index in the range.
The row with this index will not be included into the range.
Index of the first row (beneath the header, if one exists) is `0`.
User can set several ranges by defining them one after another in the command line 
(`... -fr 1 -tr 5 -fr 10 -tr 15 ...`)
3.User can select particular rows by their indexes.
It can be done, using argument `--r_index` (`-ri`).
One also can select several rows using this argument repeatedly.

User can mix all three ways for selecting rows in one call utility will display union of defined ranges.
If user does not set any restriction for row selection - all rows will be selected and displayed.

Let's look at few examples
Again, let `test.csv` content be the following:
```
Date;String;Int;Double
2010-01-04;two;1;5.0
2011-05-23;one;2;4.5
2008-03-12;two;-14;3.7
2016-12-07;one;-4;0.1
2010-01-01;hello;2;9.8
2011-07-11;world;3;2.56
2001-04-28;!;3;13.2
```
Then the following commands will have results listed below
```
./csv show --r_head 1 --r_tail 1 -d ';' -f test.csv
```
```
Date;String;Int;Double
2010-01-04;two;1;5.0
2001-04-28;!;3;13.2
```
```
./csv show -fr 2 -tr 4 -d ';' -f test.csv
```
```
Date;String;Int;Double
2008-03-12;two;-14;3.7
2016-12-07;one;-4;0.1
```
```
./csv show -ri 1 -ri 3 -ri 5 -d ';' -f test.csv
```
```
Date;String;Int;Double
2011-05-23;one;2;4.5
2016-12-07;one;-4;0.1
2011-07-11;world;3;2.56
```

User can mix row and column selections in a single call in order to minimize his focus area when studying the table.
Also, there is a invertion flag `--except`.
If this flag is set to `true` utility will display all rows and columns in the table which DO NOT sutisfy selection requirements in the call.
For example, `test.csv` content:
```
Date;String;Int;Double
2010-01-04;two;1;5.0
2011-05-23;one;2;4.5
2008-03-12;two;-14;3.7
2016-12-07;one;-4;0.1
2010-01-01;hello;2;9.8
2011-07-11;world;3;2.56
2001-04-28;!;3;13.2
```
Then selecting everythin except the middle column and the middle row will look like this:
```
./csv show --except -cn String -ri 3 -d ';' -f test.csv
```
```
Date;Int;Double
2010-01-04;1;5.0
2011-05-23;2;4.5
2008-03-12;-14;3.7
2010-01-01;2;9.8
2011-07-11;3;2.56
2001-04-28;3;13.2
```