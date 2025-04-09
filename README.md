# ai-referee
# AI Referee: Football Foul Detection Using AI

AI Referee is a project that uses Artificial Intelligence (AI) to analyze football match videos and automatically detect fouls during the game. This project leverages the YOLO (You Only Look Once) model for object detection, combined with Flask as the web framework, to create an intelligent refereeing system.

## How the Project Works

### 1. **Upload Video**
   - Users can upload football match videos through a simple web interface.
   - The video file is processed on the server for foul detection.

### 2. **Using YOLO for Object Detection**
   - The project utilizes the **YOLOv8** pre-trained model (`best.pt`) for detecting fouls. YOLO is highly efficient at detecting objects in real-time, including the ball and players, and identifying when a foul occurs.
   - The system specifically tracks and marks **fouls** based on the predefined `FOUL_CLASS_ID`.

### 3. **Foul Detection Logic**
   - As the video is analyzed, the program checks each frame for possible fouls. When a foul is detected:
     - The system draws a red rectangle around the player involved in the foul.
     - It keeps track of the number of fouls detected, and based on this count, it categorizes the severity of the foul.
     - **Decision Categories**:
       - "No foul"
       - "Foul"
       - "Foul + Yellow Card"
       - "Foul + Red Card"
     - Additionally, a snapshot of the foul and a full-frame image of the video are saved for further inspection.

### 4. **Processing the Video**
   - The video is processed frame by frame.
   - For each frame, the YOLO model is applied to detect objects and fouls.
   - The frames are written into a new video file (`output.mp4`) and converted using **FFmpeg** for optimal output.
   
### 5. **User Interface (UI)**
   - A web-based interface is built using **Flask** that allows the user to upload a video, start the analysis, and view the results.
   - After processing, the user can download the analyzed video with color-coded markers indicating fouls, a snapshot of the foul, and the full frame.
   
### 6. **Color-Coding of Fouls**
   - Legal actions and tackles are not marked.
   - Illegal tackles are highlighted with **red boxes** to indicate fouls.

### 7. **Results and Reports**
   - Once the video is processed, the system provides:
     - The processed video with visual highlights (red boxes for fouls).
     - A **text report** detailing the number of fouls and the severity (e.g., Foul, Yellow Card, Red Card).
     - A **snapshot** of the first foul and the **full frame** for context.

### 8. **Real-Time Feedback**
   - The system allows for real-time analysis with minimal delay, making it suitable for live games and match reviews.

## Installation

To run the project locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/faisal-525/ai-referee.git

