import base64
import os
import json
import urllib.parse

from .listfilestrategy import File

def to_seconds(time_mark: str) -> float:
    parts = time_mark.split(":")
    if len(parts) == 2:
        # mm:ss.000
        mm = int(parts[0])
        secs = float(parts[1])
        return mm * 60 + secs
    elif len(parts) == 3:
        # hh:mm:ss.000
        hh = int(parts[0])
        mm = int(parts[1])
        secs = float(parts[2])
        return hh * 3600 + mm * 60 + secs
    raise ValueError("Invalid format")

class VideoMapper:
    def __init__(self, file: File):
        self.file = file
        self.videoName = None
        self.videoKind = None
        self.videoUrl = None
        self.get_video_properties()

    def get_video_ts(self) -> str:
        #load file into json
        with open(self.file.content.name, 'r') as f:
            data = json.load(f)
        
        videomd = data.get("markdown")
        videoStartTime = to_seconds(videomd.split("# Shot ")[1].split(" =>")[0])

        referralInfo = {
            "referralInfo": {
                "referralApp": "StreamWebApp",
                "referralView": "ShareDialog-Link",
                "referralAppPlatform": "Web",
                "referralMode": "view"
            },
            "playbackOptions": {
                "startTimeInSeconds": videoStartTime
            }
        } 

        playbackOptions = {
            "playbackOptions": {
                "startTimeInSeconds": videoStartTime
            }
        }
        referralInfoStr = json.dumps(referralInfo)
        playbackOptionsStr = json.dumps(playbackOptions)
        # encodedInfo = urllib.parse.quote(base64.b64encode(referralInfoStr.encode('utf-8')).decode('utf-8'))
        encodedInfo = urllib.parse.quote(playbackOptionsStr)

        return encodedInfo

    def get_video_properties(self):
        #if current file is xml ignore
        if self.file.file_extension() == ".xml":
            return
        file_path = self.file.file_path()
        video_xml = os.path.join(file_path, f"{os.path.basename(file_path)}.xml")

        #try to open the xml file
        try:
            with open(video_xml, 'r') as f:
                xml_content = f.read()
        except FileNotFoundError:
            return "The medatata for the video was not found. Please make sure that the directy includes the xml file."
        
        self.videoName = xml_content.split("<videoName>")[1].split("</videoName>")[0]
        self.videoKind = xml_content.split("<videoKind>")[1].split("</videoKind>")[0]
        self.videoUrl = xml_content.split("<videoUrl>")[1].split("</videoUrl>")[0]

        if self.videoKind == "msStream":
            videoTs = self.get_video_ts()
            #if needs full encoding (not embedding)
            # self.videoUrl = f"{self.videoUrl}?csf=1&web=1&nav={videoTs}"
            #if iframe embedding
            self.videoUrl = f"{self.videoUrl}&nav={videoTs}"


        
    