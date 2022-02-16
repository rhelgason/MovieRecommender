from asyncio.windows_events import NULL
from SimilarityMatrix import SimilarityMatrix

def main():
    # create similarity matrix
    val = input('Would you like to recreate the similarity matrices [y/n]? ').lower()
    while (val != 'n' and val != 'y'):
        val = input('Would you like to recreate the similarity matrices [y/n]? ').lower()
    mat = SimilarityMatrix(True if val == 'y' else False)

if __name__ == '__main__':
    main()