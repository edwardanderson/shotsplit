shotsplit
=========

**shotsplit** automatically detects and extracts shots from video files.


## Requirements
* python
* opencv
* PIL


## How to use it

Specify the paths to a video file and a save directory:

~~~text
$ python shotsplit.py --video path/to/video.mp4 --output path/to/shots/directory/
~~~


### Options

#### `-s` / `--shot_length`
Set minimum shot length in frames

#### `-t` / `--threshold`
Set Hamming distance threshold

#### `-m` / `--monitor`
Show video frames during parsing


## How it works

**shotsplit** detects cuts in video files with [`imagehash`](https://github.com/JohannesBuchner/imagehash) by comparing difference hashes of consecutive frames and then thresholding the variations in Hamming distance between them. It uses [`MoviePy`](http://zulko.github.io/moviepy/) for clip extraction.


## To do

* [measure for quality](https://en.wikipedia.org/wiki/Shot_transition_detection)
* timecodes
* metrics: average shot duration, number of shots, etc.
* `xml` output
* **Kdenlive**, **OpenShot** project compatibility

