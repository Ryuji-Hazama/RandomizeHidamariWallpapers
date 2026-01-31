import datetime
import maplex
import random
import subprocess
import time
import os

class randomizeHidamariWallpapers:

    def __init__(self) -> None:

        self.logger = maplex.getLogger(__name__)

        try:

            # Load configurations

            self.logger.info("Loading configurations...")

            configPath = os.path.expanduser("~/.var/app/io.github.jeffshee.Hidamari/config/hidamari/config.json")
            self.hidamariConfInstance = maplex.MapleJson(configPath)
            self.confInstance = maplex.MapleJson("config.json")

        except Exception as e:

            self.logger.ShowError(e, "Failed to load configurations.", True)
            return
        
    def randomAndRun(self) -> None:

        self.logger.info("Randomizing Hidamari wallpapers...")
        self.randomize()
        self.runHidamari()
        self.logger.info("Hidamari wallpaper randomization and execution completed.")

    def randomize(self) -> None:

        try:

            # Load configurations

            conf = self.confInstance.read()
            randomizeHidamariConf = conf.get("HidamariWallpapers", {})
            videoPath = randomizeHidamariConf.get("wallpaperDirectory", None)
            self.logger.info(f"Wallpaper directory: [{videoPath}]")

            if videoPath is None:

                # Set to default directory if not present

                videoPath = os.path.expanduser("~/Videos/Hidamari")
                randomizeHidamariConf["wallpaperDirectory"] = videoPath
                self.logger.info(f"Set wallpaper directory to default: [{videoPath}]")

            # Check if directory exists

            if not os.path.exists(videoPath):

                self.logger.error(f"Wallpaper directory does not exist: [{videoPath}]")

                # Set to default directory

                videoPath = os.path.expanduser("~/Videos/Hidamari")
                randomizeHidamariConf["wallpaperDirectory"] = videoPath
                self.logger.info(f"Set wallpaper directory to default: [{videoPath}]")

            # Read Hidamari configuration

            hidamariConf = self.hidamariConfInstance.read()
            currentVideoPath = hidamariConf.get("data_source", {}).get("Default", "")
            self.logger.info(f"Current video path: [{currentVideoPath}]")

            # Get video list

            self.logger.info("Getting video list...")

            videoList = [f for f in os.listdir(videoPath) if f.endswith(('.mp4', '.mkv', '.avi'))]
            self.logger.info(f"Found {len(videoList)} videos.")

            # Exclude used videos if applicable

            usedWallpapersList = randomizeHidamariConf.get("usedWallpapersList", [])
            
            if len(usedWallpapersList) < len(videoList):

                newVideoList = [video for video in videoList if video not in usedWallpapersList]
                self.logger.info(f"Excluding {len(usedWallpapersList)} used videos. {len(newVideoList)} videos left to choose from.")

            else:

                newVideoList = videoList
                self.logger.info("All videos have been used. Resetting used videos list.")
                usedWallpapersList = []

            # Select random video

            randomSeed = int(f"{datetime.datetime.now():%f}")
            random.seed(randomSeed)
            selectedVideo = random.choice(newVideoList)
            videoPath = os.path.join(videoPath, selectedVideo)
            self.logger.info(f"Selected video: [{selectedVideo}]")

            # Update configuration with new used video list

            usedWallpapersList.append(selectedVideo)
            randomizeHidamariConf["usedWallpapersList"] = usedWallpapersList
            conf["HidamariWallpapers"] = randomizeHidamariConf
            self.confInstance.write(conf)

        except Exception as e:

            self.logger.ShowError(e, "Failed to get video list.", True)
            return
            
        try:

            # Set video path in configuration

            dataSource = "data_source"

            for key in hidamariConf[dataSource].keys():

                hidamariConf[dataSource][key] = videoPath

            # Save updated configuration

            self.hidamariConfInstance.write(hidamariConf)
            self.logger.info(f"Wallpaper randomized to: [{videoPath}]")

        except Exception as e:

            self.logger.ShowError(e, "Failed to update configuration.")

    def runHidamari(self) -> None:

        try:

            # Load change interval from configuration

            conf = self.confInstance.read().get("HidamariWallpapers", {})
            self.changeInterval = conf.get("changeIntervalMinutes", None)
            
            if self.changeInterval is None:

                # Set default value if not present

                self.logger.info("Change interval not found in configuration. Setting to default (0 minutes).")
                self.changeInterval = 0
                conf["HidamariWallpapers"]["changeIntervalMinutes"] = 0
                self.confInstance.write(conf)

            self.logger.info(f"Change interval: {self.changeInterval} minutes.")

            # Run Hidamari

            self.logger.info("Running Hidamari...")
            subprocess.Popen(["flatpak", "run", "--command=hidamari", "io.github.jeffshee.Hidamari", "-b"])

            if self.changeInterval > 0:

                self.logger.info("Entering wallpaper change loop...")

                while True:

                    # Re-read configuration to get updated change interval

                    conf = self.confInstance.read().get("HidamariWallpapers", {})
                    changeInterval = conf.get("changeIntervalMinutes", self.changeInterval)

                    if changeInterval != self.changeInterval:

                        if changeInterval in [0, None]:

                            self.logger.info("Change interval set to 0 or None. Exiting wallpaper change loop.")
                            break

                        self.changeInterval = changeInterval
                        self.logger.info(f"Change interval updated to: {self.changeInterval} minutes.")

                    # Wait for the specified change interval

                    self.logger.info(f"Waiting for {self.changeInterval} minutes before reloading...")
                    changeIntervalDatetime = datetime.datetime.now() + datetime.timedelta(minutes=self.changeInterval)
                    self.logger.info(f"Next wallpaper change at: {changeIntervalDatetime:%Y-%m-%d %H:%M:%S}")
                    time.sleep(self.changeInterval * 60)

                    # Randomize and reload Hidamari

                    self.randomize()
                    self.logger.info("Reloading Hidamari...")
                    subprocess.Popen(["dbus-send", "--session", "--print-reply",
                                    "--dest=io.github.jeffshee.Hidamari.server",
                                    "/io/github/jeffshee/Hidamari/server",
                                    "io.github.jeffshee.hidamari.server.reload"])

            else:

                self.logger.info("Change interval is set to 0. Not reloading Hidamari.")

        except Exception as e:

            self.logger.ShowError(e, "Failed to run Hidamari.", True)
            return

if __name__ == "__main__":

    randomizeHidamariWallpapers().randomAndRun()