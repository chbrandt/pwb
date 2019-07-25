with open('blazarlist.txt') as fp:
    txt = fp.readlines()

txt_clean = []
for line in txt:
    xf = {}
    fields = line.split()
    for f in fields[::-1]:
        if f != 'Y':
            break
        fields.pop()
    nfields = len(fields)
    xf['nprojs'] = fields.pop()
    c = [fields.pop() for i in range(3)]
    c.reverse()
    xf['dec'] = ':'.join(c)
    c = [fields.pop() for i in range(3)]
    c.reverse()
    xf['ra'] = ':'.join(c)
    xf['j2000'] = fields.pop(0)
    xf['b1950'] = fields.pop(0)
    xf['name'] = ' '.join(fields)
    if len(xf['name'].strip()) == 0:
        print(xf)
        continue
    line_clean = ','.join([xf[c] for c in ['name', 'ra', 'dec', 'j2000', 'b1950', 'nprojs']])
    txt_clean.append(line_clean)

with open('blazarlist.csv', 'w') as fp:
    for line in txt_clean:
        fp.write(line+'\n')
