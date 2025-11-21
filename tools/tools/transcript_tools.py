import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from youtube_transcript_api import YouTubeTranscriptApi
from textwrap import dedent
from langchain.tools import tool


@tool("Fetch Youtube Transcript")
def youtube_transcript_retriever(video_url: str) -> str:
    """
    Retrieve the transcript of a YouTube video.

    Parameters:
        - video_url: The URL of the YouTube video.

    Returns:
        - str, The transcript of the video.
    """

    # Extract video id from URL
    video_id = video_url.split("watch?v=")[1]

    if "&" in video_id:
        video_id = video_id.split("&")[0]

    # Get the transcript of the video
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

    # Convert the transcript into a single string
    transcript = " ".join([i["text"] for i in transcript_list])

    return dedent(transcript)
