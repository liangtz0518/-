from tasks.base.download import download_with_progress
from managers.logger import logger
import subprocess
import tempfile
import shutil
import os


class UpdateHandler:
    def __init__(self, download_url, cover_folder_path, extract_file_name, delete_folder_path=None):
        self.exe_path = os.path.abspath("./assets/binary/7za.exe")
        self.temp_path = os.path.abspath("./temp")
        os.makedirs(self.temp_path, exist_ok=True)
        self.download_url = download_url
        self.download_file_path = os.path.join(self.temp_path, os.path.basename(download_url))
        self.cover_folder_path = cover_folder_path
        self.extract_folder_path = os.path.join(self.temp_path, os.path.basename(extract_file_name))
        self.delete_folder_path = delete_folder_path

    def run(self):
        while True:
            self.download_file()
            if self.extract_file():
                break
        self.cover_folder()
        self.clean_up()

    def download_file(self):
        while True:
            try:
                logger.info(f"开始下载: {self.download_url}")
                download_with_progress(self.download_url, self.download_file_path)
                logger.info(f"下载完成: {self.download_file_path}")
                break
            except Exception as e:
                logger.error(f"下载失败: {e}")
                input("按回车键重试. . .")
                os.remove(self.download_file_path)

    def extract_file(self):
        while True:
            try:
                if not subprocess.run([self.exe_path, "x", self.download_file_path, f"-o{self.temp_path}", "-aoa"], check=True):
                    raise Exception
                logger.info(f"解压完成: {self.extract_folder_path}")
                return True
            except Exception as e:
                logger.error(f"解压失败: {e}")
                input("按回车键重新下载. . .")
                os.remove(self.download_file_path)
                return False

    def cover_folder(self):
        while True:
            try:
                if self.delete_folder_path and os.path.exists(self.delete_folder_path):
                    shutil.rmtree(self.delete_folder_path)
                shutil.copytree(self.extract_folder_path, self.cover_folder_path, dirs_exist_ok=True)
                logger.info(f"覆盖完成: {self.cover_folder_path}")
                break
            except Exception as e:
                logger.error(f"覆盖失败: {e}")
                input("按回车键重试. . .")

    def clean_up(self):
        try:
            os.remove(self.download_file_path)
            logger.info(f"清理完成: {self.download_file_path}")
            shutil.rmtree(self.extract_folder_path)
            logger.info(f"清理完成: {self.extract_folder_path}")
        except Exception as e:
            logger.warning(f"清理失败: {e}")
