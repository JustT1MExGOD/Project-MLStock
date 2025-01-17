import kagglehub

# Download latest version
path = kagglehub.dataset_download("vorvit/news-lenta-20-23")

print("Path to dataset files:", path)