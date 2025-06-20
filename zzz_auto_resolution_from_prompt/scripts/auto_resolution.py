import re
import gradio as gr
from modules import scripts, script_callbacks
from modules import shared

setting_key = "auto_resolution_default_enabled"

def on_ui_settings():
    shared.opts.add_option(
        "auto_resolution_default_enabled",
        shared.OptionInfo(
            False,
            "デフォルトでAutoResolutionを有効にする",
            section=("AutoResolution", "auto_resolution_default_enabled")
        )
    )

script_callbacks.on_ui_settings(on_ui_settings)

class Script(scripts.Script):
    def title(self):
        return "AutoResolution"

    def show(self, is_img2img):
        return scripts.AlwaysVisible if not is_img2img else False

    def ui(self, is_img2img):
        default_value = getattr(shared.opts, "auto_resolution_default_enabled", False)

        with gr.Accordion("AutoResolution 設定", open=False):
            enabled = gr.Checkbox(label="プロンプト中の文字列から解像度を自動設定 例:（res_640_960）のように記入", value=default_value)

        return [enabled]

    def process(self, p, enabled):
        if not enabled:
            print("[AutoResolution] チェックOFF")
            return

        prompts = getattr(p, "all_prompts", None)
        if not prompts:
            print("[AutoResolution] 展開後プロンプトなし（Dynamic Prompts未展開）")
            return

        for i, prompt in enumerate(prompts):
            match = re.search(r"res_(\d+)_(\d+)", prompt)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                p.width = width
                p.height = height

                # ✅ プロンプトから解像度指定を削除
                cleaned_prompt = re.sub(r"\s*res_\d+_\d+\s*", " ", prompt)
                p.all_prompts[i] = cleaned_prompt.strip()

                print(f"[AutoResolution] 解像度を {width}x{height} に変更、プロンプトから削除しました")
                return


        print("[AutoResolution] 解像度指定が見つかりませんでした")
