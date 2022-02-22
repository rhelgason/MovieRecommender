from SimilarityMatrix import SimilarityMatrix

def main():
    # create similarity matrices
    input1 = 'Would you like to recreate the similarity matrices [y/n]? '
    val = input(input1).lower()
    while (val != 'n' and val != 'y'):
        val = input(input1).lower()
    mat = None
    if (val == 'n'):
        mat = SimilarityMatrix(False)
    else:
        input2 = 'Enter dimension for N (0 for all movies): '
        n = input(input2)
        while (not n.isnumeric()):
            n = input(input2)
        n = int(n)
        input3 = 'Enter dimension for M (0 for all users): '
        m = input(input3)
        while (not m.isnumeric()):
            m = input(input3)
        m = int(m)
        mat = SimilarityMatrix(True, -1 if n == 0 else n, -1 if m == 0 else m)

    # create recommendations
    print()
    input4 = 'Would you like to find movies you may like [1], movies similar to another [2], or quit [q]? '
    while (val != 'q'):
        val = input(input4).lower()
        while (val != '1' and val != '2' and val != 'q'):
            val = input(input4).lower()
        if (val == 'q'):
            break

        if (val == '1'):
            mat.similarUser()
        elif (val == '2'):
            mat.similarMovie()
        print()

if __name__ == '__main__':
    main()