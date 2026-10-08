import cv2

COLORS = {
    "match": (0, 200, 0),      # green
    "review": (0, 165, 255),   # orange
    "unknown": (0, 0, 255),    # red
}


def _label_for(face) -> str:
    if face.decision == "unknown":
        return f"#{face.index} {face.similarity:.2f}"
    return f"#{face.index} {face.best_identity} {face.similarity:.2f}"


def annotate_image(image_path, face_results):
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    height, width = image.shape[:2]
    font_scale = max(0.4, width / 2000)
    thickness = max(1, round(width / 800))

    for face in face_results:
        x, y, w, h = face.box
        color = COLORS.get(face.decision, (255, 255, 255))
        cv2.rectangle(image, (x, y), (x + w, y + h), color, thickness)

        label = _label_for(face)
        (text_w, text_h), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)

        label_top = y - text_h - baseline - 4
        if label_top < 0:
            label_top = y + 2
        cv2.rectangle(image,
                      (x, label_top),
                      (x + text_w + 4, label_top + text_h + baseline + 4),
                      color, -1)
        cv2.putText(image, label,
                    (x + 2, label_top + text_h + 2),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                    (255, 255, 255), thickness, cv2.LINE_AA)

    return image
