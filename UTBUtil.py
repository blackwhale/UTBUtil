from contextlib import closing
import requests
import os
from tqdm import tqdm
from urlparse import urlparse, parse_qs


class UTBUtil:
    author = ''
    title = ''
    exts = {
        '18': 'mp4',
        '22': 'mp4',
        '37': 'mp4',
        '38': 'mp4',
    }

    def __init__(self, url):
        self.info = self._get_info(url)
        self.vinfo = self._get_video_info()

    def _get_info(self, url):
        info_url = self._get_videoid(url)
        conn = requests.post(info_url)
        body = parse_qs(conn.text.encode('utf-8'))
        s_map = body.get('url_encoded_fmt_stream_map', [])
        self.author = body.get('author', ['unknown'])[0]
        self.title = body.get('title', ['unknown'])[0]

        if not s_map:
            return []
        return s_map[0].split(',')

    def _get_videoid(self, url):
        conn = requests.get(url)
        body = conn.text.encode('utf-8')
        ind = body.find('videoId')
        videoid = body[ind+18:ind+29]
        fmt = 'http://youtube.com/get_video_info?video_id={0}'
        return fmt.format(videoid)

    def _get_video_info(self):
        temp_d = {}
        for i in self.info:
            qry = parse_qs(i)
            if qry['itag'][0] in self.exts:
                temp_d[qry['itag'][0]] = qry
        return temp_d

    def dl_video(self, csize=102400):
        keys = self.vinfo.keys()
        keys.sort()
        if keys:
            video = self.vinfo[keys[-1]]
        else:
            raise ValueError('No available video formats')

        url = video['url'][0]
        ext = self.exts[video['itag'][0]]
        with closing(requests.get(url, stream=True)) as resp:
            size = int(resp.headers.get('Content-Length'))
            fn = self.title + '.' + ext
            with open(fn, 'wb') as of:
                for chunk in tqdm(resp.iter_content(chunk_size=csize),
                                  total=int((size+csize-1)/csize)):
                    of.write(chunk)
