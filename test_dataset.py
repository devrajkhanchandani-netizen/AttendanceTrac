from pathlib import Path

BASE_DIR = Path(__file__).parent
INDV_DIR = BASE_DIR / "Celebrities" / "indv"

print("Looking inside:", INDV_DIR)

for actor_folder in INDV_DIR.iterdir():

    if actor_folder.is_dir():

        actor_name = actor_folder.name

        photos = [
            file for file in actor_folder.iterdir()
            if file.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
        ]

        print(f"\n{actor_name}")
        print(f"Photos: {len(photos)}")

        for photo in photos:
            print("   ", photo.name)