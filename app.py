import os
import subprocess
import cv2
from flask import Flask, render_template, request, jsonify, send_from_directory
from ultralytics import YOLO

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "static/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# تحميل نموذج YOLO
model = YOLO("best.pt")

# معرف الفئة للأخطاء فقط
FOUL_CLASS_ID = 1  

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_video():
    if "video" not in request.files:
        return jsonify({"error": "لم يتم تحميل ملف الفيديو!"}), 400

    video_file = request.files["video"]
    video_path = os.path.join(UPLOAD_FOLDER, "input.mp4")
    output_path = os.path.join(RESULT_FOLDER, "output.mp4")
    fixed_output_path = os.path.join(RESULT_FOLDER, "output_fixed.mp4")
    snapshot_path = os.path.join(RESULT_FOLDER, "foul_snapshot.jpg")
    full_frame_path = os.path.join(RESULT_FOLDER, "full_frame.jpg")
    result_text_path = os.path.join(RESULT_FOLDER, "results.txt")

    video_file.save(video_path)

    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))

    foul_detected = False
    foul_count = 0 

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        found_foul_in_frame = False  # Flag to track if a foul was found in the current frame
        for result in results:
            for box, class_id in zip(result.boxes.xyxy, result.boxes.cls):
                x1, y1, x2, y2 = map(int, box[:4])

                if int(class_id) == FOUL_CLASS_ID:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    if not found_foul_in_frame:
                        foul_count += 1
                        found_foul_in_frame = True

                        if not foul_detected:
                            cv2.imwrite(snapshot_path, frame[y1:y2, x1:x2])  # حفظ الخطأ المقصوص
                            cv2.imwrite(full_frame_path, frame)  # حفظ الإطار الكامل
                            foul_detected = True

        out.write(frame)

    cap.release()
    out.release()

    if foul_count == 0:
        decision_text = "مافي خطا"
    elif 1 <= foul_count <= 3:
        decision_text = "خطا"
    elif 4 <= foul_count <= 6:
        decision_text = "خطا + كرت اصفر"
    elif foul_count >= 7:
        decision_text = "خطا + كرت احمر"
    else:
        decision_text = "لم يتم تحديد أي خطأ" # إضافة حالة افتراضية

    with open(result_text_path, "w", encoding="utf-8") as f:
        f.write(decision_text)

    try:
        subprocess.run(
            ["ffmpeg", "-i", output_path, "-c:v", "libx264", "-preset", "slow", "-crf", "23",
             "-c:a", "aac", "-b:a", "128k", fixed_output_path, "-y"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"حدث خطأ أثناء تحويل الفيديو: {e}"}), 500

    return jsonify({
        "videoPath": f"/results/output_fixed.mp4?t={os.path.getmtime(fixed_output_path)}",
        "decision": decision_text,
        "snapshot": f"/results/foul_snapshot.jpg?t={os.path.getmtime(snapshot_path)}" if foul_detected else None,
        "fullFrame": f"/results/full_frame.jpg?t={os.path.getmtime(full_frame_path)}" if foul_detected else None
    })

@app.route("/results/<path:filename>")
def get_video(filename):
    return send_from_directory(RESULT_FOLDER, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)