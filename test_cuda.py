import torch
import torch.nn as nn
import time


# Configurazione dispositivo
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Dispositivo usato: {device}")

if device == 'cuda':
    print(f"GPU rilevata: {torch.cuda.get_device_name(0)}")
    print(f"Numero di GPU disponibili: {torch.cuda.device_count()}")


# Moltiplicazione matrici grandi
size = 8000

x = torch.randn(size, size, device = device)
y = torch.randn(size, size, device = device)

start = time.time()
z = x @ y
torch.cuda.synchronize() if device == 'cuda' else None
end = time.time()

print(f"[Matrici] Moltiplicazione {size}x{size} completata in {end-start:.4f} secondi")

# Operazioni element-wise su tensori grandi
size_elem = 100_000_000
a = torch.randn(size_elem, device = device)
b = torch.randn(size_elem, device = device)

start = time.time()
c = a * b + a / (b + 1e-6)
torch.cuda.synchronize() if device == 'cuda' else None
end = time.time()

print(f"[Element-wise] Operazioni su {size_elem} elementi completate in {end-start:.4f} secondi")

# Convoluzione 2D (simula layer CNN)
batch_size, channels, H, W = 32, 128, 224, 224
x_conv = torch.randn(batch_size, channels, H, W, device = device)
conv = nn.Conv2d(channels, channels, kernel_size=3, padding=1).to(device)

start = time.time()
y_conv = conv(x_conv)
torch.cuda.synchronize() if device == 'cuda' else None
end = time.time()

print(f"[Convoluzione 2D] Batch {batch_size}x{channels}x{H}x{W} completato in {end-start:.4f} secondi")

print("\n Benchmark GPU completato!")