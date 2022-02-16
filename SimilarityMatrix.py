import pandas as pd
import numpy as np
import time
from scipy.spatial.distance import cosine

class SimilarityMatrix:
    # constants
    RATINGS_PATH = './ratings.csv'
    MOVIES_PATH = './movies_metadata.csv'
    USER_MATRIX_PATH = './user_similarity_matrix.csv'
    MOVIE_MATRIX_PATH = './movie_similarity_matrix.csv'

    # class variables
    ratingMatrix = None
    movieMatrix = None
    userSimMatrix = None
    movieSimMatrix = None

    def __init__(self, fromScratch):
        # load matrices from file path
        if (not fromScratch):
            print('Loading similarity matrices...', flush=True)
            self.userSimMatrix = pd.read_csv(self.USER_MATRIX_PATH, index_col=0)
            self.movieSimMatrix = pd.read_csv(self.MOVIE_MATRIX_PATH, index_col=0)
            return
        
        # read in ratings data
        N = 10
        M = -1
        print('Reading ratings data...', flush=True)
        df = pd.read_csv(self.RATINGS_PATH, usecols=['userId', 'movieId', 'rating'])
        if (N != -1):
            df = df.loc[df['movieId'] <= N]
        if (M != -1):
            df = df.loc[df['userId'] <= M]
        self.ratingMatrix = df

        # read in movies metadata
        print('Reading movie metadata...', flush=True)
        df = pd.read_csv(self.MOVIES_PATH, usecols=['id', 'original_title'])
        if (N != -1):
            df = df.loc[df['id'] <= N]
        self.movieMatrix = df
        
        # similarity matrices from sparse table
        df = self.ratingMatrix.pivot_table(index='userId', columns='movieId', values='rating')
        print('\nCreating user similarity matrix...', flush=True)
        start = time.time()
        self.userSimMatrix = self.makeSimMatrix(df)
        elapsed = time.time() - start
        print('User similarity matrix created in ' + self.makeTimeString(elapsed))

        print('\nCreating movie similarity matrix...', flush=True)
        start = time.time()
        self.movieSimMatrix = self.makeSimMatrix(df.T)
        elapsed = time.time() - start
        print('Movie similarity matrix created in ' + self.makeTimeString(elapsed))

        # write similarity matrices to csv
        self.userSimMatrix.to_csv(self.USER_MATRIX_PATH, encoding='utf-8')
        self.movieSimMatrix.to_csv(self.MOVIE_MATRIX_PATH, encoding='utf-8')

        return

    def makeSimMatrix(self, df):
        N = df.shape[0]
        matrix = np.empty((N, N), dtype=np.float16)
        for i in range(0, N):
            matrix[i, i] = 1.0
            for j in range(i + 1, N):
                rows = df.iloc[[i, j]]
                rows = rows.dropna(axis=1)
                val = -1
                if (not rows.empty):
                    val = 1 - cosine(rows.iloc[0], rows.iloc[1])
                if (len(rows.columns) == 1):
                    val = 1 - (abs(rows.iat[0,0] - rows.iat[1,0]) / 5.0)
                matrix[i, j] = val
                matrix[j, i] = val
        return pd.DataFrame(matrix, index=np.arange(1, N + 1), columns=np.arange(1, N + 1))

    def makeTimeString(self, elapsed):
        minutes = int(elapsed // 60)
        minuteStr = str(minutes) + ' minute' + ('' if minutes == 1 else 's')
        seconds = round(elapsed % 60, 2)
        secondStr = str(seconds) + ' second' + ('' if seconds == 1.0 else 's')
        if (minutes == 0):
            return secondStr
        return minuteStr + ' and ' + secondStr

    def write(self, path):
        return