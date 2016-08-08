stream=io.BytesIO()
camera = picamera.PiCamera
camera.resolution = (2592, 1944)
camera.capture (stream, format='jpeg', bayer=True)
print format(stream.seek(0,2),',d')
