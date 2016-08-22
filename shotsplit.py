#shotsplit detects cuts by comparing difference hashes of consecutive frames


import cv2
import argparse
import imagehash
import moviepy.editor as mpy

from tqdm import tqdm
from PIL import Image


#calculate the Hamming distance between hashed frames
def difference(f, hash_size=8, verbose=False, monitor=False,):
    distances = []
    frame_count = 0
    
    cap = cv2.VideoCapture(f)
    total_frames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
    progress_bar = tqdm(total=int(total_frames))

    while(cap.isOpened()):
        ret, frame = cap.read()
        frame_count += 1

        if (type(frame) == type(None)):
            break
      
        i = Image.fromarray(frame)
        this_hash = imagehash.dhash(i, hash_size=hash_size)
        
        try:
            distance = last_hash - this_hash
            distances.append( (frame_count, distance) )
            description = 'Hashing frames [%s]' % (frame_count)
            progress_bar.set_description(description)
            progress_bar.refresh()
        except:
            pass

        if monitor:
            cv2.imshow('current_frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
        last_hash = this_hash
        progress_bar.update(1)

    cap.release()
    return distances, fps


#calculate the position of cuts by thresholding variations in Hamming distance
def cuts(distances, threshold=10):
    cuts_list = []
    
    for f, di in distances:
        if di > threshold:
            cuts_list.append(f-1)

    cuts_list.append(distances[-1][0])

    return cuts_list


#calculate shot tcin/tcout in (s)
def shots(cuts, minimum_shot_length=6):
    shots_list = []
    
    for cut in cuts:
        try: 
            last_cut = shots_list[-1][1]
        except:
            last_cut = -1

        shot_length = (cut - last_cut)
        if shot_length > minimum_shot_length:
            shot = (last_cut+1, cut-1)
            if shot[1] > shot[0]:
                shots_list.append(shot)

    return shots_list


#cut video into clips using tcin/tcout
def clips(video_filename, shots, fps=25, output=False):
    clips_list = []

    video = mpy.VideoFileClip(video_filename)
    name, extn = video_filename.split('.')

    progress_bar = tqdm(total=len(shots))
    progress_bar.set_description('Clipping shots')
    progress_bar.refresh()
    for i, shot in enumerate(shots):
        if shot[0] == 1:
            tcin = 0
        else:
            tcin = shot[0] / float(fps)
        
        tcout = shot[1] / float(fps)

        clip = video.subclip(tcin, tcout)
        clips_list.append(clip)
        
        if output:
            filename = '%s%s-clip-%s.%s' % (output, name, i, extn)
            clip.write_videofile(filename, fps=fps)

        progress_bar.update(1)

    return clips_list


def shotsplit(input_file, minimum_shot_length=6, threshold=10, fps=False, output=False, verbose=False, monitor=False):
    hamming_distances, fps = difference(input_file, verbose=verbose, monitor=monitor)
    cut_points = cuts(hamming_distances, threshold=threshold)
    shots_list = shots(cut_points, minimum_shot_length=minimum_shot_length)
    clips_list = clips(input_file, shots_list, fps=fps, output=output)
    
    return shots_list, clips_list


parser = argparse.ArgumentParser(description='''
    Shotsplit detects cuts in video by comparing
    difference hashes of consecutive frames and
    thresholding variations in Hamming distance.
    ============================================
    Edward Anderson
    -----------------------------------------
    v0.1 | 2016
''', formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-v',
                    '--video',
                    help='path to input video')

parser.add_argument('-o',
                    '--output',
                    help='path for saving cut clips',
                    default=False)

parser.add_argument('-m',
                    '--monitor',
                    help='show video monitor while parsing',
                    action='store_true',
                    default=False)

parser.add_argument('-s',
                    '--shot_length',
                    help='set minimum shot length in frames',
                    default=6,
                    type=int)

parser.add_argument('-t',
                    '--threshold',
                    help='set Hamming distance threshold',
                    default=10,
                    type=int)

parser.add_argument('-f',
                    '--fps',
                    help='specify fps',
                    type=float)

args = parser.parse_args()
if not args.video:
    parser.error('argument -v / --video is required')


shots_list, clips_list = shotsplit(args.video,
                                   output=args.output,
                                   minimum_shot_length=args.shot_length,
                                   fps=args.fps,
                                   threshold=args.threshold,
                                   verbose=True,
                                   monitor=args.monitor)

print '\nDetected %s shots:' % len(shots_list)
for s in shots_list:
    print '%s:%s' % (s[0], s[1])