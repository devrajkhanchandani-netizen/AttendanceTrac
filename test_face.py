from deepface import DeepFace

image_path = "Celebrities/indv/SRK/images.jpeg"

result = DeepFace.represent(
    img_path=image_path,
    model_name="ArcFace",
    detector_backend="retinaface"
)

print("Face detected!")
print("Embedding length:", len(result[0]["embedding"]))
print("First 10 values:")
print(result[0]["embedding"][:10])