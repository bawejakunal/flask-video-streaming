import time
import threading
from base_camera import CameraEvent
# from base_camera import BaseCamera

# singleton class
class Camera(object):

    __instance = dict()
    lock = threading.Lock()

    def __new__(cls, pid):
        with Camera.lock:
            if pid not in cls.__instance:
                instance = object.__new__(cls)
                instance.pid = pid
                instance.frame = None
                instance.last_access = time.time()
                instance.event = CameraEvent()
                instance.thread = \
                    threading.Thread(target=instance._thread)
                instance.thread.start()
                cls.__instance[pid] = instance

        return cls.__instance[pid]

    def get_frame(self):
        """Return the current camera frame."""
        self.last_access = time.time()

        # wait for a signal from the camera thread
        self.event.wait()
        self.event.clear()

        return self.frame

    def frames(self):
        """"Generator that returns frames from the camera."""
        imgs = ['1.jpg', '2.jpg', '3.jpg']
        while True:
            """read mqttc topic here and update the queue then yield front"""
            time.sleep(1)
            idx = int(time.time()) % 3
            img = open(imgs[idx], 'rb')
            content = img.read()
            img.close()
            yield content

    def _thread(self):
        """Camera background thread."""
        print('Starting camera thread.')
        frames_iterator = self.frames()
        for frame in frames_iterator:
            self.frame = frame
            self.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            if time.time() - self.last_access > 10:
                frames_iterator.close()
                print('Stopping camera thread due to inactivity.')
                break

        with Camera.lock:
            del Camera.__instance[self.pid]
