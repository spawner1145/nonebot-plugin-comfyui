import re


def replace_lora_nodes(input_string, base_json):
    # 找出原有的 LoRA 节点及其前后连接的节点
    lora_node_id = None
    prev_node_output = None
    next_node_id = None
    next_node_input_key = None

    for node_id, node in base_json["prompt"].items():
        if node["class_type"] == "LoraLoader":
            lora_node_id = node_id
            # 找到前一个节点的输出
            prev_node_output = node["inputs"]["model"]
            # 查找连接到这个 LoRA 节点输出的下一个节点
            for next_id, next_node in base_json["prompt"].items():
                for input_key, input_value in next_node["inputs"].items():
                    if isinstance(input_value, list) and input_value[0] == lora_node_id:
                        next_node_id = next_id
                        next_node_input_key = input_key
                        break
                if next_node_id:
                    break
            break

    # 如果找到原有的 LoRA 节点，移除它
    if lora_node_id:
        del base_json["prompt"][lora_node_id]

    # 正则表达式用于匹配 <lora:name:weight> 格式
    lora_pattern = r'<lora:([^:]+):([^>]+)>'
    lora_matches = re.findall(lora_pattern, input_string)
    lora_info = [(name, float(weight)) for name, weight in lora_matches]

    # 如果没有找到前一个节点的输出，尝试默认从 CheckpointLoaderSimple 节点开始
    if not prev_node_output:
        for node_id, node in base_json["prompt"].items():
            if node["class_type"] == "CheckpointLoaderSimple":
                prev_node_output = [node_id, 0]
                break

    if not prev_node_output:
        raise ValueError("Could not find a valid starting node for LoRA.")

    # 开始添加新的 LoRA 节点
    next_node_id_to_use = max(int(id) for id in base_json["prompt"].keys()) + 1
    for name, weight in lora_info:
        lora_node = {
            "class_type": "LoraLoader",
            "inputs": {
                "model": prev_node_output,
                "lora_name": f"{name}.safetensors",
                "strength_model": weight,
                "strength_clip": weight
            }
        }
        base_json["prompt"][str(next_node_id_to_use)] = lora_node
        # 更新下一个 LoRA 节点的输入模型
        prev_node_output = [str(next_node_id_to_use), 0]
        next_node_id_to_use += 1

    # 如果找到后续连接的节点，更新其输入
    if next_node_id and next_node_input_key:
        base_json["prompt"][next_node_id]["inputs"][next_node_input_key] = prev_node_output
    else:
        # 如果没有找到后续连接节点，假设是连接到 KSampler 节点
        for node_id, node in base_json["prompt"].items():
            if node["class_type"] == "KSampler":
                node["inputs"]["model"] = prev_node_output
                break

    return base_json


# 示例输入字符串，包含多个 LoRA 标签
input_string = "<lora:lora1:0.7> <lora:lora2:0.8> <lora:lora3:0.9>"

# 示例的 ComfyUI 基础工作流 JSON 数据，包含一个 LoRA 节点
base_json = {
    "prompt": {
        "1": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["3", 0],
                "seed": 12345,
                "steps": 20,
                "cfg": 7,
                "sampler_name": "euler",
                "scheduler": "normal",
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["6", 0]
            }
        },
        "2": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "v1-5-pruned-emaonly.ckpt"
            }
        },
        "3": {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["2", 0],
                "lora_name": "old_lora.safetensors",
                "strength_model": 0.5,
                "strength_clip": 0.5
            }
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "A beautiful scene",
                "clip": ["2", 1]
            }
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "ugly, blurry",
                "clip": ["2", 1]
            }
        },
        "6": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            }
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {
                "vae": ["2", 2],
                "samples": ["1", 0]
            }
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["7", 0]
            }
        }
    },
    "client_id": "example_client_id"
}

# 调用函数替换 LoRA 节点
updated_json = replace_lora_nodes(input_string, base_json)

# 打印更新后的工作流 JSON 数据
import json
print(json.dumps(updated_json, indent=4))
