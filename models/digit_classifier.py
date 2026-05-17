"""
Handwritten digit classifier
============================
Uses MNIST dataset from torch.datasets.MNIST 
- Takes in 784 pixels 28x28 pixels flattened
- 128 Hidden  Neurons
- 10 output classes
    - 0-9
"""

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import v2
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
from pathlib import Path

# -------- Device --------
if torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(f"Using {device} device")

# ----- Neural Network and Training ---------
class DigitClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.network = nn.Sequential(
            nn.Linear(28*28, 128),
            nn.ReLU(),
            nn.Linear(128, 10),
        )
        
    def forward(self, x):
        x = self.flatten(x)
        logits = self.network(x)
        return logits

# ------ Datasets --------
transform = v2.Compose([
    v2.ToImage(),
    v2.ToDtype(torch.float32, scale=True),
    v2.Normalize((0.5,), (0.5,))
])

training_data = datasets.MNIST('./data', train=True, transform=transform, download=True)
validation_data = datasets.MNIST('./data', train=False, transform=transform, download=True)

train_dataloader = DataLoader(training_data, batch_size=64, shuffle=True)
validation_dataloader = DataLoader(validation_data, batch_size=64, shuffle=True)

classes = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9",)

# ----- Training ------
model = DigitClassifier().to(device)
print(model)
loss_fn = nn.CrossEntropyLoss() # Googling why class predicition wouldn't work with MSE i couldn't find a why only the fix
optimizer = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

def train_one_epoch(epochs, tb_writer):
    running_loss = 0.
    last_loss = 0.

    for i, data in enumerate(train_dataloader):
        inputs, labels = data
        inputs = inputs.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)

        loss = loss_fn(outputs, labels)
        loss.backward()

        optimizer.step()

        running_loss += loss.item()
        if i % 100 == 99:
            last_loss = running_loss / 100 
            print(f'  batch {i + 1} loss: {last_loss}')
            tb_x = epochs * len(train_dataloader) + i + 1
            tb_writer.add_scalar('Loss/train', last_loss, tb_x)
            running_loss = 0.

    return last_loss

def traingloop():
    epochs = 50
    timestamp = datetime.now().strftime('%Y%m%d_%H')
    writer = SummaryWriter(f'runs/digit_classifier_{timestamp}')
    best_vloss = 1000000 # baseline for conditional check (avg_vloss < best_vloss) for saving
    epoch_number = 0

    for epoch in range(epochs):
        print(f'EPOCH {epoch_number + 1}:')
        model.train(True)
        avg_loss = train_one_epoch(epoch_number, writer)

        running_vloss = 0.0
        model.eval()
        with torch.no_grad():
            for i, vdata in enumerate(validation_dataloader):
                vinputs, vlabels = vdata
                vinputs = vinputs.to(device)
                vlabels = vlabels.to(device)

                voutputs = model(vinputs)
                vloss = loss_fn(voutputs, vlabels)
                running_vloss += vloss

        avg_vloss = running_vloss / (i + 1)
        print(f'Training loss {avg_loss}, Validation {avg_vloss}')
        print(f'=' * 50)

        writer.add_scalars('Training vs. Validation Loss',
                           { 'Training' : avg_loss, 'Validation' : avg_vloss },
                           epoch_number + 1)
        writer.flush()

        if avg_vloss < best_vloss:
            best_vloss = avg_vloss
            project_root = Path(__file__).resolve().parent.parent
            weights_path = project_root / "weights" / "digitclassifier" / "model_{timestamp}_{epoch_number}"
            torch.save(model.state_dict(), weights_path)
        epoch_number += 1

if __name__ == "__main__":
    traingloop()