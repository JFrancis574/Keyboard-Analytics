import time
import keyboard as kb
import numpy as np
import pandas as pd

def record(interval):
    recorded = []
    startTime = time.time()
    
    keyboardHook = kb.hook(recorded.append)
    time.sleep(interval)
    
    kb.unhook(keyboardHook)
    return recorded, startTime

def process(data, startTime):
    if len(data) == 0:
        return None
    
    rawKeys = []
    for x in data:
        rawKeys.append([x.name, (x.time - startTime), x.event_type])
        
    return rawKeys
       
def rawPairs(rawKeyData):
        pairsArray = []
        for i in range(len(rawKeyData)):
            try:
                if (rawKeyData[i][2] == 'down' and rawKeyData[i+1][2] == 'up' and rawKeyData[i][0].lower() == rawKeyData[i+1][0].lower()):
                    # If the next value in the array is the up action
                    pairsArray.append([rawKeyData[i][0], rawKeyData[i][1], rawKeyData[i+1][1]])
                else:
                    # Otherwise, search for the next opposing action and pair them up
                    for x in range(i, len(rawKeyData)):
                        if (rawKeyData[x][0].lower() == rawKeyData[i][0].lower() and rawKeyData[x][2] == 'up' and rawKeyData[i][2] == 'down'):
                            pairsArray.append([rawKeyData[i][0], rawKeyData[i][1], rawKeyData[x][1]])
                            break        
            except IndexError:
                pass
        return pairsArray
    
def genStatsPairs(dataframe):
    # Prelim
    dataframe['holdTime'] = dataframe['up']-dataframe['down']
    # A negative value indicates key which were pressed at the same time
    dataframe['floatTime'] = dataframe['down'].shift(-1)-dataframe['up']
    
    # Averages, medians, modes
    mean = pd.DataFrame(dataframe.groupby('Key').mean())
    median = pd.DataFrame(dataframe.groupby('Key').median())
    # mode = pd.DataFrame(dataframe.groupby('Key').mode())
    count = pd.DataFrame(dataframe.groupby('Key').count())
    
    print(count.head())
    print(mean.head())
    return dataframe


data, start = record(10)
rawKeys = process(data, start)
finalData = rawPairs(rawKeys)

pairsDataFrame = pd.DataFrame(finalData, columns=['Key', 'down', 'up'])
# print(pairsDataFrame.head())
pairsDataFrame = genStatsPairs(pairsDataFrame)
# print(pairsDataFrame.head())
pairsDataFrame.to_json('keyData.json')


