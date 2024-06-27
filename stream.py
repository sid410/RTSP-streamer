import gi
import cv2
import argparse
import socket

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, cap, fps, width, height, **properties):
        super(SensorFactory, self).__init__(**properties)
        self.cap = cap
        self.number_frames = 0
        self.fps = fps
        self.duration = 1 / self.fps * Gst.SECOND
        self.width = width
        self.height = height
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
                             '! videoconvert ! x264enc speed-preset=ultrafast tune=zerolatency ' \
                             '! rtph264pay name=pay0 pt=96' \
                             .format(self.width, self.height, self.fps)

    def on_need_data(self, src, length):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_LINEAR)
                data = frame.tobytes()
                buf = Gst.Buffer.new_allocate(None, len(data), None)
                buf.fill(0, data)
                buf.duration = self.duration
                timestamp = self.number_frames * self.duration
                buf.pts = buf.dts = int(timestamp)
                buf.offset = timestamp
                self.number_frames += 1
                retval = src.emit('push-buffer', buf)
                if retval != Gst.FlowReturn.OK:
                    print(retval)

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)

class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, cap, fps, width, height, stream_count, ip_address, **properties):
        super(GstServer, self).__init__(**properties)
        self.factories = []
        self.ip_address = ip_address
        self.port = opt.port
        for i in range(stream_count):
            factory = SensorFactory(cap, fps, width, height)
            factory.set_shared(True)
            self.factories.append(factory)
        self.set_service(str(self.port))
        mount_points = self.get_mount_points()
        for i, factory in enumerate(self.factories):
            stream_path = f"/video_stream{i+1}"
            mount_points.add_factory(stream_path, factory)
            print(f"RTSP stream available at: rtsp://{self.ip_address}:{self.port}{stream_path}")
        self.attach(None)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(('10.254.254.254', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, help="video device id or video file location")
    parser.add_argument("--fps", default=30, help="fps of the camera", type=int)
    parser.add_argument("--image_width", default=1280, help="video frame width", type=int)
    parser.add_argument("--image_height", default=720, help="video frame height", type=int)
    parser.add_argument("--port", default=8554, help="port to stream video", type=int)
    parser.add_argument("--stream_count", default=2, help="number of video streams", type=int)
    opt = parser.parse_args()

    try:
        opt.video = int(opt.video)
    except ValueError:
        pass

    cap = cv2.VideoCapture(opt.video)

    Gst.init(None)
    ip_address = get_ip_address()
    server = GstServer(cap, opt.fps, opt.image_width, opt.image_height, opt.stream_count, ip_address)

    loop = GLib.MainLoop()
    loop.run()
