from managers.screen import screen
from managers.automation import auto
from managers.logger import logger
from managers.config import config
from tasks.power.instance import Instance
import time


class Power:
    @staticmethod
    def run():
        Power.preprocess()

        instance_type = config.instance_type
        instance_name = config.instance_names[config.instance_type]

        if not Instance.validate_instance(instance_type, instance_name):
            return False

        logger.hr("开始清体力", 0)

        power = Power.get()

        if "拟造花萼" in instance_type:
            Power.process_calyx(instance_type, instance_name, power)
        else:
            Power.process_standard(instance_type, instance_name, power)

        logger.hr("完成", 2)

    @staticmethod
    def preprocess():
        # 优先合成沉浸器
        if config.merge_immersifier:
            Power.merge("immersifier")

    @staticmethod
    def process_calyx(instance_type, instance_name, power):
        instance_power_max = 60
        instance_power_min = 10

        full_runs = power // instance_power_max
        if full_runs:
            Instance.run(instance_type, instance_name, instance_power_max, full_runs)

        partial_run_power = power % instance_power_max
        if partial_run_power >= instance_power_min:
            Instance.run(instance_type, instance_name, partial_run_power, 1)
        elif full_runs == 0:
            logger.info(f"🟣开拓力 < {instance_power_max}")

    @staticmethod
    def process_standard(instance_type, instance_name, power):
        instance_powers = {
            "凝滞虚影": 30,
            "侵蚀隧洞": 40,
            "历战余响": 30
        }
        instance_power = instance_powers[instance_type]

        full_runs = power // instance_power
        if full_runs:
            Instance.run(instance_type, instance_name, instance_power, full_runs)
        else:
            logger.info(f"🟣开拓力 < {instance_power}")

    @staticmethod
    def customize_run(instance_type, instance_name, power_need, runs):
        if not Instance.validate_instance(instance_type, instance_name):
            return False

        logger.hr(f"准备{instance_type}", 2)

        power = Power.get()

        if power < power_need * runs:
            logger.info(f"🟣开拓力 < {power_need}*{runs}")
            return False
        else:
            return Instance.run(instance_type, instance_name, power_need, runs)

    @staticmethod
    def get():
        def get_power(crop, type="trailblaze_power"):
            try:
                if type == "trailblaze_power":
                    result = auto.get_single_line_text(
                        crop=crop, blacklist=['+', '米'], max_retries=3)
                    power = int(result.replace("1240", "/240").replace("?", "").split('/')[0])
                    return power if 0 <= power <= 999 else -1
                elif type == "reserved_trailblaze_power":
                    result = auto.get_single_line_text(
                        crop=crop, blacklist=['+', '米'], max_retries=3)
                    power = int(result[0])
                    return power if 0 <= power <= 2400 else -1
            except Exception as e:
                logger.error(f"识别开拓力失败: {e}")
                return -1

        def move_button_and_confirm():
            if auto.click_element("./assets/images/zh_CN/base/confirm.png", "image", 0.9, max_retries=10):
                result = auto.find_element(
                    "./assets/images/share/power/trailblaze_power/button.png", "image", 0.9, max_retries=10)
                if result:
                    auto.click_element_with_pos(result, action="down")
                    time.sleep(0.5)
                    result = auto.find_element(
                        "./assets/images/share/power/trailblaze_power/plus.png", "image", 0.9)
                    if result:
                        auto.click_element_with_pos(result, action="move")
                        time.sleep(0.5)
                        auto.mouse_up()
                        if auto.click_element("./assets/images/zh_CN/base/confirm.png", "image", 0.9, max_retries=10):
                            time.sleep(1)
                            auto.press_key("esc")
                            if screen.check_screen("map"):
                                return True
            return False

        trailblaze_power_crop = (1588.0 / 1920, 35.0 / 1080, 198.0 / 1920, 56.0 / 1080)

        if config.use_reserved_trailblaze_power or config.use_fuel:
            screen.change_to('map')
            # 打开开拓力补充界面
            if auto.click_element("./assets/images/share/power/trailblaze_power/trailblaze_power.png", "image", 0.9, crop=trailblaze_power_crop):
                # 等待界面加载
                if auto.find_element("./assets/images/zh_CN/base/confirm.png", "image", 0.9, max_retries=10):
                    # 开启使用后备开拓力
                    if config.use_reserved_trailblaze_power and auto.click_element("./assets/images/share/power/trailblaze_power/reserved_trailblaze_power.png", "image", 0.9, scale_range=(0.95, 0.95)):
                        move_button_and_confirm()
                    # 开启使用燃料
                    elif config.use_fuel and auto.click_element("./assets/images/share/power/trailblaze_power/fuel.png", "image", 0.9, scale_range=(0.95, 0.95)):
                        move_button_and_confirm()
                    # # 开启使用星琼
                    # elif config.stellar_jade and auto.click_element("./assets/images/share/power/trailblaze_power/stellar_jade.png", "image", 0.9, scale_range=(0.95, 0.95)):
                    #     pass
                    else:
                        auto.press_key("esc")

        screen.change_to('map')
        trailblaze_power = get_power(trailblaze_power_crop)

        logger.info(f"🟣开拓力: {trailblaze_power}/240")
        return trailblaze_power

    @staticmethod
    def merge(type):
        if type == "immersifier":
            logger.hr("准备合成沉浸器", 2)
            screen.change_to("guide3")

            immersifier_crop = (1623.0 / 1920, 40.0 / 1080, 162.0 / 1920, 52.0 / 1080)
            text = auto.get_single_line_text(crop=immersifier_crop, blacklist=[
                '+', '米'], max_retries=3)
            if "/8" not in text:
                logger.error("沉浸器数量识别失败")
                return

            immersifier_count = int(text.split("/")[0])
            logger.info(f"🟣沉浸器: {immersifier_count}/8")
            if immersifier_count >= 8:
                logger.info("沉浸器已满")
                return

            screen.change_to("guide3")
            power = Power.get()

            count = min(power // 40, 8 - immersifier_count)
            if count <= 0:
                logger.info("体力不足")
                return

            logger.hr(f"准备合成 {count} 个沉浸器", 2)
            screen.change_to("guide3")

            if auto.click_element("./assets/images/share/power/immersifier/immersifier.png", "image", 0.9, crop=immersifier_crop):
                time.sleep(1)
                for i in range(count - 1):
                    auto.click_element(
                        "./assets/images/share/power/trailblaze_power/plus.png", "image", 0.9)
                    time.sleep(0.5)
                if auto.click_element("./assets/images/zh_CN/base/confirm.png", "image", 0.9, max_retries=10):
                    time.sleep(1)
                    auto.press_key("esc")
