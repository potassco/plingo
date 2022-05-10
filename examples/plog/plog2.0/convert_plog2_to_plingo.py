import argparse

parser = argparse.ArgumentParser(description='Convert plog2.0 program to plingo format.')
parser.add_argument('--input', '-i', type=str,
                    help='input file')

args = parser.parse_args()

if __name__ == '__main__':
    with open(args.input, 'r') as fp:
        original_lines = fp.read().split('\n')

    indices = [original_lines.index(x) for x in ["sorts", "attributes","statements"]]+[-1]
    sorts, attributes, statements = [original_lines[indices[i]: indices[i+1]] for i in range(3)]
    
    converted_program = original_lines[:indices[0]]
    for s in sorts:
        if s == 'sorts':
            converted_program.append('% Sorts')
        elif s.startswith('%') or s == '':
            converted_program.append(s)
        elif s.startswith('#'):
            sort, terms = s.split('=')
            sort = sort.strip()[1:]
            terms = terms.strip()[1:-2].split(',')
            converted_program.append(f'{sort}({";".join(terms)}).')

    for a in attributes:
        if a == 'attributes':
            converted_program.append('% Attributes')
        elif a == '':
            continue
        else:
            converted_program.append(f'% {a}')
    converted_program.append('')

    for l in converted_program:
        print(l)
