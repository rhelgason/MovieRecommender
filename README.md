# MovieRecommender
A movie recommender from scratch using csv files containing user reviews of movies. Provided in the top directory are two csv files, `ratings.csv` and `movies_metadata.csv`. The former contains a massive table of users and their ratings of various movies, and the latter simply gives information about every movie included in the dataset. Similarity matrices are computed to provide movie recommendations.

As the dataset is incredibly large, the program tends to run on a subset of movies and/or users. The first dimension, N, refers to the maximum movie ID that will be considered in the similarity matrices. The second dimension, M, refers to the maximum user ID that will be considered. Of course, higher values for these dimensions provide better recommendations, but the similarity matrices will also take longer to compute.

## Dataset
The dataset is borrowed from Rounak Banik on Kaggle [here](https://www.kaggle.com/rounakbanik/the-movies-dataset/version/7?select=movies_metadata.csv). It includes over 100,000 ratings from 700 users on 9,000 movies. Originally, a larger dataset was used, but the time complexity suggested that such a large dataset was unnecessary.

As the creation of the similarity matrices is the most time-consuming part of the program, sample similarity matrices have been included in the `/sample_similarity_matrices` directory. Each sample's name is formatted as follows: `<type>_similarity_matrix_<number of movies>_<number of users>.csv`. If either of the numbers are set to -1, this implies that no filtering was done on that dimension. To use any of these matrices, simply copy them to the top level directory, trim the file name to `<type>_similarity_matrix.csv`, and run the program without recreating the similarity matrices.

## Architecture
### Similarity Matrices
The data structures involved in this implementation are not too complicated. Upon initialization, the SimilarityMatrix class reads data from the provided datasets into pandas dataframes. The similarity matrices are both square dataframes that measure the cosine similarity between various users or movies. Calculating these matrices is an expensive process, but making predictions from them afterwards is very simple. The cosine similarity function operates as follows:

<p align="center">
  <img src="https://github.com/rhelgason/MovieRecommender/blob/master/img/cosine_similarity_function.PNG" alt="cosine similarity function"/>
</p>

In the (very common) scenario that two users have not rated any of the same movies or two movies have not been rated by any of the same users, the similarity matrix is simply given the "N/A" value. This implies that the users or movies have no discernable relation and should not be considered in recommendations. A similar edge case that I had to handle was the situation in which users or movies overlapped on only one value. Although Euclidean distance can handle situations like this, cosine similarity does not deal as well because the angle between these two vectors will always be zero, no matter how different the rating was. To overcome this, I defined a simple function that inspected the single rating as a normalized Euclidean distance.

The similarity matrices do not scale well with either time or space complexity. Assuming that calculating the cosine similarity between two vectors is done in linear time, the time and space complexity are both O(n<sup>2</sup> + m<sup>2</sup>). It's likely that both of these can be reduced from the current implementation, but this has not been fully explored yet. The following is an example of a similarity matrix between 10 users:

<p align="center">
  <img src="https://github.com/rhelgason/MovieRecommender/blob/master/img/user_similarity_matrix.PNG" alt="user similarity matrix"/>
</p>

Values on this table range from 0 to 1, with higher values indicating more similarity. Obviously, the center diagonal of the dataframe is always 1.0 because users are identical to themselves. These matrices allow for simple predictions as explained ahead.

### Prediction by Movie
The simpler of the two prediction methods, this one utilizes the movie similarity matrix. Two movies are mathematically similar when users tend to give them similar ratings. This method takes a specific movie as input and suggests a few other movies that are likely to appeal in the same way. The similarity values for the input movie's column are sorted in descending order and the most similar movies are suggested. An example input and output is shown below:

<p align="center">
  <img src="https://github.com/rhelgason/MovieRecommender/blob/master/img/prediction_by_movie.PNG" alt="prediction by movie"/>
</p>

### Prediction by User
This prediction method is slightly more complicated and utilizes the user similarity matrix. Two users are mathematically similar when they tend to give movies similar ratings. This method takes a specific user as input and suggest a few other movies that the user is likely to also enjoy. The similarity values for the input user's column are sorted in descending order to find the subset of users most similar to them. The movie ratings of these similar indivduals are averaged and ranked again to produce a sorted list of the movies that the user is most likely to rate similarly. An example input and output is shown below:

<p align="center">
  <img src="https://github.com/rhelgason/MovieRecommender/blob/master/img/prediction_by_user.PNG" alt="prediction by user"/>
</p>

## Runtime
As mentioned earlier, the time complexity of creating the similarity matrices O(n<sup>2</sup> + m<sup>2</sup>). I ran the datasets on various combinations of N and M to produce a data visualization of the runtime growth. The following is the time (in seconds) it took to produce the similarity matrices for specific N and M values:

### User Similarity Table
<p align="center">
  <img src="https://github.com/rhelgason/MovieRecommender/blob/master/img/user_table.PNG" alt="user table"/>
</p>

### Movie Similarity Table
<p align="center">
  <img src="https://github.com/rhelgason/MovieRecommender/blob/master/img/movie_table.PNG" alt="movie table"/>
</p>

N values grow along the X axis and M values grow along the Y axis. For both tables, the runtime clearly directly in correlation with the N and M values. However, the difference between the tables is stark. For the user table, runtimes increase much more directly as the M values grows, while the movie table runtimes increase with stronger correlation to the N values.

After the similarity matrices have been created, the recommendation process is much simpler. Matrix access is done in linear time, but single columns of the matrix must be sorted to find the most similar values. This operation is done in O(nlog(n)) or O(mlog(m)) time, depending on whether predicting by movie or by user.

## Findings
I have gained a lot from this project. Foremostly, I want to expand on the concept a little further to improve the data structures and algorithms included. I believe that the time and space complexities are not very impressive, and there must be ways to improve them. I input my own list of movie recommendations and learned that I should watch Interstellar. I'm not sure how I haven't seen that movie yet, but I expect that it will be something I enjoy.

Lastly, I'm interested in also exploring k-means with movie recommendations. Although the data structures involved will be different, I think the concepts could be related easily. I don't think the work will be overly difficult.

## Dependencies
The following Python libraries were used:
- pandas
- numpy
- time
- scipy
