# Social-Distancing Monitoring and Tracking on AI Platform via Edge-Computing
This is a project which implement high-quality social-distancing monitoring system on NVIDIA Jetson Nano and Jetson Xavier.  
This allows real-time human tracking on the video(or webcam), categorizing person as 'definite risk' if he/she exceeds a 'threshold time' we set.
The purpose of this project is to distribute croweded area by visualizing safety level on every region.
  
## Key features
### Model 
<img src="demo/table-runtime-analysis.jpg" width="60%" height="60%"></img><br/>  
The runtime on the table above is evaluated with 640 pixel demo video.
Among these models, YOLOv4-tiny-3L showed the best balance between AP and FPS.
  
### TensorRT
(to be updated soon)

### Transfer Learning
Since the model only has to detect human, we did transfer learning of YOLOv4-tiny-3L with crowd-human dataset.  
AP of the model improved.  
(AP/FPS comparison datasheet)  

### Human Tracking Algorithm
<img src="demo/video-tracking-def.gif" width="50%" height="50%"></img><br/>

## Usage
```script  
  ## Main-thread(Algorithm, Web framework) & Child-thread(Model)
  $ python3 server_async.py

  ## Main-thread(Web framework) & Child-thread(Model, Algorithm)
  $ python3 server_async2.py
```
  
## Environment
* Platform: NVIDIA Jetson Nano Developer Kit 4GB, NVIDIA Jetson Xavier (full-name needed)
* Camera : Logitech C270 webcam
* Libraries: TensorRT, OpenCV, NumPy, PyCUDA, etc. (version needed)

## Demo Videos
### Tracking People
<img src="demo/video-tracking-full.gif" width="70%" height="70%"></img><br/>
  
### Monitoring Social-Distancing
<img src="demo/video-monitoring-full.gif" width="70%" height="70%"></img><br/>

## Improvements
- [x] Consider Jetson Xavier as a platform
- [x] Model Analysis of YOLOv4-tiny-3L
- [x] Mdoel Optimization of YOLOv4-tiny-3L
- [x] Pipelining(Multi-threading)
- [x] Test on Real-time environment
- [x] Website streaming service using OpenCV, Flask
- [x] Calculate safety level
  
## References
* TensorRT demo code : https://github.com/jkjung-avt/tensorrt_demos
* Crowd-Human Dataset : https://www.crowdhuman.org
* Transfer-Learning demo code : (to be updated soon)
* Social-Distancing using YOLOv5 : https://github.com/ChargedMonk/Social-Distancing-using-YOLOv5
* Social-Distancing Monitoring :  https://github.com/dongfang-steven-yang/social-distancing-monitoring
* Web Streaming from IP camera with Flask : https://gist.github.com/raiever/df5b6c48217df521094cbe2d12c32c66
* OpenCV Stream Video to Web : https://github.com/pornpasok/opencv-stream-video-to-web
