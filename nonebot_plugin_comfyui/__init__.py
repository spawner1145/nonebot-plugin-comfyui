from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.rule import ArgumentParser
from nonebot.plugin.on import on_shell_command, on_command

from .config import Config

from .handler import comfyui_handler

comfyui_parser = ArgumentParser()

comfyui_parser.add_argument("prompt", nargs="*", help="标签", type=str)
comfyui_parser.add_argument("-u", "-U", nargs="*", dest="negative_prompt", type=str, help="Negative prompt")
comfyui_parser.add_argument("--ar", "-ar", dest="accept_ratio", type=str, help="Accept ratio")
comfyui_parser.add_argument("--s", "-s", dest="seed", type=int, help="Seed")
comfyui_parser.add_argument("--steps", "-steps", "-t", dest="steps", type=int, help="Steps")
comfyui_parser.add_argument("--cfg", "-cfg", dest="cfg_scale", type=float, help="CFG scale")
comfyui_parser.add_argument("-n", "--n", dest="denoise_strength", type=float, help="Denoise strength")
comfyui_parser.add_argument("-height", dest="height", type=int, help="Height")
comfyui_parser.add_argument("-width", dest="width", type=int, help="Width")
comfyui_parser.add_argument("-v", dest="video", action="store_true", help="Video output flag")
comfyui_parser.add_argument("-wf", "--work-flows", dest="work_flows", type=str, help="Workflows")
comfyui_parser.add_argument("-sp", "--sampler", dest="sampler", type=str, help="采样器")
comfyui_parser.add_argument("-sch", "--scheduler", dest="scheduler", type=str, help="调度器")
comfyui_parser.add_argument("-b", "--batch_size", dest="batch_size", type=int, help="每批数量")
comfyui_parser.add_argument("-m", "--model", dest="model", type=str, help="模型")


__plugin_meta__ = PluginMetadata(
    name="Comfyui绘图插件",
    description="专门适配Comfyui的绘图插件",
    usage="基础生图命令: prompt, 发送 comfyui帮助 来获取支持的参数",
    config=Config,
    type="application",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={"author": "DiaoDaiaChan", "email": "437012661@qq.com"},
    homepage="https://github.com/DiaoDaiaChan/nonebot-plugin-comfyui"
)

comfyui = on_shell_command(
    "prompt",
    parser=comfyui_parser,
    priority=5,
    block=True,
    handlers=[comfyui_handler]
)

help_ = on_command("comfyui帮助", priority=5, block=True)
help_text = '''
comfyui绘图插件

发送 prompt [正面提示词] 来进行一次最简单的生图
-----其他参数-----
-u 负面提示词
--ar 画幅比例
-s 种子
--steps 采样步数
--cfg CFG scale
-n 去噪强度
-height 高度
-width 宽度
-v 视频输出
-wf 工作流
-sp 采样器
-sch 调度器
-b 每批数量
-m 模型
-----结束-----

例如:
prompt a girl, a beautiful girl, masterpiece -u badhand -ar 1:1 -s 123456 -steps 20 -cfg 7.5 -n 1 -height 512 -width 512 -sp "DPM++ 2M Karras"
'''


@help_.handle()
async def _():
    await help_.finish(help_text)
