# Dead Air Analyzer

## Executive Summary

The **Dead Air Analyzer** is an advanced audio analysis tool designed to automatically detect and quantify periods of silence ("dead air") in call recordings. This solution addresses a critical quality assurance need in customer service, sales, and contact center operations where extended silences can indicate issues such as:

- Agent placing customers on hold without notification
- System delays or technical difficulties
- Lack of engagement during conversations
- Process inefficiencies requiring investigation

By automating the detection of dead air, organizations can improve customer experience, identify training opportunities, and optimize operational efficiency.

---

## Table of Contents

1. [Business Value](#business-value)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Technical Specifications](#technical-specifications)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Usage Guide](#usage-guide)
8. [Output Format](#output-format)
9. [Algorithm Details](#algorithm-details)
10. [Performance Considerations](#performance-considerations)
11. [Troubleshooting](#troubleshooting)
12. [Future Roadmap](#future-roadmap)

---

## Business Value

### Problem Statement

Contact centers and customer service operations generate thousands of call recordings daily. Manual review of these recordings to identify quality issues is:
- **Time-consuming**: Reviewing a 10-minute call takes 10 minutes
- **Inconsistent**: Human reviewers have varying thresholds for what constitutes problematic silence
- **Expensive**: Requires dedicated QA staff
- **Limited**: Only a small sample of calls can be reviewed

### Solution Benefits

| Benefit | Description |
|---------|-------------|
| **Automated Analysis** | Process hundreds of calls in minutes, not hours |
| **Consistent Standards** | Apply uniform detection criteria across all recordings |
| **Scalable Operations** | Analyze 100% of calls, not just samples |
| **Actionable Insights** | Export detailed reports for coaching and process improvement |
| **Cost Reduction** | Reduce manual QA effort by 80%+ |

### Use Cases

1. **Quality Assurance**: Automatically flag calls with excessive dead air for supervisor review
2. **Agent Performance**: Track individual agent metrics over time
3. **Process Improvement**: Identify systemic issues causing delays
4. **Compliance**: Ensure service level agreements (SLAs) are met
5. **Training**: Use flagged calls as coaching examples

---

## Key Features

### Core Capabilities

- **Adaptive Silence Detection**: Automatically adjusts to varying audio levels across different recordings
- **Configurable Thresholds**: Define what constitutes "dead air" for your organization
- **Batch Processing**: Analyze entire folders of recordings at once
- **Multiple Format Support**: WAV, MP3, FLAC, OGG, M4A, AAC
- **Detailed Reporting**: Console output and CSV export for further analysis
- **Segment Tracking**: Precise timestamps for each detected silence period

### Configuration Options

- Minimum silence duration threshold
- Ignore periods at call start (pre-call silence)
- Ignore periods at call end (post-call silence)
- Sensitivity adjustment via RMS percentile

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEAD AIR ANALYZER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │              │    │              │    │              │    │            │ │
│  │ Audio Files  │───▶│ Audio Loader │───▶│  Silence     │───▶│  Report    │ │
│  │ (Input)      │    │ (librosa)    │    │  Detector    │    │  Generator │ │
│  │              │    │              │    │              │    │            │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └────────────┘ │
│         │                   │                   │                   │       │
│         │                   │                   │                   │       │
│         ▼                   ▼                   ▼                   ▼       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Configuration Layer                            │  │
│  │                         (config.yaml)                                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │           OUTPUT LAYER              │
                    ├─────────────────────────────────────┤
                    │  • Console Report                   │
                    │  • CSV Export (Summary)             │
                    │  • CSV Export (Segment Details)     │
                    └─────────────────────────────────────┘
```

### Component Details

#### 1. Configuration Manager
- Loads settings from `config.yaml`
- Provides default fallbacks for missing values
- Supports command-line overrides

#### 2. Audio Loader
- Leverages `librosa` for robust audio file handling
- Supports multiple audio formats
- Handles various sample rates automatically

#### 3. Silence Detector
- Implements adaptive RMS-based detection
- Calculates dynamic thresholds per file
- Filters edge cases (start/end silence)

#### 4. Report Generator
- Formats results for console display
- Exports data to CSV for external analysis
- Provides summary statistics

### Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   config    │     │   Audio     │     │   RMS       │     │  Silence    │
│   .yaml     │────▶│   Loading   │────▶│  Analysis   │────▶│  Detection  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   │                   │
                           │                   │                   │
                           ▼                   ▼                   ▼
                    ┌─────────────────────────────────────────────────────┐
                    │              Per-File Results                       │
                    │  • File name & path                                 │
                    │  • Total duration                                   │
                    │  • Dead air count & duration                        │
                    │  • Segment timestamps                               │
                    │  • Processing times                                 │
                    └─────────────────────────────────────────────────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────────────────────────┐
                    │              Aggregated Output                      │
                    │  • Summary report (console)                         │
                    │  • Summary CSV                                      │
                    │  • Detailed segments CSV                            │
                    └─────────────────────────────────────────────────────┘
```

---

## Technical Specifications

### System Requirements

| Requirement | Specification |
|-------------|---------------|
| **Python Version** | 3.8 or higher |
| **Operating System** | Windows, macOS, Linux |
| **Memory** | Minimum 4GB RAM (8GB recommended for large files) |
| **Disk Space** | 100MB for installation + space for audio files |

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `librosa` | ≥0.10.0 | Audio loading and feature extraction |
| `numpy` | ≥1.20.0 | Numerical computations |
| `pandas` | ≥1.3.0 | Data manipulation and CSV export |
| `PyYAML` | ≥6.0 | Configuration file parsing |

### Supported Audio Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| WAV | `.wav` | Uncompressed, highest quality |
| MP3 | `.mp3` | Compressed, widely used |
| FLAC | `.flac` | Lossless compression |
| OGG | `.ogg` | Open format, compressed |
| M4A | `.m4a` | Apple format, compressed |
| AAC | `.aac` | Advanced Audio Coding |

---

## Installation

### Step 1: Prerequisites

Ensure Python 3.8+ is installed:

```bash
python --version
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install librosa numpy pandas pyyaml
```

Or create a `requirements.txt`:

```
librosa>=0.10.0
numpy>=1.20.0
pandas>=1.3.0
PyYAML>=6.0
```

Then install:

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python dead_air_analyzer_v2.py --help
```

---

## Configuration

### Configuration File: `config.yaml`

The analyzer uses a YAML configuration file for all settings. This allows you to:
- Set organization-specific thresholds
- Maintain consistent settings across runs
- Version control your configuration

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_silence_duration` | float | 5.0 | Minimum seconds of silence to count as dead air |
| `ignore_start_duration` | float | 2.0 | Seconds to ignore at the start of each call |
| `ignore_end_duration` | float | 2.0 | Seconds to ignore at the end of each call |
| `rms_percentile` | int | 15 | Percentile threshold for adaptive detection (10-25 recommended) |
| `default_input_folder` | string | "audio_files" | Default folder for audio files |
| `default_export_filename` | string | "dead_air_results.csv" | Default CSV export filename |
| `supported_formats` | list | [".wav", ".mp3", ...] | Audio formats to process |

### Example Configuration

```yaml
# Strict settings for high-quality requirements
min_silence_duration: 3.0      # Flag shorter silences
ignore_start_duration: 1.0      # Less tolerance for start delay
ignore_end_duration: 1.0        # Less tolerance for end delay
rms_percentile: 12              # More sensitive detection
```

```yaml
# Lenient settings for noisy environments
min_silence_duration: 10.0     # Only flag long silences
ignore_start_duration: 5.0      # More tolerance for connection delay
ignore_end_duration: 5.0        # More tolerance for disconnection
rms_percentile: 20              # Less sensitive detection
```

---

## Usage Guide

### Basic Usage

1. **Prepare Audio Files**: Place audio files in the `audio_files` folder (or configure a different folder)

2. **Run Analysis**:
   ```bash
   python dead_air_analyzer_v2.py
   ```

3. **Review Results**: Check console output and optional CSV exports

### Command Line Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--input` | `-i` | Input folder path | `-i recordings/` |
| `--duration` | `-d` | Override min silence duration | `-d 10` |
| `--export` | | Export to CSV file | `--export results.csv` |
| `--config` | | Custom config file | `--config strict.yaml` |

### Usage Examples

```bash
# Analyze files in default folder with default settings
python dead_air_analyzer_v2.py

# Analyze files in custom folder
python dead_air_analyzer_v2.py -i "C:\Recordings\January"

# Set minimum silence to 10 seconds
python dead_air_analyzer_v2.py -d 10

# Export results to CSV
python dead_air_analyzer_v2.py --export january_analysis.csv

# Use custom configuration file
python dead_air_analyzer_v2.py --config strict_config.yaml

# Combine multiple options
python dead_air_analyzer_v2.py -i recordings/ -d 8 --export report.csv
```

---

## Output Format

### Console Output

The analyzer provides real-time progress and a summary report:

```
🎙 Dead Air Analyzer
----------------------------------------
Configuration file: config.yaml
Input folder: audio_files
Min silence duration: 5.0s
Ignore start duration: 2.0s
Ignore end duration: 2.0s
RMS percentile: 15
Initializing...

Analyzing 3 audio file(s)...

[1/3] Processing: call_001.wav
  ✓ Duration: 245.5s | Dead Air: 32.5s (13.2%) | Segments: 3 | ⏱ Analysis: 0.456s
    - 45.2s to 52.7s (7.5s)
    - 120.3s to 132.8s (12.5s)
    - 189.0s to 201.5s (12.5s)

[2/3] Processing: call_002.mp3
  ✓ Duration: 180.0s | Dead Air: 0.0s (0.0%) | Segments: 0 | ⏱ Analysis: 0.312s

[3/3] Processing: call_003.wav
  ✓ Duration: 320.0s | Dead Air: 45.0s (14.1%) | Segments: 2 | ⏱ Analysis: 0.623s
    - 78.5s to 98.5s (20.0s)
    - 250.0s to 275.0s (25.0s)

==========================================================================================
DEAD AIR ANALYSIS REPORT
==========================================================================================

File Name                           Duration   Dead Air   %       Segs   Analysis Run Time
------------------------------------------------------------------------------------------
call_001.wav                        04:05      00:32      13.2    3      0.456s
call_002.mp3                        03:00      00:00      0.0     0      0.312s
call_003.wav                        05:20      00:45      14.1    2      0.623s
------------------------------------------------------------------------------------------
TOTAL/AVERAGE                       12:25      01:17      9.1     5      1.391s

==========================================================================================
```

### CSV Export Format

#### Summary File (`results.csv`)

| Column | Description |
|--------|-------------|
| File Name | Audio file name |
| Total Duration (s) | Call length in seconds |
| Dead Air Duration (s) | Total silence in seconds |
| Dead Air Percentage | Silence as % of call |
| Number of Segments | Count of silence periods |
| Load Time (s) | File loading time |
| Analysis Time (s) | Processing time |

#### Segments File (`results_segments.csv`)

| Column | Description |
|--------|-------------|
| File Name | Audio file name |
| Start Time (s) | Silence start timestamp |
| End Time (s) | Silence end timestamp |
| Duration (s) | Silence duration |

---

## Algorithm Details

### Adaptive RMS-Based Detection

The analyzer uses an adaptive approach to handle varying audio levels across different recordings:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DETECTION ALGORITHM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. LOAD AUDIO                                                   │
│     └── Load file with native sample rate                       │
│                                                                  │
│  2. CALCULATE RMS ENERGY                                         │
│     └── Compute RMS for each frame (2048 samples, 512 hop)      │
│                                                                  │
│  3. DETERMINE ADAPTIVE THRESHOLD                                 │
│     ├── Calculate percentile-based threshold                    │
│     ├── Calculate median-based threshold (10% of median)        │
│     ├── Take minimum of above                                   │
│     └── Apply floor (1% of max RMS)                            │
│                                                                  │
│  4. IDENTIFY SILENT FRAMES                                       │
│     └── Mark frames below threshold as silent                   │
│                                                                  │
│  5. FIND CONTIGUOUS REGIONS                                      │
│     └── Group consecutive silent frames                         │
│                                                                  │
│  6. FILTER BY DURATION                                           │
│     └── Keep only regions ≥ min_silence_duration                │
│                                                                  │
│  7. FILTER EDGE CASES                                            │
│     ├── Exclude silence at start (≤ ignore_start_duration)     │
│     └── Exclude silence at end (≥ audio_duration - ignore_end) │
│                                                                  │
│  8. RETURN RESULTS                                               │
│     └── Count, total duration, segment details                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Why Adaptive Detection?

Different recordings have different:
- Recording volumes
- Background noise levels
- Microphone sensitivities
- Compression artifacts

A fixed threshold would fail across diverse recordings. The adaptive approach:
1. Analyzes each file's unique audio characteristics
2. Sets a threshold relative to that file's energy distribution
3. Produces consistent detection regardless of absolute volume levels

### RMS Percentile Explanation

The `rms_percentile` parameter controls detection sensitivity:

| Percentile | Effect |
|------------|--------|
| 10 | Very sensitive - detects quieter sounds as silence |
| 15 | Balanced (default) |
| 20 | Less sensitive - only very quiet sounds are silence |
| 25 | Lenient - tolerates more background noise |

---

## Performance Considerations

### Processing Speed

| Factor | Impact | Recommendation |
|--------|--------|----------------|
| File Size | Linear relationship | Expect ~1 second per minute of audio |
| Format | Compressed formats need decoding | WAV is fastest, MP3 adds ~10% overhead |
| Sample Rate | Higher = more data | Native rate is used, no impact on results |

### Memory Usage

- Each file is loaded entirely into memory
- 1 minute of audio at 44.1kHz ≈ 10MB memory
- Process large files (>1 hour) individually if memory constrained

### Batch Processing Tips

1. **Group by Size**: Process similar-sized files together
2. **Monitor Memory**: Watch RAM usage for very large batches
3. **Use SSDs**: Faster disk I/O improves file loading

---

## Troubleshooting

### Common Issues

#### "No audio files found"

**Cause**: No supported audio files in the specified folder

**Solution**:
1. Check folder path is correct
2. Verify files have supported extensions
3. Ensure files are not hidden or in subfolders

#### "Could not load config file"

**Cause**: Invalid YAML syntax or missing file

**Solution**:
1. Validate YAML syntax (use online validator)
2. Check file permissions
3. Ensure file is in working directory

#### High false positive rate

**Cause**: Threshold too sensitive for noisy recordings

**Solution**:
1. Increase `rms_percentile` (try 18-22)
2. Increase `min_silence_duration`
3. Check for consistent background noise in recordings

#### Missing legitimate silences

**Cause**: Threshold not sensitive enough

**Solution**:
1. Decrease `rms_percentile` (try 10-12)
2. Review the audio files for actual silence levels

### Debug Information

The analyzer displays timing information for diagnosis:
- **Load Time**: Time to read and decode audio file
- **Analysis Time**: Time for silence detection only

Slow load times indicate I/O bottlenecks; slow analysis times may indicate CPU constraints.

---

## Future Roadmap

### Planned Enhancements

| Feature | Priority | Status |
|---------|----------|--------|
| Web-based dashboard | High | Planned |
| Real-time streaming analysis | High | Research |
| Speaker diarization integration | Medium | Planned |
| Parallel multi-file processing | Medium | Planned |
| Database storage for results | Medium | Planned |
| API endpoint for integration | Low | Backlog |
| Machine learning-based detection | Low | Research |

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-01 | Added YAML configuration, improved documentation |
| 1.0.0 | 2025-12 | Initial release with adaptive RMS detection |

---

## Support

For questions, issues, or feature requests, please contact the development team or submit an issue through the appropriate channels.

---

*© 2026 Dead Air Analyzer - Audio Quality Analysis Tool*

