import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

FRIENDNAME = "Toby Johnson"
PATH = Path("C:\\Users\\GSMRoss\\Documents\\Python Scripts\\FB Messanger Reply Time\\messages")
FB_FULLNAME = "Clair Ross"



def ParseData():
    files = list(Path(PATH).rglob("*.json"))
    data = np.array([])
    for file in files:
        with open(file) as f:
            conversationData = StripJSONData(json.load(f))
            if conversationData:
                data = np.append(data,conversationData)
    return data

def StripJSONData(jsonData):
    # TODO: Add ability for more than two speakers
    if len(jsonData['participants']) > 2:
        return None
    for participants in jsonData['participants']:
        name = participants['name']
        if participants['name'] != FB_FULLNAME:
            break
    if name == FB_FULLNAME:
        return None
    msgs = jsonData['messages']

    try:
        lastSpeakerWasMe = 0 if msgs[0]['sender_name'] != FB_FULLNAME else 1
    except KeyError:
        return None #TODO: Fix this so try isn't needed
    # Set first speaker arbitrarily
    lastSpeaker = FB_FULLNAME
    currentMsgTimeArray = []
    msgsTimeArray = []
    for msg in msgs:
        try:
            if lastSpeaker != msg['sender_name']:
                lastSpeaker = msg['sender_name']
                if len(currentMsgTimeArray) > 0:
                    msgsTimeArray.append(currentMsgTimeArray)
                currentMsgTimeArray = []
            time = msg['timestamp_ms']
            currentMsgTimeArray.append(time)
        except KeyError:
            continue
    return {'name': name, 'lastSpeakerWasMe': lastSpeakerWasMe, 'msgTimes': msgsTimeArray}
    

def replyTimesFromMsgTimes(msgTimes, lastSpeakerWasMe):
    # assume it's in unix time 
    mTimes = msgTimes.copy()
    meHistogramCountsArray = []
    friendHistogramCountsArray = []
    friendWasSpeaking = not lastSpeakerWasMe
    while len(mTimes) > 1:
        msgTime = mTimes.pop(0)
        replyTime = (msgTime[-1] - mTimes[0][0])/1000 # Difference in seconds
        if friendWasSpeaking:
            friendHistogramCountsArray.append(replyTime)
        else:
            meHistogramCountsArray.append(replyTime)
        friendWasSpeaking = not friendWasSpeaking
    return meHistogramCountsArray, friendHistogramCountsArray

try:
    data
except NameError:
    data = ParseData()

friendConversation = [item for item in data if item['name'] == FRIENDNAME ][0]

replyArray = replyTimesFromMsgTimes(friendConversation['msgTimes'], friendConversation['lastSpeakerWasMe'])

fig, ax = plt.subplots(1,2)
ax[0].hist([i for i in replyArray[0] if i < 100], bins=10, color = 'b', histtype='step')
ax[1].hist([i for i in replyArray[1] if i < 100], bins=10, color = 'r', histtype='step')
ax[0].set_title(FB_FULLNAME + " Reply Times")
ax[1].set_title(FRIENDNAME + " Reply Times")
fig.text(0.5, 0, "Time (seconds)", ha='center')
fig.text(0, 0.5, "Count", ha='center', rotation="vertical")
plt.show()