
import asyncio
import pathlib
import shutil

from ..module.general_module import general_module
from .filemanager import FilemanagerClass


class FilecopyClass(FilemanagerClass):

    def __init__(self):
        pass


    async def copy_video(self,
                         src_service_name,
                         src_cid,
                         src_vid,
                         dst_service_name,
                         dst_cid,
                         dst_vid=None):
        # シンボリックリンクなので，vid はコピー先と同じ
        dst_vid = src_vid
        #
        self.make_symlink(dst_vid, dst_service_name, dst_cid)


    async def copy_cid_directory(self,
                                 src_service_name,
                                 src_cid,
                                 dst_service_name,
                                 dst_cid,):
        src_path = "/".join([self.video_dir,
                             src_service_name,
                             src_cid])
        directories = await self.directory_list(src_path)
        for directory in directories:
            # info.jsonがあるものだけコピー対象
            info_json = directory / "info.json"
            if info_json.exists():
                src_vid = str(directory.name)

                await self.copy_video(src_service_name,
                                      src_cid,
                                      src_vid,
                                      dst_service_name,
                                      dst_cid)

        pass
