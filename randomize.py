import datetime
import json
import maplex
import random
import os

def randomize():

    # Load configurations

    conf = maplex.MapleTree("config.mpl")
    homePath = conf.readMapleTag("HOME", "PATH")
    configPath = os.path.join(
        homePath,
        ".var/app/io.github.jeffshee.Hidamari/config/hidamari/config.json"
        )
    
    with open(configPath, "r") as f:

        hidamariConf = json.load(f)

    # Get video list

    videoPath = os.path.join(
        homePath,
        "Videos/Hidamari"
        )
    
    videoList = [f for f in os.listdir(videoPath) if f.endswith(('.mp4', '.mkv', '.avi'))]
    randomSeed = int(f"{datetime.datetime.now():%f}")
    random.seed(randomSeed)
    videoPath = os.path.join(videoPath, random.choice(videoList))

    # Set video path in configuration

    dataSource = "data_source"

    for key in hidamariConf[dataSource].keys():

        hidamariConf[dataSource][key] = videoPath

    # Save updated configuration

    with open(configPath, "w") as f:

        json.dump(hidamariConf, f, indent=4)

if __name__ == "__main__":
    randomize()