#!/usr/bin/env python3
# Video/Audio processing library
from pytube import YouTube
import ffmpeg

# Pretty Print libraries
import typer
from rich.progress import SpinnerColumn, Progress, TextColumn
from rich.pretty import pprint

# Concurrency + Management
import os
import sys
import subprocess as sp
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import tempfile

# My own files
import prompts
import task_manager as tsm

def process_ytdl_input(input, delim):
    try: 
        link, fname = input.split(delim);
        link = link.strip()
        fname = fname.strip()
    except: 
        link = input.strip()
        fname = None
    return (link, fname)

app = typer.Typer(help="Youtube Downloader CLI")

@app.command()
def download(
    file: typer.FileText = typer.Argument(None, help = "File to read, stdin otherwise"),
    workers: int = typer.Option(1, "-w", "--workers", help = "Number of parallel tasks"),
    output_path: str = typer.Option(os.getcwd(), "-p", help="Output path to write downloaded Youtube videos to"),
    silent: bool = typer.Option(False, "-q", "--quiet", help="Do not prompt for audio/video quality choices"),
    delim: str = typer.Option(";", "-d", "--delim", help="Delimiter separating Youtube link and desired file name to rename to"),
    ):
    # Prompt here
    if file:
        min_res, max_res = prompts.select_bounds("resolution", prompts.RESOLUTIONS)
        min_abr, max_abr = prompts.select_bounds("audio bit rate", prompts.AUDIO_BITRATES)
    else:
        resolutions = [prompts.remove_units(val) for val in prompts.RESOLUTIONS]
        min_res = min(resolutions)
        max_res = max(resolutions)
        audio_br = [prompts.remove_units(val) for val in prompts.AUDIO_BITRATES]
        min_abr = min(audio_br)
        max_abr = max(audio_br)

    input_ = file if file else sys.stdin

    video_dwnlds = []
    for line in input_:
        video_dwnlds.append(process_ytdl_input(line.strip(), delim))


    for link, fname in video_dwnlds:
        # executor.submit(Download, min_abr, max_abr, min_res, max_res)
        print(link, fname)
        tempdname, title = Download(link, min_abr, max_abr, min_res, max_res)
        if fname != None:
            pprint(f"Renamed '{title}' to '{fname}'")
            new_fname = fname + ".mp4"
        else:
            new_fname = title + ".mp4"

        os.rename(tempdname + "/output.mp4", output_path + "/" + new_fname)
        os.rmdir(os.path.join(tempdname))
    
#    futures = []
#    with ThreadPoolExecutor(max_workers = workers) as executor:
#        # Add some code to ensure we continue if download is not successful

#
#            success = Download(link, tmpdirname, min_abr, max_abr, min_res, max_res)

#    title = YouTube(link).title

#    os.rename(tempdname + "/output.mp4", output_path + "/" + new_fname)

def select_abr(s, min_abr, max_abr):
    streams = s.filter(type="audio").order_by("abr")
    for stream in s.filter(type="audio").order_by("abr"):
        abr = int(stream.abr.rstrip("kbps"))
        if (abr >= min_abr and abr <= max_abr): 
            pprint(f"Audio Bit Rate: {stream.abr}")
            return stream
    return None

def select_res(s, min_res, max_res):
    streams = s.filter(type="video").order_by("resolution")
    for stream in streams:
        res = int(stream.resolution.rstrip("p"))
        if (res >= min_res and res <= max_res): 
            pprint(f"Resolution: {stream.resolution}")
            return stream
    return None

def mp4_to_wav(inputf, path):
    outf = re.sub(r"\.mp4$", ".wav", inputf)
    ffmpeg.input(path + '/' + inputf).output(path + '/' + outf).run(quiet = True)
    return outf

import re
# Return temporary path
def Download(link, min_abr, max_abr, min_res, max_res):
    temp_path = tempfile.mkdtemp()

    try: 
        youtubeObject = YouTube(link)
        print("Retrieved Video:", youtubeObject.title)
    except:
        print("link", repr(link), "does not exist")
        return -1
        
    ys = youtubeObject.streams

    audio = select_abr(ys, min_abr, max_abr) 
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(
            description="Downloading " + youtubeObject.title + " audio...", 
            total = None
        )
        audio.download(temp_path)
        mp4_fname= os.listdir(temp_path)[0]
        wav_fname = mp4_to_wav(mp4_fname, temp_path)
    print("Done downloading audio!")

    video= select_res(ys, min_res, max_res)
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(
            description="Downloading " + youtubeObject.title + " video...", 
            total = None
        )
        video.download(temp_path)

    print("Done downloading video!")

    #with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
    #    progress.add_task(
    #        description="Combining audio and video...", 
    #        total = None
    #    )
    input_video = ffmpeg.input(temp_path + '/' + mp4_fname)
    input_audio = ffmpeg.input(temp_path + '/' + wav_fname)
    process = ffmpeg.concat(input_audio, input_video, a=1, v=1).output(temp_path + '/output.mp4').run()
    return temp_path, "output.mp4"


if __name__ == "__main__":
    app() 

