# return list of file lines with specified size
def splitFile(file, size):
    # return file.readlines(size)
    lst = []
    fbytes = file.read(size)
    while fbytes:
        lst.append(fbytes)
        fbytes = file.read(size)
    return lst


def printspace(lst):
    for l in lst:
        print l
        print "\n\n"