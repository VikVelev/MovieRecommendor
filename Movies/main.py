import os
import pickle
import pandas as pd

from sklearn.preprocessing import MaxAbsScaler
from sklearn.neighbors import NearestNeighbors


def here(file):
    return os.path.dirname(os.path.realpath(__file__)) + file


if os.path.exists(here("/data.sav")) and os.path.exists(here("/distances.sav")) and os.path.exists(here("/indices.sav")):
    movieData = pickle.load(open(here('/data.sav'), 'rb'))
    distances = pickle.load(open(here('/distances.sav'), 'rb'))
    indices = pickle.load(open(here('/indices.sav'), 'rb'))

else:
    print("Loading data...")

    movieData = pd.read_table(here("/data/basics"), low_memory=False)
    movieData = movieData.dropna()
    movieData = movieData.drop(["endYear", "isAdult"], axis=1)

    # the parameters I consider the most important
    print("Converting to dummies.")
    f_Genre = movieData.genres.str.get_dummies(sep=",")
    movieData[movieData["startYear"] == "\\N"] = "0"
    f_StartYear = movieData.startYear
    f_Type = pd.get_dummies(movieData.titleType)

    # Assemble the training data
    movieFeatures = pd.concat([f_Genre, f_Type, f_StartYear], axis=1)
    print("Training...")
    print("Number of movies %s." % len(movieFeatures))
    movieFeatures = MaxAbsScaler().fit_transform(movieFeatures)

    # number of neighbors represents how many similar shows you will get
    nbrs = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(movieFeatures)
    distances, indices = nbrs.kneighbors(movieFeatures)

    with open(here('/data.sav'), 'wb') as file:
        pickle.dump(movieData, file, pickle.HIGHEST_PROTOCOL)

    with open(here('/distances.sav'), 'wb') as file:
        pickle.dump(distances, file, pickle.HIGHEST_PROTOCOL)

    with open(here('/indices.sav'), 'wb') as file:
        pickle.dump(indices, file, pickle.HIGHEST_PROTOCOL)

allMovies = list(movieData.originalTitle)
print("Loaded.")


def getIndex(name):
    if movieData[movieData["originalTitle"] == name].index.tolist() == []:
        if not getIdPartialName(name) == []:
            print("There are multiple choices")
            print("------------------------------")

            iterator = 1
            for label in getIdPartialName(name):
                print(("%s. %s") % (iterator, label))
                iterator += 1

            print("------------------------------")
            print("Which one should I search for? (number only)")
            choice = int(input()) - 1
            print("------------------------------")
            return getIndex(getIdPartialName(name)[choice])
        else:
            print("Nothing found.")
    else:
        return movieData[movieData["originalTitle"] == name].index.tolist()[0]


# basically autocomplete
def getIdPartialName(partial):
    movieArray = []
    for name in allMovies:
        if partial in name:
            movieArray.append(name)
    return movieArray


def printMovies(query=None, id=None):
    print("------------------------------")
    print("Here are some recommendations:")
    print("------------------------------")

    if id:
        for id in indices[id][1:]:
            print(movieData.iloc[id]["originalTitle"])
    if query:
        found_id = getIndex(query)
        for id in indices[found_id][1:]:
            print("______________________________")
            print(movieData.iloc[id]["originalTitle"])
            print(movieData.iloc[id]["genres"])


print("Tell me a movie/tv show:")
inputMovie = input()
print(len(indices))
print(len(allMovies))
printMovies(query=inputMovie)
