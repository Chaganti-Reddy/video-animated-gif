import streamlit as st
import os
import base64
import tempfile
from PIL import image
import numpy as np
from moviepy.editor import videofileclip
import moviepy.video.fx.all as vfx

## session state ##
if 'clip_width' not in st.session_state:
    st.session_state.clip_width = 0
if 'clip_height' not in st.session_state:
    st.session_state.clip_height = 0
if 'clip_duration' not in st.session_state:
    st.session_state.clip_duration = 0
if 'clip_fps' not in st.session_state:
    st.session_state.clip_fps = 0
if 'clip_total_frames' not in st.session_state:
    st.session_state.clip_total_frames = 0  

st.set_page_config(
    page_title="video to animated gif",
    layout="wide",
    page_icon="🎈",
    menu_items={
        "get help": "https://github.com/chaganti-reddy/video-animated-gif",
        "report a bug": "https://github.com/chaganti-reddy/video-animated-gif/issues",
        "about": "video to animated gif's using *python & streamlit*",
    },
)
    
st.title('🎈 animated gif maker')

## upload file ##
st.sidebar.header('upload file')
uploaded_file = st.sidebar.file_uploader("choose a file", type=['mov', 'mp4'])
st.sidebar.markdown('''
[download example file](https://github.com/chaganti-reddy/video-animated-gif/blob/main/example/streamlit-app-starter-kit-screencast.mov)

---
made with ❤️ by venkatarami reddy ([chaganti reddy](https://github.com/chaganti-reddy))
''')

## display gif generation parameters once file has been uploaded ##
if uploaded_file is not none:
  ## save to temp file ##
  tfile = tempfile.namedtemporaryfile(delete=false) 
  tfile.write(uploaded_file.read())
  
  ## open file ##
  clip = videofileclip(tfile.name)
    
  st.session_state.clip_duration = clip.duration
  
  ## input widgets ##
  st.sidebar.header('input parameters')
  selected_resolution_scaling = st.sidebar.slider('scaling of video resolution', 0.0, 1.0, 0.5 )
  selected_speedx = st.sidebar.slider('playback speed', 0.1, 10.0, 5.0)
  selected_export_range = st.sidebar.slider('duration range to export', 0, int(st.session_state.clip_duration), (0, int(st.session_state.clip_duration) ))
    
  ## resizing of video ##
  clip = clip.resize(selected_resolution_scaling)
     
  st.session_state.clip_width = clip.w
  st.session_state.clip_height = clip.h
  st.session_state.clip_duration = clip.duration
  st.session_state.clip_total_frames = clip.duration * clip.fps
  st.session_state.clip_fps = st.sidebar.slider('fps', 10, 60, 20)
    
  ## display output ##
  st.subheader('metrics')
  col1, col2, col3, col4, col5 = st.columns(5)
  col1.metric('width', st.session_state.clip_width, 'pixels')
  col2.metric('height', st.session_state.clip_height, 'pixels')
  col3.metric('duration', st.session_state.clip_duration, 'seconds')
  col4.metric('fps', st.session_state.clip_fps, '')
  col5.metric('total frames', st.session_state.clip_total_frames, 'frames')

  # extract video frame as a display image
  st.subheader('preview')

  with st.expander('show image'):
    selected_frame = st.slider('preview a time frame (s)', 0, int(st.session_state.clip_duration), int(np.median(st.session_state.clip_duration)) )
    clip.save_frame('frame.gif', t=selected_frame)
    frame_image = image.open('frame.gif')
    st.image(frame_image)

  ## print image parameters ##
  st.subheader('image parameters')
  with st.expander('show image parameters'):
    st.write(f'file name: `{uploaded_file.name}`')
    st.write('image size:', frame_image.size)
    st.write('video resolution scaling', selected_resolution_scaling)
    st.write('speed playback:', selected_speedx)
    st.write('export duration:', selected_export_range)
    st.write('frames per second (fps):', st.session_state.clip_fps)
    
  ## export animated gif ##
  st.subheader('generate gif')
  generate_gif = st.button('generate animated gif')
  
  if generate_gif:
    clip = clip.subclip(selected_export_range[0], selected_export_range[1]).speedx(selected_speedx)
    
    frames = []
    for frame in clip.iter_frames():
        frames.append(np.array(frame))
    
    image_list = []

    for frame in frames:
        im = image.fromarray(frame)
        image_list.append(im)

    image_list[0].save('export.gif', format = 'gif', save_all = true, loop = 0, append_images = image_list)
    
    #clip.write_gif('export.gif', fps=st.session_state.clip_fps)
    
    ## download ##
    st.subheader('download')
    
    #video_file = open('export.gif', 'rb')
    #video_bytes = video_file.read()
    #st.video(video_bytes)
    
    file_ = open('export.gif', 'rb')
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()
    st.markdown(
        f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
        unsafe_allow_html=true,
    )
    
    fsize = round(os.path.getsize('export.gif')/(1024*1024), 1)
    st.info(f'file size of generated gif: {fsize} mb', icon='💾')
    
    fname = uploaded_file.name.split('.')[0]
    with open('export.gif', 'rb') as file:
      btn = st.download_button(
            label='download image',
            data=file,
            file_name=f'{fname}_scaling-{selected_resolution_scaling}_fps-{st.session_state.clip_fps}_speed-{selected_speedx}_duration-{selected_export_range[0]}-{selected_export_range[1]}.gif',
            mime='image/gif'
          )

## default page ##
else:
  st.warning('👈 upload a video file')
