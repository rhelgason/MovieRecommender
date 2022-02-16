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
        # read in movies metadata
        print('Reading movie metadata...', flush=True)
        df = pd.read_csv(self.MOVIES_PATH, usecols=['id', 'original_title'])
        self.movieMatrix = df

        # read in ratings data
        print('Reading ratings data...', flush=True)
        df = pd.read_csv(self.RATINGS_PATH, usecols=['userId', 'movieId', 'rating'])

        # load matrices from file path
        if (not fromScratch):
            self.ratingMatrix = df.pivot_table(index='userId', columns='movieId', values='rating')
            print('Loading similarity matrices...', flush=True)
            self.userSimMatrix = pd.read_csv(self.USER_MATRIX_PATH, index_col=0)
            self.userSimMatrix = pd.DataFrame(self.userSimMatrix.to_numpy(), index=np.arange(1, self.userSimMatrix.shape[0] + 1), columns=np.arange(1, self.userSimMatrix.shape[0] + 1))
            self.movieSimMatrix = pd.read_csv(self.MOVIE_MATRIX_PATH, index_col=0)
            self.movieSimMatrix = pd.DataFrame(self.movieSimMatrix.to_numpy(), index=np.arange(1, self.movieSimMatrix.shape[0] + 1), columns=np.arange(1, self.movieSimMatrix.shape[0] + 1))
            return

        # dimensions
        N = 9000
        M = 900
        if (N != -1):
            df = df.loc[df['movieId'] <= N]
        if (M != -1):
            df = df.loc[df['userId'] <= M]
        self.ratingMatrix = df.pivot_table(index='userId', columns='movieId', values='rating')
        
        # similarity matrices from sparse table
        print('\nCreating user similarity matrix...', flush=True)
        start = time.time()
        self.userSimMatrix = self.makeSimMatrix(self.ratingMatrix)
        elapsed = time.time() - start
        print('User similarity matrix created in ' + self.makeTimeString(elapsed))

        print('\nCreating movie similarity matrix...', flush=True)
        start = time.time()
        self.movieSimMatrix = self.makeSimMatrix(self.ratingMatrix.T)
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

    def similarUser(self):
        input1 = 'What is your user ID? '
        id = input(input1)
        while (not id.isnumeric() or int(id) < 1 or int(id) > self.userSimMatrix.shape[0]):
            if (not id.isnumeric()):
                id = input(input1)
            if (int(id) <= 0):
                id = input('ID must be greater than or equal to 1. ' + input1)
            elif (int(id) > self.userSimMatrix.shape[0]):
                id = input('ID must be less than or equal to ' + str(self.userSimMatrix.shape[0]) + '. ' + input1)
            
        # find most similar users
        M = 30
        if (M >= self.userSimMatrix.shape[0]):
            M = self.userSimMatrix.shape[0] - 1
        topUsers = self.userSimMatrix.nlargest(M + 1, [int(id)])
        topUsers = topUsers.drop([int(id)])

        # average their movie ratings
        userIds = []
        for userId in topUsers.index:
            userIds.append(userId)
        averageRatings = self.ratingMatrix.iloc[userIds].mean(axis=0)

        # find best rated movies
        N = 5
        if (N >= averageRatings.shape[0]):
            N = averageRatings.shape[0] - 1
        # not sure why some aren't found, N increased for now
        topMovies = averageRatings.nlargest(averageRatings.shape[0])

        # print data
        print('The top ' + str(N) + ' movie' + ('' if N == 1 else 's') + ' suggested for you are:')
        i = 0
        for movieId in topMovies.index:
            if (i >= N):
                continue
            row = self.movieMatrix.loc[self.movieMatrix['id'] == movieId]
            if (row.empty):
                continue
            i += 1
            print('\t' + str(i) + '. ' + row.iloc[0]['original_title'])
    
    def similarMovie(self):
        input1 = 'What is the ID of the movie you would like similar recommendations for? '
        id = input(input1)
        while (not id.isnumeric() or int(id) < 1 or int(id) > self.movieSimMatrix.shape[0]):
            if (not id.isnumeric()):
                id = input(input1)
            elif (int(id) <= 0):
                id = input('ID must be greater than or equal to 1. ' + input1)
            elif (int(id) > self.movieSimMatrix.shape[0]):
                id = input('ID must be less than or equal to ' + str(self.movieSimMatrix.shape[0]) + '. ' + input1)
        
        # find movie title if exists
        titleRow = self.movieMatrix.loc[self.movieMatrix['id'] == int(id)]
        if (titleRow.empty):
            print('Error. Movie ID not found in movie metadata file.')
            return
        title = titleRow.iloc[0]['original_title']
            
        # find most similar movies
        N = 5
        if (N >= self.movieSimMatrix.shape[0]):
            N = self.movieSimMatrix.shape[0] - 1
        # not sure why some aren't found, N increased for now
        topMovies = self.movieSimMatrix.nlargest(self.movieSimMatrix.shape[0], [int(id)])
        topMovies = topMovies.drop([int(id)])

        # print data
        print('The top ' + str(N) + ' movie' + ('' if N == 1 else 's') + ' rated most similar to ' + title + ' are:')
        i = 0
        for movieId in topMovies.index:
            if (i >= N):
                continue
            row = self.movieMatrix.loc[self.movieMatrix['id'] == movieId]
            if (row.empty):
                continue
            i += 1
            print('\t' + str(i) + '. ' + row.iloc[0]['original_title'])