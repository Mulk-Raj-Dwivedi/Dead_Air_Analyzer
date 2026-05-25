# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

from dead_air_analyzer_v2test import DeadAirAnalyzer, load_config

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Dead Air Analyzer",
    page_icon="🎙",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================
st.title("🎙 Dead Air Analyzer Dashboard")

st.markdown("""
Upload one or multiple audio files and analyze dead air/silence segments.
""")

# =========================================================
# SIDEBAR SETTINGS
# =========================================================
st.sidebar.header("⚙ Settings")

min_silence = st.sidebar.slider(
    "Minimum Silence Duration (sec)",
    1,
    20,
    5
)

rms_percentile = st.sidebar.slider(
    "RMS Percentile",
    1,
    50,
    15
)

# =========================================================
# MULTIPLE FILE UPLOAD
# =========================================================
uploaded_files = st.file_uploader(
    "Upload Audio Files",
    type=["mp3", "wav", "flac", "ogg", "m4a", "aac"],
    accept_multiple_files=True
)

# =========================================================
# PROCESS FILES
# =========================================================
if uploaded_files:

    os.makedirs("temp_audio", exist_ok=True)

    # -----------------------------
    # Load Config
    # -----------------------------
    config = load_config()

    config["min_silence_duration"] = min_silence
    config["rms_percentile"] = rms_percentile

    analyzer = DeadAirAnalyzer(config=config)

    # =====================================================
    # MASTER SUMMARY STORAGE
    # =====================================================
    all_summary_results = []

    st.header("📊 Analysis Results")

    # =====================================================
    # LOOP THROUGH FILES
    # =====================================================
    for uploaded_file in uploaded_files:

        st.divider()

        st.subheader(f"🎧 {uploaded_file.name}")

        # Save uploaded file
        file_path = os.path.join(
            "temp_audio",
            uploaded_file.name
        )

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Audio player
        st.audio(uploaded_file)

        # Analyze
        with st.spinner(f"Analyzing {uploaded_file.name}..."):

            result = analyzer.analyze_file(file_path)

        # =================================================
        # SUCCESS
        # =================================================
        if result["status"] == "success":

            # ---------------------------------------------
            # METRICS
            # ---------------------------------------------
            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Duration",
                f"{result['total_duration_seconds']} sec"
            )

            col2.metric(
                "Dead Air",
                f"{result['total_dead_air_seconds']} sec"
            )

            col3.metric(
                "Dead Air %",
                f"{result['dead_air_percentage']}%"
            )

            col4.metric(
                "Segments",
                result["num_dead_air_segments"]
            )

            # ---------------------------------------------
            # STORE SUMMARY
            # ---------------------------------------------
            summary_row = {
                "File Name": result["file_name"],
                "Total Duration (s)": result["total_duration_seconds"],
                "Dead Air Duration (s)": result["total_dead_air_seconds"],
                "Dead Air Percentage": result["dead_air_percentage"],
                "Number of Segments": result["num_dead_air_segments"],
                "Analysis Time (s)": result["analysis_time_seconds"]
            }

            all_summary_results.append(summary_row)

            # =================================================
            # SEGMENT REPORT
            # =================================================
            st.subheader("🔇 Silence Segments")

            if result["silence_segments"]:

                segment_df = pd.DataFrame(
                    result["silence_segments"]
                )

                st.dataframe(segment_df)

                # ---------------------------------------------
                # CHART
                # ---------------------------------------------
                st.subheader("📈 Silence Duration Chart")

                fig, ax = plt.subplots(figsize=(10, 4))

                ax.bar(
                    range(len(segment_df)),
                    segment_df["duration"]
                )

                ax.set_xlabel("Segment Number")
                ax.set_ylabel("Duration (sec)")
                ax.set_title(
                    f"Dead Air Segment Durations - {uploaded_file.name}"
                )

                st.pyplot(fig)

                # ---------------------------------------------
                # DOWNLOAD SEGMENT REPORT
                # ---------------------------------------------
                segment_csv = segment_df.to_csv(index=False)

                st.download_button(
                    label=f"⬇ Download Segment Report - {uploaded_file.name}",
                    data=segment_csv,
                    file_name=f"{uploaded_file.name}_segments.csv",
                    mime="text/csv"
                )

            else:
                st.info("No dead air detected.")

        # =================================================
        # ERROR
        # =================================================
        else:
            st.error(result["error"])

    # =====================================================
    # MASTER SUMMARY REPORT
    # =====================================================
    if all_summary_results:

        st.divider()

        st.header("📋 Overall Summary Report")

        master_summary_df = pd.DataFrame(
            all_summary_results
        )

        st.dataframe(master_summary_df)

        # =================================================
        # MASTER CHART
        # =================================================
        st.subheader("📊 Dead Air Percentage Comparison")

        fig2, ax2 = plt.subplots(figsize=(12, 5))

        ax2.bar(
            master_summary_df["File Name"],
            master_summary_df["Dead Air Percentage"]
        )

        ax2.set_xlabel("Audio Files")
        ax2.set_ylabel("Dead Air %")
        ax2.set_title("Dead Air Percentage Across Audio Files")

        plt.xticks(rotation=45)

        st.pyplot(fig2)

        # =================================================
        # DOWNLOAD MASTER SUMMARY
        # =================================================
        master_csv = master_summary_df.to_csv(index=False)

        st.download_button(
            label="⬇ Download Overall Summary Report",
            data=master_csv,
            file_name="overall_results.csv",
            mime="text/csv"
        )