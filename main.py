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
    # Averages, medians, modes
    mean = pd.DataFrame(dataframe.groupby('Key').mean())
    median = pd.DataFrame(dataframe.groupby('Key').median())
    # mode = pd.DataFrame(dataframe.groupby('Key').mode())
    count = pd.DataFrame(dataframe.groupby('Key').size())
    
    stats = mean.merge(median, how='inner', on='Key')
    stats = stats.merge(count, how='inner', on='Key')
    stats.rename(
            {'holdTime_x' : 'meanHoldTime', 
             'floatTime_x' : 'meanFloatTime', 
             'holdTime_y' : 'medianHoldTime', 
             'floatTime_y' : 'medianFloatTime',
             0 : 'Count'}, axis='columns', inplace=True, errors='raise')
    stats.drop(labels=['down_x', 'up_x', 'down_y', 'up_y'], inplace=True, axis='columns')

    print(stats.head())
    return stats

data, start = record(10)
finalData = rawPairs(process(data, start))

pairsDataFrame = pd.DataFrame(finalData, columns=['Key', 'down', 'up'])
pairsDataFrame.to_json('keyData.json')
# print(pairsDataFrame.head())
# pairsDataFrame = pd.read_json('keyData.json')

# Prelim
pairsDataFrame['holdTime'] = pairsDataFrame['up']-pairsDataFrame['down']
# A negative value indicates key which were pressed at the same time
pairsDataFrame['floatTime'] = pairsDataFrame['down'].shift(-1)-pairsDataFrame['up']

stats = genStatsPairs(pairsDataFrame)
# print(pairsDataFrame.head())



