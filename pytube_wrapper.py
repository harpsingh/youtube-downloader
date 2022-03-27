from pytube import YouTube


class YouTubeClient(YouTube):

    def __init__(self, url: str, **kwargs):
        super().__init__(url, **kwargs)
        self.filename = None
        self.stream_list = None
        self.best_video_stream = None
        self.best_audio_stream = None
        self.video_processing = False
        self.video_file = None
        self.audio_file = None

    def get_best_streams(self):
        self.best_video_stream = self.stream_list.filter(type="video").order_by("resolution").last()
        self.best_audio_stream = self.stream_list.filter(type="audio").order_by("abr").last()

