from GraphConvolution import STGCN
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from formatDataset import PoseDataset

# Load dataset
dataset_path = "pose_dataset_interpolated.npy"
train_dataset = PoseDataset(dataset_path)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

# Define ST-GCN model parameters
in_channels = 3    # x, y, z coordinates
num_nodes = 33     # BlazePose keypoints
num_classes = 5    # Unique labels
num_frames = 60   # Fixed frame length

# Initialize model, loss function, and optimizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = STGCN(in_channels=in_channels, num_nodes=num_nodes, num_classes=num_classes, num_frames=num_frames).to(device)
criterion = torch.nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
num_epochs = 50
for epoch in range(num_epochs):
    model.train()
    total_loss = 0

    for batch in train_loader:
        inputs, labels = batch
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # Get the predicted class (index with the highest score)
        _, predicted = torch.max(outputs, 1)

        # Check if the predictions match the true labels
        correct = (predicted == labels).sum().item()

        # Calculate accuracy
        accuracy = correct / labels.size(0)  # labels.size(0) is the batch size
        print(f'Accuracy: {accuracy * 100:.2f}%')


        total_loss += loss.item()

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss / len(train_loader):.4f}")

print("Training complete!")


