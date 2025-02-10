from GraphConvolution import STGCN
import torch
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset





train_dataset = PoseDataset(train_data, train_labels)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

# Initialize model, loss function, and optimizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = STGCN(in_channels=in_channels, num_nodes=num_nodes, num_classes=num_classes, num_frames=num_frames).to(device)
criterion = torch.nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)





# Training loop
num_epochs = 10
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

        total_loss += loss.item()

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss / len(train_loader):.4f}")

print("Training complete!")