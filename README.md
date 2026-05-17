# Aurelius Python Tools

> This folder contains a vareity of tools and projects in python.

## Models
This includes AI/ML related models including:
- Digit Classfier Model (Pytorch)
- Supervised Learning Car Tuning Model (Pytorch) Uncompleted

## RedPy
This also includes a very simple python variant of Redis that is yet to be completed fully.
While it works, active expiry and persistance still needs to be added which will be in the next 
push.
- Requires redis-cli
- Ncat can also be used for example: echo -e "*3\r\n\$3\r\nSET\r\n\$3\r\nfoo\r\n\$3\r\nbar\r\n" | ncat 127.0.0.1 6379 

## Datasets
We use the MNIST dataset for this project. The models code auto installs the data using the following PyTorch code:

```python
training_data = datasets.MNIST('./data', train=True, transform=transform, download=True)
validation_data = datasets.MNIST('./data', train=False, transform=transform, download=True)
```

## Misc
These contain the runs and weights. These are just for the models.