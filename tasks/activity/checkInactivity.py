import time
from managers.automation import auto
from managers.logger import logger
from .activitytemplate import ActivityTemplate


class CheckInActivity(ActivityTemplate):
    RECEIVE_PATH = "./assets/images/zh_CN/activity/double/receive.png"
    RECEIVE_FIN_PATH = "./assets/images/zh_CN/activity/double/receive_fin.png"
    CLOSE_PATH = "./assets/images/zh_CN/base/click_close.png"
    IMAGE_SIMILARITY_THRESHOLD = 0.8

    def _has_reward(self):
        return auto.find_element(CheckInActivity.RECEIVE_PATH, "image", CheckInActivity.IMAGE_SIMILARITY_THRESHOLD) or \
            auto.find_element(CheckInActivity.RECEIVE_FIN_PATH, "image", CheckInActivity.IMAGE_SIMILARITY_THRESHOLD)

    def _has_reward(self):
        while auto.click_element(CheckInActivity.RECEIVE_PATH, "image", CheckInActivity.IMAGE_SIMILARITY_THRESHOLD) or \
                auto.click_element(CheckInActivity.RECEIVE_FIN_PATH, "image", CheckInActivity.IMAGE_SIMILARITY_THRESHOLD):
            auto.click_element(CheckInActivity.CLOSE_PATH, "image", CheckInActivity.IMAGE_SIMILARITY_THRESHOLD, max_retries=10)
            time.sleep(1)

    def run(self):
        if self._has_reward():
            logger.hr(f"检测到{self.name}奖励", 2)
            self._collect_rewards()
            logger.info(f"领取{self.name}奖励完成")
