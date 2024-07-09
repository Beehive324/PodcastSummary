import streamlit as st
import glob
import json
from main import pipeline
from threading import Thread

st.title("Podcast Summaries")

json_files = glob.glob('*.json')


episode_id = st.sidebar.text_input("Enter Episode ID")
button = st.sidebar.button("Download Episode summary")

if button and episode_id:
    st.sidebar.write("Get auto chapter...")
    t = Thread(target=pipeline, args=(episode_id,))
    t.start()


def get_clean_title(title):
    txt = ''
    for char in title:
        if char == '(':
            continue
        elif char == ')':
            continue
        else:
            txt += char
    return txt


def get_clean_summary(chapters):
    txt = ''
    for chapter in chapters:
        start_ms = chapter['start']
        headline = chapter['headline']
        seconds = int((start_ms / 1000) % 60)
        minutes = int((start_ms / (1000 * 60)) % 60)
        hours = int((start_ms / (1000 * 60 * 60)) % 24)
        if hours > 0:
            txt += f'start: {hours:02d}:{minutes:02d}:{seconds:02d}'
        else:
            txt += f'start: {minutes:02d}:{seconds:02d}'
        txt += '\n\n'
        txt += chapter['summary']
        txt += '\n\n'
        txt += '\n\n'
        txt += headline.upper()
        txt += '\n\n'
    return txt


for file in json_files:
    with open(file, 'r') as f:
        data = json.load(f)

    chapters = data['chapters']

    #ep_image = data['ep_image'],
    #ep_podcast_title = data['ep_podcast_title'],
    ep_podcast_title = data['ep_title'],
    ep_audio = data['ep_audio'],
    ep_thumbnail = data['ep_thumbnail']

    with st.expander(f"{get_clean_title(ep_podcast_title)}"):
        st.image(ep_thumbnail, width=200)
        st.markdown(f'### {get_clean_title(ep_podcast_title)}')
        st.write(get_clean_summary(chapters))
