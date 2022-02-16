from asyncio.windows_events import NULL
from SimilarityMatrix import SimilarityMatrix

def main():
    # create similarity matrices
    input1 = 'Would you like to recreate the similarity matrices [y/n]? '
    val = input(input1).lower()
    while (val != 'n' and val != 'y'):
        val = input(input1).lower()
    mat = SimilarityMatrix(True if val == 'y' else False)

    # create recommendations
    print()
    input2 = 'Would you like to find movies you may like [1], movies similar to another [2], or quit [q]? '
    while (val != 'q'):
        val = input(input2).lower()
        while (val != '1' and val != '2' and val != 'q'):
            val = input(input2).lower()
        if (val == 'q'):
            break

        if (val == '1'):
            mat.similarUser()
        elif (val == '2'):
            mat.similarMovie()
        print()

if __name__ == '__main__':
    main()