import os
import datetime
from collections import defaultdict
import matplotlib
# Use 'Agg' backend for non-interactive plotting (for saving to file)
# This prevents charts from trying to open a GUI window, which is not needed when embedding in HTML.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from playsound import playsound
import tkinter as tk
from tkinter import messagebox
import random
import time
import base64 # Import for base64 encoding images
import matplotlib.font_manager as fm # Import for font management

# === CONFIG ===
# Ensure these paths are valid for your system.
# For security and portability, consider using relative paths or user's home directory.
# IMPORTANT: Update these paths to your actual desired locations.
SOUND_FILE = "/Users/snehacherukuri/Downloads/Mario Coin Sound/mario_coin_sound.mp3" # Path to your Mario Coin Sound MP3

# Define the directory where log files will be stored
LOG_FILES_DIR = "/Users/snehacherukuri/Downloads/Mario Coin Sound/"
RAW_LOG_FILE = os.path.join(LOG_FILES_DIR, "productivity_raw.csv") # New file for raw data
DISPLAY_LOG_FILE = os.path.join(LOG_FILES_DIR, "productivity_log.html") # File for formatted display

# This directory will hold the generated chart images
CHART_SAVE_DIR = "/Users/snehacherukuri/Library/CloudStorage/GoogleDrive-snehacherukuri07@gmail.com/My Drive/Python Daily tracker/"

# --- Initial Directory Setup ---
# Ensure the log files directory exists
try:
    os.makedirs(LOG_FILES_DIR, exist_ok=True)
    print(f"Log files directory ensured: {LOG_FILES_DIR}")
except OSError as e:
    error_msg = f"CRITICAL ERROR: Could not create log files directory:\n{LOG_FILES_DIR}\nError: {e}\nPlease check permissions for the 'Downloads' folder."
    messagebox.showerror("Directory Creation Error", error_msg)
    print(error_msg)
    # Exit or disable functionality if essential directories cannot be created
    exit()

# Ensure the chart save directory exists
try:
    os.makedirs(CHART_SAVE_DIR, exist_ok=True)
    print(f"Chart save directory ensured: {CHART_SAVE_DIR}")
except OSError as e:
    error_msg = f"CRITICAL ERROR: Could not create chart save directory:\n{CHART_SAVE_DIR}\nError: {e}\nPlease check permissions for your Google Drive folder."
    messagebox.showerror("Directory Creation Error", error_msg)
    print(error_msg)
    exit()


# Configure Matplotlib to use a font that supports emojis
plt.rcParams['font.sans-serif'] = ['Inter', 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False # Allows minus sign to be displayed correctly with emoji fonts

POINTS_BY_LEVEL = {
    "easy": {"points": 1, "emoji": "🌱", "sound_plays": 1},
    "medium": {"points": 3, "emoji": "⚡", "sound_plays": 2},
    "hard": {"points": 5, "emoji": "🔥", "sound_plays": 3},
}

MOTIVATIONAL_QUOTES = [
    "The best way to predict the future is to create it. – Peter Drucker",
    "Believe you can and you're halfway there. – Theodore Roosevelt",
    "The only way to do great work is to love what you do. – Steve Jobs",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston S. Churchill",
    "Your limitation—it's only your imagination.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Success doesn't just find you. You have to go out and get it.",
    "The harder you work for something, the greater you'll feel when you achieve it.",
    "Don't stop when you're tired. Stop when you're done.",
    "Wake up with determination. Go to bed with satisfaction.",
    "Do something today that your future self will thank you for.",
    "Little things make big days.",
    "It's going to be hard, but hard does not mean impossible.",
    "Don't wait for opportunity. Create it.",
]

def play_sound_conditional(level):
    """Plays the sound a specified number of times based on task difficulty."""
    num_plays = POINTS_BY_LEVEL.get(level, {}).get("sound_plays", 0)
    try:
        for _ in range(num_plays):
            playsound(SOUND_FILE)
            time.sleep(0.2) # Small delay between sounds for distinct playback
    except Exception as e:
        print(f"Sound error: {e}. Please ensure '{SOUND_FILE}' exists and is accessible.")
        messagebox.showerror("Sound Error", f"Could not play sound: {e}\nPlease check if '{SOUND_FILE}' exists and is accessible.")


def generate_quote():
    """Returns a random motivational quote."""
    return random.choice(MOTIVATIONAL_QUOTES)

def get_daily_data():
    """Reads the raw log file (CSV) and returns parsed entries and daily totals."""
    daily_totals = defaultdict(int)
    raw_entries = []
    # Check if the raw log file exists before attempting to open
    if not os.path.exists(RAW_LOG_FILE):
        print(f"RAW_LOG_FILE not found: {RAW_LOG_FILE}. Returning empty data.")
        return raw_entries, daily_totals

    try:
        with open(RAW_LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        # Attempt to split by 5 parts (date, time, level, points, emoji)
                        parts = line.split(",")
                        date, task_time, level, points_str = parts[0], parts[1], parts[2], parts[3]
                        # Safely get emoji: if CSV has 5+ parts, use last; otherwise, derive from POINTS_BY_LEVEL
                        emoji = parts[-1] if len(parts) > 4 else POINTS_BY_LEVEL.get(level, {}).get("emoji", "")
                        
                        points = int(points_str)
                        raw_entries.append({
                            "date": date,
                            "time": task_time,
                            "level": level,
                            "points": points,
                            "emoji": emoji
                        })
                        daily_totals.setdefault(date, 0)
                        daily_totals[date] += points
                    except ValueError:
                        print(f"Skipping malformed raw log entry: '{line}' - Please manually delete '{RAW_LOG_FILE}' to fix this if persistent.")
                        continue
    except PermissionError as e:
        messagebox.showerror("File Access Error", f"Permission denied to read '{RAW_LOG_FILE}'.\nError: {e}\nPlease check file permissions.")
        print(f"File Access Error: Permission denied to read '{RAW_LOG_FILE}'. Error: {e}")
    except Exception as e:
        messagebox.showerror("File Read Error", f"An error occurred while reading '{RAW_LOG_FILE}'.\nError: {e}")
        print(f"File Read Error: An error occurred while reading '{RAW_LOG_FILE}'. Error: {e}")

    return raw_entries, daily_totals


def get_image_as_base64(filepath):
    """Reads an image file and returns its base64 encoded string."""
    try:
        with open(filepath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/png;base64,{encoded_string}"
    except FileNotFoundError:
        print(f"Error: Image file not found at {filepath}")
        return ""
    except Exception as e:
        print(f"Error encoding image {filepath}: {e}")
        return ""

def update_display_log_file():
    """
    Reads the raw log data, calculates daily summaries, generates charts,
    and rewrites the DISPLAY_LOG_FILE as an HTML file with embedded charts.
    """
    raw_entries, daily_totals = get_daily_data()

    if not raw_entries and os.path.exists(RAW_LOG_FILE):
        messagebox.showwarning(
            "No Usable Data Found",
            f"The file '{RAW_LOG_FILE}' exists but contains no valid productivity data.\n\n"
            "This is often caused by malformed entries from previous versions.\n"
            "To fix this, please manually DELETE the file:\n"
            f"{RAW_LOG_FILE}\n"
            "Then, log a new task to create a fresh, clean log."
        )
    elif not raw_entries and not os.path.exists(RAW_LOG_FILE):
        messagebox.showinfo(
            "No Data File Yet",
            f"The productivity data file '{RAW_LOG_FILE}' was not found.\n"
            "Please log your first task to create it and start tracking!"
        )

    # Generate charts and save them first
    chart_paths = generate_and_save_charts(daily_totals, raw_entries)

    # Get base64 encoded images
    trend_chart_b64 = get_image_as_base64(chart_paths.get("trend_chart", ""))
    today_chart_b64 = get_image_as_base64(chart_paths.get("today_chart", ""))
    all_days_chart_b64 = get_image_as_base64(chart_paths.get("all_days_comparison_chart", ""))


    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Productivity Log</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                margin: 20px;
                background-color: #f4f7f6;
                color: #333;
                line-height: 1.6;
            }}
            h1, h2 {{
                color: #2c3e50;
                text-align: center;
                margin-bottom: 15px;
            }}
            hr {{
                border: none;
                border-top: 1px solid #eee;
                width: 80%;
                margin: 25px auto;
            }}
            table {{
                width: 90%;
                margin: 20px auto;
                border-collapse: collapse;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                overflow: hidden;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #e9f5ff;
            }}
            .summary-table th {{
                background-color: #28b463;
            }}
            .today-table th {{
                background-color: #E74C3C; /* A distinct color for today's tasks */
            }}
            .no-data {{
                text-align: center;
                padding: 20px;
                color: #777;
            }}
            .chart-container {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
                margin-top: 30px;
            }}
            .chart-card {{
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                padding: 20px;
                text-align: center;
                flex: 1 1 calc(33% - 40px);
                min-width: 300px;
                max-width: 500px;
            }}
            .chart-card img {{
                max-width: 100%;
                height: auto;
                border-radius: 5px;
            }}
            @media (max-width: 768px) {{
                .chart-card {{
                    flex: 1 1 calc(50% - 40px);
                }}
            }}
            @media (max-width: 480px) {{
                .chart-card {{
                    flex: 1 1 calc(100% - 40px);
                }}
            }}
        </style>
    </head>
    <body>
        <h1>Productivity Log</h1>
        <hr>

        <h2>Detailed Entries (All Time)</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Level</th>
                    <th>Points</th>
                    <th>Emoji</th>
                </tr>
            </thead>
            <tbody>
    """

    if raw_entries:
        # Sort raw entries by date and then time for chronological display
        # sorted_raw_entries = sorted(raw_entries, key=lambda x: (x['date'], x['time']))
        sorted_raw_entries = sorted(raw_entries, key=lambda x: (x['date'], datetime.datetime.strptime(x['time'], '%I:%M %p')))
        for entry in sorted_raw_entries:
            html_content += f"""
                <tr>
                    <td>{entry['date']}</td>
                    <td>{entry['time']}</td>
                    <td>{entry['level'].capitalize()}</td>
                    <td>{entry['points']}</td>
                    <td>{entry['emoji']}</td>

                </tr>
            """
    else:
        html_content += """
                <tr>
                    <td colspan="5" class="no-data">No detailed entries available yet.</td>
                </tr>
        """

    html_content += """
            </tbody>
        </table>

        <h2>Daily Summary (All Recorded Days)</h2>
        <table class="summary-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Total Points</th>
                </tr>
            </thead>
            <tbody>
    """

    if daily_totals:
        sorted_dates = sorted(daily_totals.keys())
        for date in sorted_dates:
            html_content += f"""
                <tr>
                    <td>{date}</td>
                    <td>{daily_totals.get(date, 0)}</td>
                </tr>
            """
    else:
        html_content += """
                <tr>
                    <td colspan="2" class="no-data">No daily summary available yet.</td>
                </tr>
        """

    html_content += """
            </tbody>
        </table>

        <h2>Today's Productivity</h2>
        <table class="today-table">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Level</th>
                    <th>Points</th>
                    <th>Emoji</th>
                </tr>
            </thead>
            <tbody>
    """
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_tasks_only = [entry for entry in raw_entries if entry["date"] == today_str]
    if today_tasks_only:
        # Sort today's tasks by time
        # sorted_today_tasks = sorted(today_tasks_only, key=lambda x: x['time'])
        sorted_today_tasks = sorted(today_tasks_only, key=lambda x: datetime.datetime.strptime(x['time'], '%I:%M %p'))
        for entry in sorted_today_tasks:
            html_content += f"""
                <tr>
                    <td>{entry['time']}</td>
                    <td>{entry['level'].capitalize()}</td>
                    <td>{entry['points']}</td>
                    <td>{entry['emoji']}</td>
                </tr>
            """
        html_content += f"""
                <tr>
                    <td colspan="2" style="text-align: right; font-weight: bold;">Today's Total:</td>
                    <td colspan="2" style="font-weight: bold;">{daily_totals.get(today_str, 0)} points</td>
                </tr>
        """
    else:
        html_content += """
                <tr>
                    <td colspan="4" class="no-data">No tasks logged today yet.</td>
                </tr>
        """

    html_content += f"""
            </tbody>
        </table>

        <hr>
        <h2>Productivity Visuals</h2>
        <div class="chart-container">
            <div class="chart-card">
                <h3>Today's Task Performance</h3>
                <img src="{trend_chart_b64}" alt="Today's Task Performance Chart">
            </div>
            <div class="chart-card">
                <h3>Today's Productivity Breakdown</h3>
                <img src="{today_chart_b64}" alt="Today's Productivity Chart">
            </div>
            <div class="chart-card">
                <h3>Daily Points Comparison (All Days)</h3>
                <img src="{all_days_chart_b64}" alt="All Days Productivity Comparison Chart">
            </div>
        </div>
    </body>
    </html>
    """
    try:
        with open(DISPLAY_LOG_FILE, "w") as f:
            f.write(html_content)
            print(f"Successfully wrote HTML log to: {DISPLAY_LOG_FILE}")
    except PermissionError as e:
        messagebox.showerror("File Access Error", f"Permission denied to write to '{DISPLAY_LOG_FILE}'.\nError: {e}\nPlease check file permissions.")
        print(f"File Access Error: Permission denied to write to '{DISPLAY_LOG_FILE}'. Error: {e}")
    except Exception as e:
        messagebox.showerror("File Write Error", f"An error occurred while writing to '{DISPLAY_LOG_FILE}'.\nError: {e}")
        print(f"File Write Error: An error occurred while writing to '{DISPLAY_LOG_FILE}'. Error: {e}")


def generate_and_save_charts(daily_totals, raw_entries):
    """
    Generates and saves three charts as PNG files with enhanced aesthetics.
    Returns a dictionary of saved chart paths.
    """
    chart_paths = {}
    plt.style.use('seaborn-v0_8-whitegrid')

    # --- 1. Today's Task Performance (Line Graph with High-Low Line) ---
    fig1, ax1 = plt.subplots(figsize=(12, 8))
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_tasks = [entry for entry in raw_entries if entry["date"] == today_str]

    if today_tasks:
        # Sort tasks by time for correct chronological plotting
        today_tasks.sort(key=lambda x: datetime.datetime.strptime(x['time'], '%I:%M %p'))

        # Extract hours and points, converting time to a float for continuous x-axis
        # FIX: Changed '%H:%M' to '%I:%M %p' to match your log format
        hours = [datetime.datetime.strptime(task['time'], '%I:%M %p').hour + datetime.datetime.strptime(task['time'], '%I:%M %p').minute / 60 for task in today_tasks]
        points = [task['points'] for task in today_tasks]

        # Background
        fig1.patch.set_facecolor("#F8F6F1")
        ax1.set_facecolor("#F8F6F1")

        # Grid Styling
        ax1.grid(True, axis='y', linestyle='--', alpha=0.6, color='#D3D3D3')
        ax1.xaxis.grid(False)

        # Plot individual task points and connect them
        ax1.plot(hours, points, marker="o", markersize=8, color="#1F77B4", linestyle='-', linewidth=1.5, label='Task Points')

        # Find daily high and low points
        if points: # Only proceed if there are points to analyze
            # Find the actual tasks corresponding to min/max points to get their hours
            min_point_val = min(points)
            max_point_val = max(points)
            
            # Find the first occurrence of min/max task (if multiple tasks have same min/max points)
            # This ensures we get the time associated with that min/max point
            min_task_idx = next(i for i, p in enumerate(points) if p == min_point_val)
            max_task_idx = next(i for i, p in enumerate(points) if p == max_point_val)

            min_hour_val = hours[min_task_idx]
            max_hour_val = hours[max_task_idx]

            # Plot the high-low line (connecting the earliest min point to the earliest max point)
            ax1.plot([min_hour_val, max_hour_val], [min_point_val, max_point_val], color="#FF7F0E", linestyle='--', linewidth=2, label='Daily Range')

            # Annotate high and low points
            # Ensure text labels are clear and don't overlap with markers too much
            ax1.text(max_hour_val, max_point_val + 0.2, f'{max_point_val}', ha='center', va='bottom', fontsize=9, color="#222222")
            ax1.text(min_hour_val, min_point_val - 0.4, f'{min_point_val}', ha='center', va='top', fontsize=9, color="#222222")

        # Title and Labels
        ax1.set_title(f"Today's Task Performance ({today_str})", fontsize=20, color="#222222", fontweight='bold', pad=15)
        ax1.set_xlabel("Hour of Day", fontsize=16, color="#555555")
        ax1.set_ylabel("Points", fontsize=16, color="#555555")

        # Ticks - Adjust x-axis ticks to be more readable for hours
        # Determine min and max hour from the actual task times
        min_hour = int(min(hours)) - 1  # Pad with 1 hour before
        max_hour = int(max(hours)) + 2  # Pad with 2 hours after

        # Limit range between 0 and 23
        min_hour = max(min_hour, 0)
        max_hour = min(max_hour, 23)

        # Set x-ticks dynamically
        ax1.set_xticks(range(min_hour, max_hour + 1, 1))
        ax1.set_xlim(min_hour, max_hour)
        ax1.set_xticklabels([f'{h:02d}:00' for h in range(min_hour, max_hour + 1)], rotation=45, ha='right')
        ax1.tick_params(axis='x', labelsize=9, colors="#555555")
        ax1.tick_params(axis='y', labelsize=10, colors="#555555")

        ax1.legend(loc='upper left', fontsize=10)

    else:
        ax1.text(0.5, 0.5, "No tasks logged today yet!", horizontalalignment='center',
                 verticalalignment='center', transform=ax1.transAxes, fontsize=14, color="#777777")
        ax1.set_title(f"Today's Task Performance ({today_str})", fontsize=18, color="#222222", fontweight='bold', pad=15)
        ax1.set_xlabel("Hour of Day", fontsize=14, color="#555555")
        ax1.set_ylabel("Points", fontsize=14, color="#555555")
        ax1.axis('off') # Hide axes if no data
        fig1.patch.set_facecolor("#F8F6F1")
        ax1.set_facecolor("#F8F6F1")

    plt.tight_layout()
    trend_chart_path = os.path.join(CHART_SAVE_DIR, f"productivity_trend_chart_{today_str}.png")
    try:
        plt.savefig(trend_chart_path)
        chart_paths["trend_chart"] = trend_chart_path
    except PermissionError as e:
        messagebox.showerror("Chart Save Error", f"Permission denied to save chart to '{trend_chart_path}'.\nError: {e}")
    except Exception as e:
        messagebox.showerror("Chart Save Error", f"An error occurred while saving chart to '{trend_chart_path}'.\nError: {e}")
    plt.close(fig1)

    # --- 2. Today's Productivity Breakdown (Bar Chart) ---
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_tasks = [entry for entry in raw_entries if entry["date"] == today_str]

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    if today_tasks:
        today_points = [entry["points"] for entry in today_tasks]
        today_labels = [f"{entry['level'].capitalize()} ({entry['time']})" for entry in today_tasks]

        level_colors = {
            "easy": "#8BC34A",   # Light Green
            "medium": "#FFC107", # Amber
            "hard": "#F44336"    # Red
        }
        bar_colors = [level_colors.get(entry["level"], "#9E9E9E") for entry in today_tasks]

        bars = ax2.bar(today_labels, today_points, color=bar_colors, edgecolor='black', linewidth=0.8)
        ax2.set_title(f"🗓️ Today's Productivity Breakdown ({today_str})", fontsize=18, color="#D32F2F", pad=15)
        ax2.set_ylabel("Points", fontsize=14, color="#607D8B")
        ax2.tick_params(axis='x', rotation=45, labelsize=10, colors="#757575")
        ax2.tick_params(axis='y', labelsize=10, colors="#757575")
        ax2.set_facecolor("#F9F9F9")
        fig2.patch.set_facecolor("#ECEFF1")
        ax2.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            yval = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 1), ha='center', va='bottom', fontsize=10, color='black')
    else:
        ax2.text(0.5, 0.5, "No tasks logged today yet!", horizontalalignment='center',
                 verticalalignment='center', transform=ax2.transAxes, fontsize=14, color="#777777")
        ax2.set_title(f"🗓️ Today's Productivity Breakdown ({today_str})", fontsize=18, color="#D32F2F", pad=15)
        ax2.axis('off')
    plt.tight_layout()
    today_chart_path = os.path.join(CHART_SAVE_DIR, f"today_productivity_chart_{today_str}.png")
    try:
        plt.savefig(today_chart_path)
        chart_paths["today_chart"] = today_chart_path
    except PermissionError as e:
        messagebox.showerror("Chart Save Error", f"Permission denied to save chart to '{today_chart_path}'.\nError: {e}")
    except Exception as e:
        messagebox.showerror("Chart Save Error", f"An error occurred while saving chart to '{today_chart_path}'.\nError: {e}")
    plt.close(fig2)

    # --- 3. All Days Productivity Comparison (Bar Chart) ---
    today_str = datetime.datetime.now().strftime("%Y-%m-%d") # Re-declare today_str for clarity here
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    if daily_totals:
        sorted_dates = sorted(daily_totals.keys())
        comparison_values = [daily_totals.get(date, 0) for date in sorted_dates]

        bar_colors = "#FFDAB9" # Peach Puff color

        bars = ax3.bar(sorted_dates, comparison_values, color=bar_colors, width=0.7, edgecolor='black', linewidth=0.8)
        ax3.set_title("🏆 Daily Points Comparison (All Days)", fontsize=18, color="#00796B", pad=15)
        ax3.set_xlabel("Date", fontsize=14, color="#607D8B")
        ax3.set_ylabel("Total Points", fontsize=14, color="#607D8B")
        ax3.tick_params(axis='x', rotation=45, labelsize=10, colors="#757575")
        ax3.tick_params(axis='y', labelsize=10, colors="#757575")
        ax3.set_facecolor("#F9F9F9")
        fig3.patch.set_facecolor("#ECEFF1")
        ax3.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            yval = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, yval + 0.5, str(yval), ha='center', va='bottom', fontsize=10, color='black')
    else:
        ax3.text(0.5, 0.5, "No daily comparison data yet!", horizontalalignment='center',
                 verticalalignment='center', transform=ax3.transAxes, fontsize=14, color="#000000")
        ax3.set_title("🏆 Daily Points Comparison (All Days)", fontsize=18, color="#00796B", pad=15)
        ax3.axis('off')
    plt.tight_layout()
    all_days_comparison_chart_path = os.path.join(CHART_SAVE_DIR, f"all_days_comparison_chart_{today_str}.png")
    try:
        plt.savefig(all_days_comparison_chart_path)
        chart_paths["all_days_comparison_chart"] = all_days_comparison_chart_path
    except PermissionError as e:
        messagebox.showerror("Chart Save Error", f"Permission denied to save chart to '{all_days_comparison_chart_path}'.\nError: {e}")
    except Exception as e:
        messagebox.showerror("Chart Save Error", f"An error occurred while saving chart to '{all_days_comparison_chart_path}'.\nError: {e}")
    plt.close(fig3)

    return chart_paths

def show_chart():
    """
    This function is now largely redundant as charts are embedded in HTML.
    It will just call update_display_log_file to ensure charts are regenerated.
    """
    pass


def log_task(level):
    """Logs a task with its details to the raw CSV log file."""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%I:%M %p") # Use 12-hour format with AM/PM for consistency
    entry = POINTS_BY_LEVEL[level]
    points = entry["points"]
    emoji = entry["emoji"] 

#   line = f"{date_str},{time_str},{level},{points},{emoji}\n"
    line = f"{date_str},{time_str},{level},{points}\n"  # Removed emoji from raw log for simplicity

    print(f"Attempting to write to RAW_LOG_FILE: {RAW_LOG_FILE}")
    try:
        # Append to the raw CSV file. This line *creates* the file if it doesn't exist.
        with open(RAW_LOG_FILE, "a") as f:
            f.write(line)
        print(f"Successfully wrote line to RAW_LOG_FILE: {line.strip()}")
    except PermissionError as e:
        error_msg = f"CRITICAL FILE WRITE ERROR: Permission denied to write to '{RAW_LOG_FILE}'.\nError: {e}\nPlease check file and directory permissions for '{LOG_FILES_DIR}'."
        messagebox.showerror("File Write Error", error_msg)
        print(error_msg)
        return 0, "Error: Could not log task due to file permissions."
    except Exception as e:
        error_msg = f"CRITICAL FILE WRITE ERROR: An unexpected error occurred while writing to '{RAW_LOG_FILE}'.\nError: {e}"
        messagebox.showerror("File Write Error", error_msg)
        print(error_msg)
        return 0, "Error: Could not log task due to unexpected file error."

    return points, f"{emoji} [{date_str} {time_str}] {level.upper()} task — +{points} points! 🏆"


def handle_click(level):
    """Handles button clicks, logs task, plays sound, shows message, and updates charts."""
    play_sound_conditional(level)
    points, log_msg = log_task(level) # log to RAW_LOG_FILE
    
    # Only proceed with updating display and showing quote if logging was successful
    if "Error" not in log_msg: # Simple check for error message from log_task
        update_display_log_file() # This now generates the HTML with embedded charts
        quote = generate_quote()
        messagebox.showinfo("✅ Task Logged!", f"{log_msg}\n\n \"{quote}\"")
    else:
        # If log_task returned an error, the error message box was already shown
        pass

# === GUI ===
root = tk.Tk()
root.title("🎯 I Did It!")
root.geometry("290x300") # Slightly taller to accommodate new button
root.configure(bg="#EAF2F8")

font_heading = ("Helvetica Neue", 16, "bold")
font_button = ("Arial", 12)

label = tk.Label(root, text="Select Task Difficulty", font=font_heading, bg="#EAF2F8", fg="#333333")
label.pack(pady=20)

button_style = {
    "width": 25,
    "height": 2,
    "font": font_button,
    "fg": "black",
    "relief": "raised",
    "bd": 3,
    "activebackground": "#2186C1",
    "activeforeground": "black",
    "cursor": "hand2",
    "highlightbackground": "#85C1E9",
    "highlightthickness": 2
}

tk.Button(root, text="🌱 Easy", bg="#2ECC71", **button_style, command=lambda: handle_click("easy")).pack(pady=7)
tk.Button(root, text="⚡ Medium", bg="#F1C40F", **button_style, command=lambda: handle_click("medium")).pack(pady=7)
tk.Button(root, text="🔥 Hard", bg="#E74C3C", **button_style, command=lambda: handle_click("hard")).pack(pady=7)
"""
# New "Refresh Log" button
refresh_button_style = {
    "width": 25,
    "height": 2,
    "font": font_button,
    "fg": "white",
    "bg": "#5DADE2",
    "relief": "raised",
    "bd": 3,
    "activebackground": "#3498DB",
    "activeforeground": "white",
    "cursor": "hand2",
    "highlightbackground": "#AAB7B8",
    "highlightthickness": 2
}
tk.Button(root, text="🔄 Refresh Log", **refresh_button_style, command=update_display_log_file).pack(pady=15)
"""

# Initial log file formatting on startup
update_display_log_file()

root.mainloop()