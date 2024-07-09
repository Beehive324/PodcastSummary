import json
import pprint
import time
import requests
from keys import API_KEY_LISTENNOTES, API_KEY_ASSEMBLYAI

listen_notes_api_key = API_KEY_LISTENNOTES
assemblyai_api_key = API_KEY_ASSEMBLYAI

url_1 = 'https://listen-api.listennotes.com/api/v2/episodes'

headers_1 = {
    'X-ListenAPI-Key': listen_notes_api_key,
}

transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_assemblyai = {
    'authorization': assemblyai_api_key,
    'content-type': "application/json"
}


def make_request(episode_id):
    url = f"{url_1}/{episode_id}"
    response = requests.get(url, headers=headers_1)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()

    ep_title = data['title']
    ep_image = data['image']
    ep_podcast_title = data['podcast']['title']
    ep_audio = data['audio']
    ep_thumbnail = data['thumbnail']

    return ep_title, ep_image, ep_podcast_title, ep_audio, ep_thumbnail


def transcribe(audio_url, auto_chapters=True):
    transcript_request = {
        'audio_url': audio_url,
        'auto_chapters': auto_chapters
    }

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers_assemblyai)
    transcript_response.raise_for_status()  # Raise an exception for HTTP errors

    pprint.pprint(transcript_response.json())
    return transcript_response.json()['id']


def poll(transcript_id, **kwargs):
    polling_endpoint = f"{transcript_endpoint}/{transcript_id}"
    polling_response = requests.get(polling_endpoint, headers=headers_assemblyai)
    polling_response.raise_for_status()  # Raise an exception for HTTP errors

    if polling_response.json()['status'] == 'completed':
        filename = f"{transcript_id}.txt"
        with open(filename, 'w') as f:
            f.write(polling_response.json()['text'])

        filename = f"{transcript_id}_chapters.json"
        with open(filename, 'w') as f:
            chapters = polling_response.json().get('chapters', [])

            data = {'chapters': chapters}
            for key, value in kwargs.items():
                data[key] = value

            json.dump(data, f, indent=4)

        print('Transcript saved')
        return True
    return False


def pipeline(episode_id):
    ep_title, ep_image, ep_podcast_title, ep_audio, ep_thumbnail = make_request(episode_id)
    transcribe_id = transcribe(ep_audio, auto_chapters=True)
    while True:
        result = poll(transcribe_id, ep_audio=ep_audio, ep_thumbnail=ep_thumbnail, ep_title=ep_title)
        if result:
            break
        print("Waiting for transcript")
        time.sleep(60)


if __name__ == "__main__":
    pipeline("559a2fe7a6d74c43809ebcfa5da38a5b")
