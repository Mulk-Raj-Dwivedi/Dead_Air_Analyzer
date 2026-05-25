🎙 Dead Air Analyzer

A Streamlit-based audio analytics application that automatically detects and quantifies dead air/silence segments in customer interaction recordings using adaptive RMS-based audio signal processing.

This project helps organizations analyze customer support, RM (Relationship Manager), and call-center conversations to identify excessive silence, operational inefficiencies, and customer experience issues.


📌 Project Overview

Customer interaction recordings often contain:

Long hold periods

Delayed agent responses

System-related silence

Lack of engagement during conversations

Manually reviewing thousands of calls is:

Time-consuming

Expensive

Inconsistent


The Dead Air Analyzer automates this process by:

Uploading audio recordings

Detecting silence segments

Calculating dead air percentage

Generating downloadable reports

Visualizing silence analytics in an interactive dashboard


🚀 Key Features

✅ Multi-File Audio Upload

Upload and analyze multiple customer interaction recordings simultaneously.

✅ Adaptive RMS-Based Silence Detection

Uses dynamic RMS thresholding for robust silence detection across varying audio levels.

✅ Interactive Streamlit Dashboard

Browser-based UI with:

metrics

tables

charts

audio playback


✅ Dead Air Analytics

For each audio file:

Total Duration

Dead Air Duration

Dead Air Percentage

Number of Silence Segments

✅ Silence Segment Tracking


Detects:

silence start time

silence end time

silence duration

✅ CSV Report Downloads

Generate:

Overall Summary Report

Segment-Level Detailed Report

✅ Configurable Detection Parameters


Modify:

silence duration threshold

RMS sensitivity

ignore start/end duration

through:

YAML config

Streamlit sidebar controls

🏗 System Architecture   

					 ┌────────────────────────────┐
                     │     Audio Recordings       │
                     │ (mp3/wav/flac/m4a/etc.)   │
                     └─────────────┬──────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │     Streamlit Frontend     │
                    │       (app.py)             │
                    └─────────────┬──────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │   DeadAirAnalyzer Engine   │
                    │ (dead_air_analyzer.py)     │
                    └─────────────┬──────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │     Librosa Processing     │
                    │   RMS Feature Extraction   │
                    └─────────────┬──────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │    Silence Detection       │
                    │   Adaptive Thresholding    │
                    └─────────────┬──────────────┘
                                   │
            ┌──────────────────────┴──────────────────────┐
            ▼                                             ▼

┌────────────────────────┐              				┌────────────────────────┐
│  Summary Report CSV    | 								|	Segment-Level Report |
│              			 │                              |   					 |
│  Overall Dead Air %    │             					│   Silence Timestamps   │
└────────────────────────┘         						└────────────────────────┘


⚙️ Technical Stack

Technology	Purpose

Python		Backend processing

Streamlit	Frontend dashboard

Pandas		Data processing

Librosa		Audio analysis

NumPy		Numerical computations

Matplotlib	Visualization

YAML		Configuration management

Git/GitHub	Version control

📂 Project Structure

Dead_Air_Analyzer/
│
├── app.py
├── dead_air_analyzer_v2test.py
├── config.yaml
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── temp_audio/
├── outputs/
└── sample_audio/


🔄 Project Workflow

User Uploads Audio Files
            ↓
Files Stored Temporarily
            ↓
Audio Loaded using Librosa
            ↓
RMS Energy Calculated
            ↓
Adaptive Silence Threshold Generated
            ↓
Silent Frames Detected
            ↓
Contiguous Silence Segments Identified
            ↓
Dead Air Metrics Computed
            ↓
Dashboard Visualization
            ↓
CSV Report Generation

🧠 Core Detection Logic

The project uses:

RMS (Root Mean Square) Energy Analysis

The RMS value measures audio loudness.

RMS=√(1/N∗Σ(x2))

Where:

Higher RMS → speech/audio

Lower RMS → silence/dead air

📊 Silence Detection Process

Step 1 — Audio Loading

Audio files are loaded using:

librosa

Supported formats:

WAV, 
MP3, 
FLAC, 
OGG, 
AAC, 
M4A

Step 2 — RMS Feature Extraction

The audio waveform is divided into frames.

RMS energy is calculated for each frame.

Step 3 — Adaptive Thresholding

Dynamic threshold generated using:

RMS percentile

Median RMS energy

This makes the analyzer robust to:

noisy recordings

low-volume calls

microphone differences

Step 4 — Silence Segmentation

Frames below threshold are marked silent.

Continuous silent frames are grouped into:

silence segments

Step 5 — Filtering

Silence is filtered using:

minimum silence duration

ignore start duration

ignore end duration

📈 Dashboard Features

Metrics Dashboard

Displays:

Total Duration

Dead Air Duration

Dead Air Percentage

Silence Segment Count

Audio Playback

Play uploaded recordings directly in browser.

Silence Segment Table

Displays:

Start Time

End Time

Duration

Visualization

Bar chart comparison of silence durations.

Comparative Analytics

Compare dead air percentages across multiple files.

📤 Output Reports

1. Summary Report

Example:

File Name	Duration	Dead Air %

call_1.mp3	240 sec		18%

call_2.mp3	320 sec		9%

2. Segment Report

Example:

Start Time	End Time	Duration

45 sec		58 sec		13 sec

⚙️ Configuration Parameters

Defined in:

config.yaml

Parameter	Description

min_silence_duration	Minimum silence to detect

rms_percentile	Detection sensitivity

ignore_start_duration	Ignore initial silence

ignore_end_duration	Ignore ending silence

📦 Installation

Clone Repository

git clone https://github.com/YOUR_USERNAME/Dead_Air_Analyzer.git

Install Dependencies

pip install -r requirements.txt

▶️ Run Application

streamlit run app.py

Application opens at:

http://localhost:8501

☁️ Deployment

The application can be deployed using:

Streamlit Community Cloud

Docker

AWS

Azure

GCP

📋 requirements.txt

streamlit

pandas

numpy

librosa

soundfile

pyyaml

matplotlib

plotly

🎯 Business Use Cases

Contact Center QA

Identify excessive customer hold times.

RM/Customer Interaction Analytics

Analyze silence patterns during customer conversations.

Agent Performance Monitoring

Compare dead air percentages across agents.

Operational Efficiency

Detect workflow/process bottlenecks.

Customer Experience Analytics

Reduce disengagement during interactions.

🔮 Future Enhancements

Real-time audio streaming

Speaker diarization

Emotion detection

ML-based call quality scoring

Waveform silence highlighting

Database integration

Cloud deployment pipeline

LLM-based call summarization

📸 Sample Dashboard

(Add screenshots here)

![Dashboard](screenshots/dashboard.png)

👨‍💻 Author

Mulk Raj Dwivedi

Data Science

Machine Learning

Audio Analytics

AI/ML Engineering

Streamlit Deployment

📄 License

MIT License

⭐ Project Highlights

This project demonstrates:

End-to-end ML application thinking

Audio signal processing

Interactive dashboard development

Config-driven architecture
Reporting & analytics
Real-world QA automation use case
