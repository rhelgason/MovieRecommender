from SimilarityMatrix import SimilarityMatrix

def main():
    # define pairs of N and M
    pairs = []
    N = [10, 30, 50, 100, 200, 500, 1000, 3000, -1]
    M = [10, 30, 50, 100, 150, 200, 300, 500, -1]
    for n in N:
        for m in M:
            pairs.append((n, m))
    
    for pair in pairs:
        print('\nTesting with N=' + str(pair[0]) + ' and M=' + str(pair[1]), flush=True)
        mat = SimilarityMatrix(True, pair[0], pair[1])

if __name__ == '__main__':
    main()