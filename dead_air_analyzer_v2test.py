

"""
Dead Air Analyzer - Detects silence/dead air in call recordings.

Uses adaptive RMS-based detection that adjusts to each audio's characteristics.

Usage:
    python dead_air_analyzer_v2.py [options]

Place your audio files in the 'audio_files' folder before running.
Configuration can be modified via config.yaml file.
"""

import argparse
import time
from pathlib import Path
from typing import Dict, List, Tuple

import librosa
import numpy as np
import pandas as pd
import yaml

# ============================================================================
# Configuration Management
# ============================================================================
DEFAULT_CONFIG = {
    "min_silence_duration": 5.0,
    "ignore_start_duration": 2.0,
    "ignore_end_duration": 2.0,
    "rms_percentile": 15,
    "default_input_folder": "audio_files",
    "default_export_filename": "dead_air_results.csv",
    "supported_formats": [".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"],
}


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Load configuration from YAML file with fallback to defaults.

    Args:
        config_path: Path to the configuration YAML file

    Returns:
        dict: Configuration dictionary with all settings
    """
    config = DEFAULT_CONFIG.copy()

    config_file = Path(config_path)
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    config.update(user_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            print("Using default configuration.")

    return config


def warmup_librosa():
    """Pre-initialize librosa to avoid first-file timing overhead."""
    # Create a tiny dummy signal to trigger librosa's lazy initialization
    dummy = np.zeros(1024, dtype=np.float32)
    librosa.feature.rms(y=dummy, frame_length=512, hop_length=256)


class DeadAirAnalyzer:
    """Dead air analyzer using adaptive RMS-based detection."""

    def __init__(self, config: dict = None):
        """
        Initialize the Dead Air Analyzer.

        Args:
            config: Configuration dictionary with all settings.
                   If None, default configuration will be used.
        """
        if config is None:
            config = DEFAULT_CONFIG

        self.config = config
        self.min_silence_duration = config.get(
            "min_silence_duration", DEFAULT_CONFIG["min_silence_duration"]
        )
        self.ignore_start_duration = config.get(
            "ignore_start_duration", DEFAULT_CONFIG["ignore_start_duration"]
        )
        self.ignore_end_duration = config.get(
            "ignore_end_duration", DEFAULT_CONFIG["ignore_end_duration"]
        )
        self.rms_percentile = config.get(
            "rms_percentile", DEFAULT_CONFIG["rms_percentile"]
        )

        # Set supported formats from config
        formats = config.get("supported_formats", DEFAULT_CONFIG["supported_formats"])
        self.SUPPORTED_FORMATS = set(formats)

    def detect_silence(
        self,
        y: np.ndarray,
        sr: int,
        min_silence_duration: float,
        frame_length: int = 2048,
        hop_length: int = 512,
    ) -> Tuple[int, float, List[Dict]]:
        """
        Detect silence using adaptive RMS-based thresholding.

        This method calculates a threshold based on the audio's own RMS distribution,
        making it robust across different audio files with varying levels.

        Args:
            y: Audio time series
            sr: Sample rate
            min_silence_duration: Minimum silence duration in seconds
            frame_length: Frame length for RMS calculation
            hop_length: Hop length for RMS calculation

        Returns:
            Tuple of (num_silences, total_duration, silence_segments)
        """
        # Calculate RMS energy per frame
        rms = librosa.feature.rms(
            y=y, frame_length=frame_length, hop_length=hop_length
        )[0]

        # Calculate adaptive threshold based on percentile
        rms_threshold = np.percentile(rms, self.rms_percentile)

        # Also consider values significantly below median as silence
        median_rms = np.median(rms)
        adaptive_threshold = min(rms_threshold, median_rms * 0.1)

        # Ensure minimum threshold to avoid false positives in very quiet recordings
        min_threshold = np.max(rms) * 0.01
        threshold = max(adaptive_threshold, min_threshold)

        # Convert to frame indices
        min_silence_frames = int(min_silence_duration * sr / hop_length)

        # Find silent frames
        is_silent = rms < threshold

        # Find contiguous silent regions
        silence_segments = []
        num_silences = 0
        total_duration = 0.0

        in_silence = False
        silence_start = 0

        for i, silent in enumerate(is_silent):
            if silent and not in_silence:
                in_silence = True
                silence_start = i
            elif not silent and in_silence:
                in_silence = False
                silence_length = i - silence_start

                if silence_length >= min_silence_frames:
                    start_time = librosa.frames_to_time(
                        silence_start, sr=sr, hop_length=hop_length
                    )
                    duration = librosa.frames_to_time(
                        silence_length, sr=sr, hop_length=hop_length
                    )

                    # Filter out silences at the start of the audio
                    if start_time >= self.ignore_start_duration:
                        silence_segments.append(
                            {
                                "start_time": round(start_time, 2),
                                "end_time": round(start_time + duration, 2),
                                "duration": round(duration, 2),
                            }
                        )
                        num_silences += 1
                        total_duration += duration

        # Check for trailing silence (but not at the very end)
        if in_silence:
            silence_length = len(is_silent) - silence_start
            if silence_length >= min_silence_frames:
                start_time = librosa.frames_to_time(
                    silence_start, sr=sr, hop_length=hop_length
                )
                duration = librosa.frames_to_time(
                    silence_length, sr=sr, hop_length=hop_length
                )
                audio_duration = librosa.get_duration(y=y, sr=sr)

                # Only count if not at the very end of audio
                if start_time < audio_duration - self.ignore_end_duration:
                    silence_segments.append(
                        {
                            "start_time": round(start_time, 2),
                            "end_time": round(start_time + duration, 2),
                            "duration": round(duration, 2),
                        }
                    )
                    num_silences += 1
                    total_duration += duration

        return num_silences, total_duration, silence_segments

    def analyze_file(self, audio_file_path: str) -> dict:
        """
        Analyze a single audio file for dead air.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            dict: Analysis results with separate load_time and analysis_time
        """
        #audio_file_path = r"C:\Users\dwivedi mulk raj\OneDrive - The Boston Consulting Group, Inc\Documents\demo call"
        file_path = Path(audio_file_path)

        if not file_path.exists():
            return {"error": f"File not found: {audio_file_path}", "status": "error"}

        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return {
                "error": f"Unsupported format: {file_path.suffix}",
                "status": "error",
            }

        try:
            # Time file loading separately
            load_start = time.time()
            y, sr = librosa.load(audio_file_path, sr=None)
            load_time = time.time() - load_start

            duration = librosa.get_duration(y=y, sr=sr)

            # Time only the analysis
            analysis_start = time.time()
            num_silences, total_silence, segments = self.detect_silence(
                y, sr, self.min_silence_duration
            )
            analysis_time = time.time() - analysis_start

            # Calculate percentage of dead air
            dead_air_percentage = (
                (total_silence / duration * 100) if duration > 0 else 0
            )

            return {
                "file_name": file_path.name,
                "file_path": str(file_path.absolute()),
                "total_duration_seconds": round(duration, 2),
                "num_dead_air_segments": num_silences,
                "total_dead_air_seconds": round(total_silence, 2),
                "dead_air_percentage": round(dead_air_percentage, 2),
                "silence_segments": segments,
                "load_time_seconds": round(load_time, 3),
                "analysis_time_seconds": round(analysis_time, 3),
                "status": "success",
            }
        except Exception as e:
            return {"file_name": file_path.name, "error": str(e), "status": "error"}

    def analyze_folder(self, folder_path: str) -> list:
        """
        Analyze all audio files in a folder.

        Args:
            folder_path: Path to folder containing audio files

        Returns:
            list: List of analysis results for each file
        """
        folder = Path(folder_path)

        if not folder.exists():
            print(f"Error: Folder '{folder_path}' not found.")
            return []

        audio_files = [
            f
            for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_FORMATS
        ]

        if not audio_files:
            print(f"No audio files found in '{folder_path}'.")
            print(f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}")
            return []

        results = []
        print(f"\nAnalyzing {len(audio_files)} audio file(s)...\n")

        total_load_time = 0.0
        total_analysis_time = 0.0

        for i, audio_file in enumerate(audio_files, 1):
            print(f"[{i}/{len(audio_files)}] Processing: {audio_file.name}")

            result = self.analyze_file(str(audio_file))
            results.append(result)

            if result.get("status") == "success":
                load_t = result.get("load_time_seconds", 0)
                analysis_t = result.get("analysis_time_seconds", 0)
                total_load_time += load_t
                total_analysis_time += analysis_t

                print(
                    f"  ✓ Duration: {result['total_duration_seconds']}s | "
                    f"Dead Air: {result['total_dead_air_seconds']}s ({result['dead_air_percentage']}%) | "
                    f"Segments: {result['num_dead_air_segments']} | "
                    f"⏱ Analysis: {analysis_t:.3f}s"
                )
                if result["silence_segments"]:
                    for seg in result["silence_segments"][:3]:
                        print(
                            f"    - {seg['start_time']}s to {seg['end_time']}s ({seg['duration']}s)"
                        )
                    if len(result["silence_segments"]) > 3:
                        print(
                            f"    ... and {len(result['silence_segments']) - 3} more segments"
                        )
            else:
                print(f"  ✗ Error: {result.get('error', 'Unknown error')}")

        print(
            f"\n📊 Total load time: {total_load_time:.2f}s | Total analysis time: {total_analysis_time:.2f}s"
        )

        return results


def format_time(seconds: float) -> str:
    """Format seconds into MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def print_detailed_report(results: list):
    """Print a detailed report of the analysis results."""
    print("\n" + "=" * 90)
    print("DEAD AIR ANALYSIS REPORT")
    print("=" * 90)

    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "error"]

    if successful:
        print(
            f"\n{'File Name':<35} {'Duration':<10} {'Dead Air':<10} {'%':<7} {'Segs':<6} {'Analysis Run Time'}"
        )
        print("-" * 90)

        for result in successful:
            analysis_t = result.get("analysis_time_seconds", 0)
            print(
                f"{result['file_name'][:33]:<35} "
                f"{format_time(result['total_duration_seconds']):<10} "
                f"{format_time(result['total_dead_air_seconds']):<10} "
                f"{result['dead_air_percentage']:<7.1f} "
                f"{result['num_dead_air_segments']:<6} "
                f"{analysis_t:.3f}s"
            )

        # Summary statistics
        total_duration = sum(r["total_duration_seconds"] for r in successful)
        total_dead_air = sum(r["total_dead_air_seconds"] for r in successful)
        avg_percentage = sum(r["dead_air_percentage"] for r in successful) / len(
            successful
        )
        total_segments = sum(r["num_dead_air_segments"] for r in successful)
        total_analysis_time = sum(r.get("analysis_time_seconds", 0) for r in successful)

        print("-" * 90)
        print(
            f"{'TOTAL/AVERAGE':<35} "
            f"{format_time(total_duration):<10} "
            f"{format_time(total_dead_air):<10} "
            f"{avg_percentage:<7.1f} "
            f"{total_segments:<6} "
            f"{total_analysis_time:.3f}s"
        )

    if failed:
        print(f"\n⚠ {len(failed)} file(s) failed to process:")
        for result in failed:
            print(
                f"  - {result.get('file_name', 'Unknown')}: {result.get('error', 'Unknown error')}"
            )

    print("\n" + "=" * 90)


def export_to_csv(results: list, output_path: str):
    """Export results to a CSV file."""
    successful = [r for r in results if r.get("status") == "success"]

    if not successful:
        print("No successful results to export.")
        return

    # Main results
    df = pd.DataFrame(
        [
            {
                "File Name": r["file_name"],
                "Total Duration (s)": r["total_duration_seconds"],
                "Dead Air Duration (s)": r["total_dead_air_seconds"],
                "Dead Air Percentage": r["dead_air_percentage"],
                "Number of Segments": r["num_dead_air_segments"],
                "Load Time (s)": r.get("load_time_seconds", 0),
                "Analysis Time (s)": r.get("analysis_time_seconds", 0),
            }
            for r in successful
        ]
    )

    df.to_csv(output_path, index=False)
    print(f"\nResults exported to: {output_path}")

    # Export detailed segments
    segments_data = []
    for r in successful:
        for seg in r.get("silence_segments", []):
            segments_data.append(
                {
                    "File Name": r["file_name"],
                    "Start Time (s)": seg["start_time"],
                    "End Time (s)": seg["end_time"],
                    "Duration (s)": seg["duration"],
                }
            )

    if segments_data:
        segments_path = output_path.replace(".csv", "_segments.csv")
        pd.DataFrame(segments_data).to_csv(segments_path, index=False)
        print(f"Segment details exported to: {segments_path}")


def main():
    """Main entry point for the dead air analyzer."""
    # Load configuration from file
    config = load_config()

    parser = argparse.ArgumentParser(
        description="Analyze call recordings for dead air (silence) detection.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dead_air_analyzer_v2.py                    # Analyze all files in audio_files/
  python dead_air_analyzer_v2.py -i my_recordings/  # Analyze files in custom folder
  python dead_air_analyzer_v2.py -d 15              # Set minimum silence to 15 seconds
  python dead_air_analyzer_v2.py --export results.csv  # Export results to CSV
  python dead_air_analyzer_v2.py --config custom.yaml  # Use custom config file
        """,
    )

    parser.add_argument(
        "-i",
        "--input",
        default=None,
        help=f"Input folder containing audio files (default: {config['default_input_folder']})",
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=None,
        help=f"Minimum silence duration in seconds (default: {config['min_silence_duration']})",
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export results to CSV file",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration YAML file (default: config.yaml)",
    )

    #args = parser.parse_args()
    args, unknown = parser.parse_known_args()

    # Reload config if custom config path provided
    if args.config != "config.yaml":
        config = load_config(args.config)

    # Override config with command line arguments if provided
    if args.duration is not None:
        config["min_silence_duration"] = args.duration

    input_folder = args.input if args.input else config["default_input_folder"]

    print("\n🎙 Dead Air Analyzer")
    print("-" * 40)
    print(f"Configuration file: {args.config}")
    print(f"Input folder: {input_folder}")
    print(f"Min silence duration: {config['min_silence_duration']}s")
    print(f"Ignore start duration: {config['ignore_start_duration']}s")
    print(f"Ignore end duration: {config['ignore_end_duration']}s")
    print(f"RMS percentile: {config['rms_percentile']}")

    # Pre-warm librosa to avoid first-file initialization overhead
    print("Initializing...")
    warmup_librosa()

    # Create analyzer instance with config
    analyzer = DeadAirAnalyzer(config=config)

    # Analyze audio files
    results = analyzer.analyze_folder(input_folder)

    if results:
        # Print detailed report
        print_detailed_report(results)

        # Export to CSV if requested
        if args.export:
            export_to_csv(results, args.export)


if __name__ == "__main__":
    main()
