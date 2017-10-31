import os
import re
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import MaxAbsScaler
from sklearn.neighbors import NearestNeighbors

if os.path.exists("./data.sav") and os.path.exists("./distances.sav") and os.path.exists("./indices.sav"):  
    animeData = pickle.load(open('data.sav','rb'))
    distances = pickle.load(open('distances.sav','rb'))
    indices = pickle.load(open('indices.sav','rb'))
else:
    print("Loading data...")

    animeData = pd.read_csv(os.path.dirname(os.path.realpath(__file__)) + "/anime.csv")

    #Remove "Unkown" values and replace them with an estimate for less computer confusion
    animeData.loc[(animeData["genre"] == "Hentai") & (animeData["episodes"] == "Unknown"),"episodes"] = "1"
    animeData.loc[(animeData["type"] == "OVA") & (animeData["episodes"] == "Unknown"),"episodes"] = "2"
    animeData.loc[(animeData["type"] == "Movie") & (animeData["episodes"] == "Unknown")] = "1"
    animeData.loc[(animeData["episodes"] == "Unknown")] = "12"
    animeData["type"] = pd.get_dummies(animeData[["type"]])

    #a huge sparse matrix, with the parameters I consider the most important
    f_Genre = animeData["genre"].str.get_dummies(sep=",")
    f_Type = pd.get_dummies(animeData[["type"]])
    f_Rating = animeData[["rating"]]
    f_Episodes = animeData["episodes"]

    #Assemble the training data
    animeFeatures = pd.concat([f_Genre, f_Type, f_Rating, f_Episodes],axis=1)

    #Fills all NaN ratings with 0
    animeFeatures["rating"] = animeFeatures["rating"].fillna(0)

    #regex to sanitize name
    animeData["name"] = animeData["name"].map(lambda name:re.sub('[^A-Za-z0-9]+', " ", name))

    print("Training...")
    #MaxAbsScaler is used with sparce matrices for capping their values between 1 and 0
    animeFeatures = MaxAbsScaler().fit_transform(animeFeatures)

    #using KNN to get similar anime.
    #number of neighbors represents how many similar animes you will get
    nbrs = NearestNeighbors(n_neighbors=6, algorithm='ball_tree').fit(animeFeatures)
    distances, indices = nbrs.kneighbors(animeFeatures)

    pickle.dump(animeData,open('data.sav','wb'))
    pickle.dump(distances,open('distances.sav','wb'))
    pickle.dump(indices,open('indices.sav','wb'))

print("Loaded.")

def getIndex(name):
    if animeData[animeData["name"]==name].index.tolist() == []:
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
        return animeData[animeData["name"]==name].index.tolist()[0]

allAnime = list(animeData.name.values)

#because most names are 5+ words this makes it so it will be enough to type just one word.
def getIdPartialName(partial):
    animeArray = []
    for name in allAnime:
        if partial in name:
            animeArray.append(name)
    return animeArray

def printAnime(query=None,id=None):
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
            print(animeData.ix[id]["name"])
            print(animeData.ix[id]["genre"])
            print(("Rating: %s") % animeData.ix[id]["rating"])
            print()

while True:
    print("------------------------------")       
    print("Tell me an anime:")
    inputAnime = input()
    printAnime(query=inputAnime)
