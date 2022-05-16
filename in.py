import torch

model = torch.hub.load("ultralytics/yolov5", "yolov5s")

img = "x.jpg"

results = model(img)

results.save(save_dir = "./")
