import datetime
import json
import maplex
import random
import os

logger = maplex.Logger("randomizeHidamariWallpapers")

def randomize() -> None:

    try:

        # Load configurations

        logger.Info("Loading configurations...")
        conf = maplex.MapleTree("config.mpl")
        homePath = conf.readMapleTag("HOME", "PATH")
        configPath = os.path.join(
            homePath,
            ".var/app/io.github.jeffshee.Hidamari/config/hidamari/config.json"
            )
        
        with open(configPath, "r") as f:

            hidamariConf = json.load(f)

        currentVideoPath = hidamariConf.get("data_source", {}).get("Default", "")
        logger.Info(f"Current video path: [{currentVideoPath}]")

    except Exception as e:

        logger.ShowError(e, "Failed to load configurations.")
        return
    
    try:

        logger.Info("Getting video list...")

        # Get video list

        videoPath = os.path.join(
            homePath,
            "Videos/Hidamari"
            )

        videoList = [f for f in os.listdir(videoPath) if f.endswith(('.mp4', '.mkv', '.avi'))]
        randomSeed = int(f"{datetime.datetime.now():%f}")
        logger.Info(f"Found {len(videoList)} videos.")

        while True:

            random.seed(randomSeed)
            videoPath = os.path.join(videoPath, random.choice(videoList))

            if videoPath != currentVideoPath:

                break

            logger.Debug("Selected video is the same as current. Reselecting...")
        
    except Exception as e:

        logger.ShowError(e, "Failed to get video list.")
        return
        
    try:

        # Set video path in configuration

        dataSource = "data_source"

        for key in hidamariConf[dataSource].keys():

            hidamariConf[dataSource][key] = videoPath

        # Save updated configuration

        with open(configPath, "w") as f:

            json.dump(hidamariConf, f, indent=4)

        logger.Info(f"Wallpaper randomized to: [{videoPath}]")

    except Exception as e:

        logger.ShowError(e, "Failed to update configuration.")
        return

if __name__ == "__main__":

    logger.Info("Randomizing Hidamari wallpapers...")
    randomize()