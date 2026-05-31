from youtube_transcript_api import YouTubeTranscriptApi

# Quick test with a sample YouTube video
api = YouTubeTranscriptApi()

transcript = api.fetch("aircAruvnKk")

print(f"Type of transcript: {type(transcript)}")
print(f"Type of first item: {type(transcript[0])}")
print(f"First item: {transcript[0]}")
print("\n--- First 5 items ---")

for item in transcript[:5]:
    print(item.text)
