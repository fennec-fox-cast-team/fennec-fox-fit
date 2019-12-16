from torchvision import models, transforms
import torch
import PIL


class_names = {0: 'sushi',
               1: 'hamburger',
               2: 'pizza',
               3: 'omelet',
               4: 'hot dog',
               5: 'sandwiches',
               6: 'sausage',
               7: 'beef steak'}

transformation = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(244),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

model = models.resnet50()
model.fc = torch.nn.Sequential(torch.nn.Linear(in_features=2048,
                                               out_features=len(class_names),
                                               bias=True))

model.load_state_dict(torch.load('app/model/food_clf.pth', map_location=torch.device('cpu')))
model.eval()


def get_prediction(img):
    outputs = model(transformation(img).view(1, 3, 244, 244))
    _, preds = torch.max(outputs.data, 1)

    return class_names[preds.tolist()[0]]


if __name__ == '__main__':
    img = PIL.Image.open('tests/sausage1.jpeg')
    print('Prediction:', get_prediction(img))
