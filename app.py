from transformers import AutoProcessor, AutoModelForImageTextToText
import requests
import torch
from torchvision import io
from typing import Dict
import gradio as gr
from PIL import Image

processor = AutoProcessor.from_pretrained("JackChew/Qwen2-VL-2B-OCR")
model = AutoModelForImageTextToText.from_pretrained("JackChew/Qwen2-VL-2B-OCR").to("cuda")


def OCR(image: Image.Image):
    conversation = [
        {
            "role":"user",
            "content":[
                {
                    "type":"image",
                },
                {
                    "type":"text",
                    "text":"extract all data from this payslip without miss anything"
                }
            ]
        }
    ]

    # Preprocess the inputs
    text_prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)
    # Excepted output: '<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n<|vision_start|><|image_pad|><|vision_end|>Describe this image.<|im_end|>\n<|im_start|>assistant\n'

    inputs = processor(text=[text_prompt], images=[image], padding=True, return_tensors="pt")
    inputs = inputs.to('cuda')

    # Inference: Generation of the output
    output_ids = model.generate(**inputs, max_new_tokens=2048)
    generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, output_ids)]
    output_text = processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    print(output_text[0])
    return output_text[0]

   
demo=gr.Interface(
    fn=OCR,                      # Function to call
    inputs=gr.Image(type="pil"),     # Input component (image as PIL object)
    outputs="text",                  # Output component (text for class)
    title="OVision OCR",
    description="Upload an image"
)
    # Launch the app
demo.launch()


