from googleapiclient.discovery import build

api_key = "AIzaSyAZ9hHZOdpvuvrM-GLhn5I6enzZ8h9Hpp8"


def search_videos_by_keyword(keyword):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.search().list(
        part="snippet",
        maxResults=10,
        q=keyword,
        type="video"
    )

    response = request.execute()
    url = f"https://www.youtube.com/watch?v={response['items'][0]['id']['videoId']}"
    return url
