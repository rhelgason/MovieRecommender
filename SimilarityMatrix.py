import pandas as pd
import numpy as np
import time
from scipy.spatial.distance import cosine
import unicodedata

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

    def __init__(self, fromScratch, N=-1, M=-1):
        # read in movies metadata
        print('Reading movie metadata...', flush=True)
        self.movieMatrix = pd.read_csv(self.MOVIES_PATH, usecols=['id', 'original_title'])
        self.movieMatrix['id'] = self.movieMatrix[pd.to_numeric(self.movieMatrix['id'], errors='coerce', downcast='integer').notnull()]
        self.movieMatrix['original_title'] = self.movieMatrix['original_title'].str.encode('ascii', 'replace').str.decode('ascii')
        invalidMovies = self.movieMatrix[self.movieMatrix.isna().any(axis=1)].index.tolist()
        self.movieMatrix = self.movieMatrix.dropna()
        self.movieMatrix = self.movieMatrix.astype({'id': 'int', 'original_title': 'string'})
        validMovies = list(map(int, self.movieMatrix['id'].tolist()))

        # read in ratings data
        print('Reading ratings data...', flush=True)
        self.ratingMatrix = pd.read_csv(self.RATINGS_PATH, usecols=['userId', 'movieId', 'rating'])
        self.ratingMatrix = self.ratingMatrix.astype({'userId': 'int', 'movieId': 'int', 'rating': 'float'})
        for movie in invalidMovies:
            self.ratingMatrix = self.ratingMatrix.drop(self.ratingMatrix[self.ratingMatrix['movieId'] == movie].index)

        # load matrices from file path
        if (not fromScratch):
            self.ratingMatrix = self.ratingMatrix.pivot_table(index='userId', columns='movieId', values='rating')
            self.ratingMatrix = self.ratingMatrix[self.ratingMatrix.columns.intersection(validMovies)]
            print('Loading similarity matrices...', flush=True)
            self.userSimMatrix = pd.read_csv(self.USER_MATRIX_PATH, index_col=0)
            self.userSimMatrix.index = self.userSimMatrix.index.map(int)
            self.userSimMatrix.columns = self.userSimMatrix.columns.map(int)
            self.movieSimMatrix = pd.read_csv(self.MOVIE_MATRIX_PATH, index_col=0)
            self.movieSimMatrix.index = self.movieSimMatrix.index.map(int)
            self.movieSimMatrix.columns = self.movieSimMatrix.columns.map(int)
            return

        # dimensions
        if (N != -1):
            self.ratingMatrix = self.ratingMatrix.loc[self.ratingMatrix['movieId'] <= N]
            self.movieMatrix = self.movieMatrix.loc[self.movieMatrix['id'] <= N]
        if (M != -1):
            self.ratingMatrix = self.ratingMatrix.loc[self.ratingMatrix['userId'] <= M]
        self.ratingMatrix = self.ratingMatrix.pivot_table(index='userId', columns='movieId', values='rating')
        self.ratingMatrix = self.ratingMatrix[self.ratingMatrix.columns.intersection(validMovies)]
        
        # similarity matrices from sparse table
        print('Creating user similarity matrix...', flush=True)
        start = time.time()
        self.userSimMatrix = self.makeSimMatrix(self.ratingMatrix)
        self.userSimMatrix.index = self.userSimMatrix.index.map(int)
        self.userSimMatrix.columns = self.userSimMatrix.columns.map(int)
        elapsed = time.time() - start
        print('User similarity matrix created in ' + self.makeTimeString(elapsed))

        print('Creating movie similarity matrix...', flush=True)
        start = time.time()
        self.movieSimMatrix = self.makeSimMatrix(self.ratingMatrix.T)
        self.movieSimMatrix.index = self.movieSimMatrix.index.map(int)
        self.movieSimMatrix.columns = self.movieSimMatrix.columns.map(int)
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
        return pd.DataFrame(matrix, index=df.index, columns=df.index)

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
        while (not id.isnumeric() or int(id) < 1 or not int(id) in self.userSimMatrix.index):
            if (not id.isnumeric()):
                id = input(input1)
            if (int(id) <= 0):
                id = input('ID must be greater than or equal to 1. ' + input1)
            else:
                id = input('Sorry, that ID is not in the similarity matrix. ' + input1)
        id = int(id)
            
        # find most similar users
        M = 30
        if (M >= self.userSimMatrix.shape[0]):
            M = self.userSimMatrix.shape[0] - 1
        topUsers = self.userSimMatrix.nlargest(M + 1, [id])
        topUsers = topUsers.drop([id])

        # average their movie ratings
        userIds = []
        for userId in topUsers.index:
            userIds.append(userId)
        averageRatings = self.ratingMatrix.iloc[userIds].mean(axis=0)

        # find best rated movies
        N = 5
        if (N >= averageRatings.shape[0]):
            N = averageRatings.shape[0] - 1
        topMovies = averageRatings.nlargest(N)

        # print data
        N = topMovies.shape[0]
        print('The top ' + str(N) + ' movie' + ('' if N == 1 else 's') + ' suggested for you are:')
        i = 0
        for movieId in topMovies.index:
            row = self.movieMatrix.loc[self.movieMatrix['id'] == movieId]
            i += 1
            print('\t' + str(i) + '. ' + row.iloc[0]['original_title'])
    
    def similarMovie(self):
        input1 = 'What is the name or ID of the movie you would like similar recommendations for? '
        id = input(input1)
        if (not id.isnumeric() and id in self.movieMatrix['original_title'].values):
            row = self.movieMatrix.loc[self.movieMatrix['original_title'] == id]
            id = str(row.iloc[0]['id'])
        while (not id.isnumeric() or int(id) < 1 or not int(id) in self.movieSimMatrix.index):
            if (not id.isnumeric()):
                id = input(input1)
            elif (int(id) <= 0):
                id = input('ID must be greater than or equal to 1. ' + input1)
            else:
                id = input('Sorry, that movie or ID is not in the similarity matrix. ' + input1)
            if (not id.isnumeric() and id in self.movieMatrix['original_title'].values):
                row = self.movieMatrix.loc[self.movieMatrix['original_title'] == id]
                id = str(row.iloc[0]['id'])
        id = int(id)
        
        # find movie title if exists
        titleRow = self.movieMatrix.loc[self.movieMatrix['id'] == id]
        if (titleRow.empty):
            print('Error. Movie ID not found in movie metadata file.')
            return
        title = titleRow.iloc[0]['original_title']
            
        # find most similar movies
        N = 5
        if (N >= self.movieSimMatrix.shape[0]):
            N = self.movieSimMatrix.shape[0] - 1
        topMovies = self.movieSimMatrix.nlargest(N + 1, [id])
        if (id in topMovies.index.values):
            topMovies = topMovies.drop([id])
        else:
            topMovies = topMovies.drop(topMovies.tail(1).index)

        # print data
        N = topMovies.shape[0]
        print('The top ' + str(N) + ' movie' + ('' if N == 1 else 's') + ' rated most similar to ' + title + ' are:')
        i = 0
        for movieId in topMovies.index:
            row = self.movieMatrix.loc[self.movieMatrix['id'] == int(movieId)]
            i += 1
            print('\t' + str(i) + '. ' + row.iloc[0]['original_title'])