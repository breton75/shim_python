import struct
import sys
import array as arr

def read_header(file_name, hstruct):
    try:
        f = open(file_name, 'rb')

        h = struct.unpack(hstruct, f.read(struct.calcsize(hstruct)))
        f.close()

    except Exception as E:
        print('error in function read_header(): ', file=sys.stderr, end='')
        print(E, file=sys.stderr)
        return None

    return h


def read_file(file_name, dtype, offset, count):
    try:

        f = open(file_name, 'rb')
        f.seek(offset)
        a = arr.array(dtype)
        a.fromfile(f, count)

        if count != len(a):
            raise ValueError()

        f.close()

    except (OSError) as E:
        print('error in function read_file(): ', file=sys.stderr, end='')
        print(E, file=sys.stderr)
        return None

    except (ValueError, EOFError):
        print('error in function read_file(): wrong size: estimated %i, got %i' % (count, len(a)), file=sys.stderr)
        f.close()
        return None

    return a