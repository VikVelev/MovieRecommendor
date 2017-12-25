import os
import re
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import MaxAbsScaler
from sklearn.neighbors import NearestNeighbors

def here(file):
    return os.path.dirname(os.path.realpath(__file__)) + file

if os.path.exists(here("/data.sav")) and os.path.exists(here("/distances.sav")) and os.path.exists(here("/indices.sav")):
    movieData = pickle.load(open(here('/data.sav'),'rb'))
    distances = pickle.load(open(here('/distances.sav'),'rb'))
    indices = pickle.load(open(here('/indices.sav'),'rb'))

else:
    print("Loading data...")    

    movieData = pd.read_table(here("/data/basics"),low_memory=False)
    movieRatings = pd.read_table(here("/data/ratings"))
    movieData = np.array_split(movieData, 2)[0]
    movieData = movieData.drop(["endYear","isAdult","runtimeMinutes"],axis=1)

    #the parameters I consider the most important

    f_Genre = movieData.genres.str
    print("Converted to string.")
    print("Converting to dummies.")
    f_Genre = f_Genre.get_dummies(sep=",")
    f_Type = pd.get_dummies(movieData.titleType)
    f_Rating = movieRatings.averageRating
    print(f_Genre)
    print("=========================================")
    print(f_Type)
    print("=========================================")
    print(f_Rating)
    
    #Assemble the training data
    movieFeatures = pd.concat([f_Genre, f_Type, f_Rating],axis=1)
    movieFeatures = movieFeatures.dropna()
    print("Training...")
    #MaxAbsScaler is used with sparce matrices for capping their values between 1 and 0
    movieFeatures = MaxAbsScaler().fit_transform(movieFeatures)

    #using KNN to get similar anime.
    #number of neighbors represents how many similar animes you will get
    nbrs = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(movieFeatures)
    distances, indices = nbrs.kneighbors(movieFeatures)

    with open(here('/data.sav'), 'wb') as file:
        pickle.dump(movieData, file, pickle.HIGHEST_PROTOCOL)
    
    with open(here('/distances.sav'), 'wb') as file:
        pickle.dump(distances, file, pickle.HIGHEST_PROTOCOL)
    
    with open(here('/indices.sav'), 'wb') as file:
        pickle.dump(indices, file, pickle.HIGHEST_PROTOCOL)

print("Loaded.")

def getIndex(name):
    if movieData[movieData["originaname"]==name].index.tolist() == []:
        if not getIdPartialName(name) == []:

            print("There are multiple choices")
            print("------------------------------")
            
            iterator = 1
            for label in getIdPartialName(name):
                print(("%s. %s") % (iterator,label))
                iterator += 1

            print("------------------------------")            
            print("Which one should I search for? (number only)")
            choice = int(input()) - 1
            print("------------------------------")
            return getIndex(getIdPartialName(name)[choice])
        else:
            print("Nothing found.")
    else:
        return movieData[movieData["name"]==name].index.tolist()[0]

allMovies = list(movieData.originalTitle)

#because most names are 5+ words this makes it so it will be enough to type just one word.
def getIdPartialName(partial):
    movieArray = []
    for name in allMovies:
        if partial in name:
            movieArray.append(name)
    return movieArray

def printMovies(query=None,id=None):
    print("------------------------------")    
    print("Here are some recommendations:")
    print("------------------------------")
    
    if id:
        for id in indices[id][1:]:
            print(animeData.ix[id]["name"])
    if query:
        found_id = getIndex(query)
        for id in indices[found_id][1:]:
            print("______________________________")            
            print(movieData.ix[id]["name"])
            print(movieData.ix[id]["genre"])
            print(("Rating: %s") % movieData.ix[id]["rating"])
            print()


#[print("------------------------------")       
#print("Tell me a movie/tv show:")
print(movieData)
# inputMovie = input()
# printMovies(query=inputMovie)
