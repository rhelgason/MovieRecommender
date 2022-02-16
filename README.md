# MovieRecommender
A movie recommender from scratch using csv files containing user reviews of movies. Provided in the top directory are two csv files, `ratings.csv` and `movies_metadata.csv`. The former contains a massive table of users and their ratings of various movies, and the latter simply gives information about every movie included in the dataset. Similarity matrices are computed to provide movie recommendations.

As the dataset is incredibly large, the program tends to run on a subset of movies and/or users. The first dimension, N, refers to the maximum movie ID that will be considered in the similarity matrices. The second dimension, M, refers to the maximum user ID that will be considered. Of course, higher values for these dimensions provide better recommendations, but the similarity matrices will also take longer to compute.

## Dataset
The dataset is borrowed from Rounak Banik on Kaggle [here](https://www.kaggle.com/rounakbanik/the-movies-dataset/version/7?select=movies_metadata.csv). It includes over 100,000 ratings from 700 users on 9,000 movies. Originally, a larger dataset was used, but the time complexity suggested that such a large dataset was unnecessary.

As the creation of the similarity matrices is the most time-consuming part of the program, sample similarity matrices have been included in the `/sample_similarity_matrices` directory. Each sample's name is formatted as follows: `<type>_similarity_matrix_<number of movies>_<number of users>.csv`. If either of the numbers are set to -1, this implies that no filtering was done on that dimension. To use any of these matrices, simply copy them to the top level directory, trim the file name to `<type>_similarity_matrix.csv`, and run the program without recreating the similarity matrices.

## Architecture

## Runtime

## Findings

## Gained Knowledge and Predictions

## Dependencies
The following Python libraries were used:
- pandas
- numpy
- time
- scipy
