# littleaudiovisualizer

i made a little audio visualizer for my youtube videos (my remixes in particular) so that i can quickly turn songs into videos without worrying too much about visuals

![Example of audio visualizer](https://github.com/astronomy487/littleaudiovisualizer/blob/main/example.png?raw=true)

this is what the output looks like. the image gets scaled so that its 540px tall, and the waveform shows below it. this is literally just a waveform, no fourier transform. the last 6s of audio are shown

## using it

to use this thing, you'll need ffmpeg installed on your machine, because it works by calling ffmpeg. so you should have ffmpeg. also i've only tested this on windows because thats what i use, i make no guarantees about it working anywhere else

you can either run littleaudiovisualizer.exe (like 30 megabytes), or you can run main.py yourself if you feel so inclined. the exe is just main.py compiled using pyinstaller

when you run it, it will open SIX prompts

1. choose an audio file (flac or wav only. i totally could support lossy formats but i'll never want to use that)
2. choose an image file (png or jpg) (no size requirements, it'll get scaled)
3. choose a background color
4. choose "foreground color 1" (fg1)
5. choose "foreground color 2" (fg2)
6. choose where you want to save the video

the waveform itself interpolates beetween the two foreground colors. the waveform is fg1 when it's quietest, and the waveform is fg2 when it's loudest

the machine runs in three steps:

1. draw all the frames to /frames/f(number).bmp, using pillow. the terminal window will tell you every 5% progress it makes during this step
2. stitch the frames into a silent video (hi ffmpeg)
3. combine the video and the audio into a video (hi ffmpeg)

maybe i can combine steps 2 and 3 but im not experienced with ffmpeg so im just happy i got it running

## other details

on my machine (windows 11, 16gb ram, intel core ultra 7), exporting a 3 minute song takes around 3 minutes. around half the time is taken in step 1, around half the time is taken in step 2

the output video is 1748x1080, 60fps. you can also modify it to get other framerates, but you should know that the framerate needs to be a factor of the sample rate (usually 44.1khz) (i.e. you cannot make it do 24 fps lol but you can do 25)