#!/usr/bin/python

# Use: Diff two MARC files.
#   Specify tags to exclude from comparison in exclude list.
#   Output is a tab-delimited file containing bib id, context, delta, and value for each diff.
#   Context is 'record', 'ldr/' followed by the character position, or the tag for the field.
#   Delta is '-' if unique to file1, '+' if unique to file2, or ' ' if common to both (not written to output).

# Update
file1 = 'first.mrc'
file2 = 'second.mrc'
outfile = 'out.txt'
exclude = ['901', '902', '905', '907']

f1 = open(file1, 'r')
f2 = open(file2, 'r')
out = open(outfile, 'w')

# Functions
def extract_records(marc):
    """Extract records from open MARC file. Return dictionary with bib id as key."""
    d = {}
    records = map(lambda x: x + '\x1d', marc.read()[:-1].split('\x1d'))
    for r in records:
        d[r.split('\x1e')[1]] = r
    return d

def diff_records(d1, d2):
    """Return diff of records in dictionaries as dictionary with delta as key."""
    d1_keys = set(d1.iterkeys())
    d2_keys = set(d2.iterkeys())
    return {' ': d1_keys & d2_keys, '-': d1_keys - d2_keys, '+': d2_keys - d1_keys}

def diff_leader(r1, r2):
    """Return diff of leaders as dictionary with position as key.
    Exclude record length (ldr/00-04) and base address of data (ldr/12-16) from comparison.
    """
    d = {}
    exclude = range(0, 5) + range(12, 17)
    ldr = enumerate(zip(r1[0:24], r2[0:24]))
    for pos, char in ldr:
        if pos not in exclude and char[0] != char[1]:
            d[pos] = char
    return d

def diff_fields(r1, r2, exclude):
    """Return diff of fields in two records as list of tuples containing tag, delta, and value.
    Exclude fields with designated tags from comparison.
    """
    f1 = []
    f2 = []
    comm = []
    d = []
    
    base1 = int(r1[12:17])
    dir1 = r1[24:base1]
    for i in range(0, len(dir1) - 1, 12):
        tag = dir1[i:i + 3]
        length = int(dir1[i + 3:i + 7])
        address = base1 + int(dir1[i + 7:i + 12])
        if tag not in exclude:
            f1.append((tag, r1[address:address + length]))
    base2 = int(r2[12:17])
    dir2 = r2[24:base2]
    for i in range(0, len(dir2) - 1, 12):
        tag = dir2[i:i + 3]
        length = int(dir2[i + 3:i + 7])
        address = base2 + int(dir2[i + 7:i + 12])
        if tag not in exclude:
            f2.append((tag, r2[address:address + length]))
    for f in f1:
        if f in f2:
            comm.append(f)
    for f in comm:
        f1.remove(f)
        f2.remove(f)
    for f in f1:
        d.append((f[0], '-', f[1]))
    for f in f2:
        d.append((f[0], '+', f[1]))
    d.sort(key = lambda x: x[0])
    return d

def format_output(bibid, context, delta, value):
    """Return output of comparison as formatted string."""
    fields = [bibid, context, delta, value]
    return '\t'.join(fields) + '\r\n'

# Write headers
out.write(format_output('bibid', 'context', 'delta', 'value'))

# Extract records
d1 = extract_records(f1)
d2 = extract_records(f2)

# Compare files
diff_r = diff_records(d1, d2)
for b in diff_r['-']:
    out.write(format_output(b, 'record', '-', ''))
for b in diff_r['+']:
    out.write(format_output(b, 'record', '+', ''))

# Compare records
for b in diff_r[' ']:
    r1 = d1[b]
    r2 = d2[b]
    diff_l = diff_leader(r1, r2)
    if diff_l:
        for k, v in diff_l.iteritems():
            out.write(format_output(b, 'ldr/' + str(k), '-', str(v[0])))
            out.write(format_output(b, 'ldr/' + str(k), '+', str(v[1])))
    diff_f = diff_fields(r1, r2, exclude)
    if diff_f:
        for f in diff_f:
            out.write(format_output(b, f[0], f[1], f[2]))

f1.close()
f2.close()
out.close()



