import os

os.add_dll_directory(os.getcwd())
os.add_dll_directory('D:\\tmp_programs\\VLC')
from vk_api.utils import get_random_id
import key
import vlc
import requests
import yt
import vk_api
import pafy

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard
from collections import deque
from yt import Song

class Keybooard:
    def __init__(self):
        self.state = 0
        self.states = 1

    def getKeybord(self, state=0):
        kb = VkKeyboard()
        if state == 2:
            kb.add_button('1')
            kb.add_button('2')
            kb.add_button('3')
            return kb.get_keyboard()
        if self.state == 0:
            kb.add_button('▶')
            kb.add_button('⏭')
        elif self.state == 1:
            kb.add_button('⏸')
            kb.add_button('⏭')
        print(self.state)
        return kb.get_keyboard()

    def next(self):
        self.state += 1
        if self.state > self.states:
            self.state = 0


class Seq:
    def __init__(self):
        self.songs_seq = deque()
        self.playlist = []
        self.vlcInstance = vlc.Instance()
        self.player = self.vlcInstance.media_player_new()
        self.state = 0

    def play(self):
        if len(self.songs_seq) == 0:
            return
        self.state = 1
        video = pafy.new(self.songs_seq[0].link)
        best = video.getbest()
        playurl = best.url
        Media = self.vlcInstance.media_new(playurl)
        Media.get_mrl()
        self.player.set_media(Media)
        self.player.play()
        self.log()
        print('now playing' + self.songs_seq[0].name)

    def pause(self):
        if len(self.songs_seq) == 0:
            pass
        self.player.stop()
        self.state = 0
        self.log()

    def count(self):
        return len(self.songs_seq)

    def to_str(self):
        s = ''
        i = 0
        for song in self.songs_seq:
            s += '[' + str(i) + ']' + song.name
            s += '\n'
            i += 1
        if s == '':
            return 'song list is empty'
        return s

    def push(self, song):
        self.songs_seq.append(song)
        if len(self.songs_seq) == 1:
            self.play()
        self.log()

    def pop(self):
        self.songs_seq.popleft()
        self.pause()
        self.log()

    def next(self):
        if len(self.songs_seq) == 0:
            pass
        else:
            sq.pause()
            sq.pop()
            if len(self.songs_seq) != 0:
                sq.play()

    def log(self):
        self.to_str()


class MyLongPoll(VkLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print(e)


def send(vk, peer, rand, message, kb):
    if kb == 0:
        vk.messages.send(
            peer_id=peer,
            random_id=rand,
            message=message,
        )
        return
    vk.messages.send(
        peer_id=peer,
        random_id=rand,
        message=message,
        keyboard=kb
    )


session = requests.Session()
vk_session = vk_api.VkApi(token=key.key)

longpoll = MyLongPoll(vk_session)
vk = vk_session.get_api()

kb = Keybooard()
sq = Seq()
limks = []
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        if event.text == '▶':
            sq.play()
            kb.next()
            send(vk, event.peer_id, get_random_id(), sq.to_str(), kb.getKeybord())
            continue
        if event.text == '⏸':
            sq.pause()
            kb.next()
            send(vk, event.peer_id, get_random_id(), sq.to_str(), kb.getKeybord())
            continue
        if event.text == '⏭':
            sq.next()
            send(vk, event.peer_id, get_random_id(), sq.to_str(), kb.getKeybord())
            continue
        if event.text.find('youtube') >= 0:
            print('yt req')
            # TODO name to song
            # TODO try catch
            sq.push(Song(event.text, 'todo'))
            send(vk, event.peer_id, get_random_id(), sq.to_str(), kb.getKeybord())
            continue
        if event.text in ['1', '2', '3']:
            # TODO try catch
            sq.push(links[int(event.text) - 1])
            send(vk, event.peer_id, get_random_id(), sq.to_str(), kb.getKeybord())
            continue
        else:
            links = yt.get(event.text)
            if links:
                link_list = ''
                for i in range(len(links)):
                    link_list += '[' + str(i + 1) + '] ' + links[i].name + '\n'
                send(vk, event.peer_id, get_random_id(), link_list, kb.getKeybord(state=2))
            else:
                send(vk, event.peer_id, get_random_id(), 'nothing found', kb.getKeybord())
            print(sq.to_str())
            continue
