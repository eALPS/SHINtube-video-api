import os
import random
import string
import json
import shutil
import glob
import aiofiles
import datetime

import asyncio
from functools import wraps, partial


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


# 保存先のビデオフォルダ
video_dir = "video"


def GetRandomStr(num) -> str:
    # 英数字をすべて取得
    dat = string.digits + string.ascii_lowercase + string.ascii_uppercase

    # 英数字からランダムに取得
    return ''.join([random.choice(dat) for i in range(num)])


def read_json(json_file):
    try:
        with open(json_file) as f:
            _dict = json.load(f)
    except FileNotFoundError:
        return False
    else:
        return _dict


def write_json(json_file, _dict):
    try:
        with open(json_file, "w") as f:
            json.dump(_dict, f, indent=4)
    except BaseException:
        return False
    else:
        return True


def write_playlist(playlist_file: str, _list: list, add=False):
    if add:
        mode = "a"
    else:
        mode = "w"
    with open(playlist_file, mode) as f:
        f.writelines('\n'.join(_list))
        f.write("\n")


async def create_directory(year, cid, title, explanation) -> str:
    _created_dir = None
    while True:
        try:
            _created_dir = "/".join([video_dir, str(year),
                                     cid, GetRandomStr(10)])
            await async_wrap(os.makedirs)(_created_dir)
        except FileExistsError:
            pass
        else:
            break
    dict_template = {
        "title": title,
        "explanation": explanation,
        "created_at": datetime.datetime.today().isoformat(),
        "updated_at": datetime.datetime.today().isoformat(),
        "resolution": [],
        "encode_tasks": []
    }
    write_json(_created_dir + "/info.json", dict_template)
    playlist_template = ["#EXTM3U", "#EXT-X-VERSION:3"]
    write_playlist(_created_dir + "/playlist.m3u8", playlist_template)
    return _created_dir


async def delete_directory(year, cid, vid):
    _delete_dir = "/".join([video_dir, str(year), cid, vid])
    await async_wrap(shutil.rmtree)(_delete_dir)
    return True


def delete_video(year, cid, vid):
    _delete_dir = "/".join([video_dir, str(year), cid, vid])
    for filepath in glob.glob(f"{_delete_dir}/*"):
        if "info.json" in filepath:
            pass
        else:
            os.remove(filepath)
    # プレイリストの初期化
    playlist_file = "/".join([video_dir, str(year), cid, vid, "playlist.m3u8"])
    playlist_template = ["#EXTM3U", "#EXT-X-VERSION:3"]
    write_playlist(playlist_file, playlist_template)
    # 既存のjsonを読み込み
    json_file = "/".join([video_dir, str(year), cid, vid, "info.json"])
    _dict = read_json(json_file)
    if not _dict:
        return False
    # jsonの更新
    _dict["resolution"] = []
    _dict["encode_tasks"]= []
    _dict["updated_at"] = datetime.datetime.today().isoformat()
    # jsonの書き込み
    if write_json(json_file, _dict):
        return True
    return False


def update_json(year, cid, vid, title, explanation):
    # 既存のjsonを読み込み
    json_file = "/".join([video_dir, str(year), cid, vid, "info.json"])
    _dict = read_json(json_file)
    if not _dict:
        return False
    # jsonの更新
    _dict["title"] = title
    _dict["explanation"] = explanation
    # jsonの書き込み
    if write_json(json_file, _dict):
        return True
    return False


async def list_video_id(year, cid):
    _video_dir = "/".join([video_dir, str(year), cid])
    temp = await async_wrap(glob.glob)(f"{_video_dir}/*")
    return [video_id.split("/")[-1]
            for video_id in temp]


async def list_link(year, cid):
    _video_dir = "/".join([video_dir, str(year), cid])
    temp = await async_wrap(glob.glob)(f"{_video_dir}/*")
    result = {}
    for link_path in temp:
        json_file = link_path + "/info.json"
        try:
            with open(json_file) as f:
                _dict = await async_wrap(json.load)(f)
        except FileNotFoundError:
            pass
        result[link_path.split("/")[-1]] = _dict
    return result


def add_resolution(folderpath, resolution):
    _list = {
        240: [
            "#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=426x240",
            "240p.m3u8"],
        360: [
            "#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=640x360",
            "360p.m3u8"],
        480: [
            "#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=854x480",
            "480p.m3u8"],
        720: [
            "#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1280x720",
            "720p.m3u8"],
        1080: [
            "#EXT-X-STREAM-INF:BANDWIDTH=8000000,RESOLUTION=1920x1080",
            "1080p.m3u8"],
    }
    playlist = "/".join([folderpath, "playlist.m3u8"])
    write_playlist(playlist, _list[int(resolution)], add=True)
    # 既存のjsonを読み込み
    json_file = "/".join([folderpath, "info.json"])
    _dict = read_json(json_file)
    if not _dict:
        return False
    # 画質の追加
    _dict["resolution"].append(f"{resolution}p")
    _dict["encode_tasks"].remove(f"{resolution}p")
    # jsonの書き込み
    if write_json(json_file, _dict):
        return True
    return False


def add_resolution_task(folderpath, resolution):
    # 既存のjsonを読み込み
    json_file = "/".join([folderpath, "info.json"])
    _dict = read_json(json_file)
    if not _dict:
        return False
    # 画質の追加
    _dict["encode_tasks"].append(f"{resolution}p")
    # jsonの書き込み
    if write_json(json_file, _dict):
        return True
    return False
