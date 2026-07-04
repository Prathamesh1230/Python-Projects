#!/usr/bin/env python3
"""
CommitMood — visualize the emotional tone of your git commit history.

Turns your commit messages into a GitHub-style contribution calendar,
but colored by *sentiment* instead of commit count. Watch your code
get grumpier before a deadline, or happier right after a refactor.
"""

import argparse
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta

from colorama import Fore, Style, init as colorama_init
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

colorama_init(autoreset=True)


def get_commits(repo_path, days):
    """Return a list of (date_str, message) tuples from git log."""
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            [
                "git", "-C", repo_path, "log", f"--since={since}",
                "--pretty=format:%ad|%s", "--date=short",
            ],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error reading git log: {e.stderr.strip()}")
        sys.exit(1)
    except FileNotFoundError:
        print("Git is not installed or not found in PATH.")
        sys.exit(1)

    commits = []
    for line in result.stdout.splitlines():
        if "|" not in line:
            continue
        date_str, msg = line.split("|", 1)
        commits.append((date_str, msg))
    return commits


def analyze_mood(commits):
    """Compute average sentiment score and commit count per date."""
    analyzer = SentimentIntensityAnalyzer()
    scores = defaultdict(list)
    for date_str, msg in commits:
        score = analyzer.polarity_scores(msg)["compound"]
        scores[date_str].append(score)

    daily_avg = {d: sum(v) / len(v) for d, v in scores.items()}
    daily_count = {d: len(v) for d, v in scores.items()}
    return daily_avg, daily_count


def mood_color(score):
    """Map a sentiment score to a colored block character."""
    if score is None:
        return Style.DIM + "░" + Style.RESET_ALL
    if score >= 0.5:
        return Fore.GREEN + "█" + Style.RESET_ALL
    if score >= 0.05:
        return Fore.CYAN + "▓" + Style.RESET_ALL
    if score > -0.05:
        return Fore.YELLOW + "▒" + Style.RESET_ALL
    if score > -0.5:
        return Fore.MAGENTA + "▓" + Style.RESET_ALL
    return Fore.RED + "█" + Style.RESET_ALL


def mood_label(score):
    if score >= 0.5:
        return "thriving"
    if score >= 0.05:
        return "content"
    if score > -0.05:
        return "neutral"
    if score > -0.5:
        return "stressed"
    return "burnt out"


def print_calendar(daily_avg, daily_count, days):
    """Print a GitHub-style contribution calendar colored by mood."""
    today = datetime.now().date()
    start = today - timedelta(days=days - 1)
    start -= timedelta(days=(start.weekday() + 1) % 7)  # align to Sunday

    total_days = (today - start).days + 1
    weeks = (total_days // 7) + 1

    print("\nCommitMood — sentiment calendar\n")

    grid = [["  " for _ in range(weeks)] for _ in range(7)]
    for w in range(weeks):
        for d in range(7):
            day = start + timedelta(days=w * 7 + d)
            if day > today:
                continue
            key = day.strftime("%Y-%m-%d")
            score = daily_avg.get(key)
            grid[d][w] = mood_color(score) + " "

    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for d in range(7):
        row = "".join(grid[d])
        print(f"{day_labels[d]}  {row}")

    print("\nLegend:  ", end="")
    print(Fore.RED + "█" + Style.RESET_ALL, "very negative  ", end="")
    print(Fore.MAGENTA + "▓" + Style.RESET_ALL, "negative  ", end="")
    print(Fore.YELLOW + "▒" + Style.RESET_ALL, "neutral  ", end="")
    print(Fore.CYAN + "▓" + Style.RESET_ALL, "positive  ", end="")
    print(Fore.GREEN + "█" + Style.RESET_ALL, "very positive  ", end="")
    print(Style.DIM + "░" + Style.RESET_ALL, "no commits")

    total_commits = sum(daily_count.values())
    if total_commits:
        overall = sum(s * daily_count[d] for d, s in daily_avg.items()) / total_commits
        print(f"\nTotal commits analyzed: {total_commits}")
        print(f"Overall mood score: {overall:+.3f}  ({mood_label(overall)})")
    else:
        print("\nNo commits found in this time range.")


def export_png(daily_avg, days, filename):
    """Export the mood calendar as a PNG heatmap using matplotlib."""
    import matplotlib.pyplot as plt
    import numpy as np

    today = datetime.now().date()
    start = today - timedelta(days=days - 1)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    total_days = (today - start).days + 1
    weeks = (total_days // 7) + 1

    matrix = np.full((7, weeks), np.nan)
    for w in range(weeks):
        for d in range(7):
            day = start + timedelta(days=w * 7 + d)
            if day > today:
                continue
            key = day.strftime("%Y-%m-%d")
            if key in daily_avg:
                matrix[d, w] = daily_avg[key]

    fig, ax = plt.subplots(figsize=(weeks * 0.3 + 2, 3))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
    ax.set_yticks(range(7))
    ax.set_yticklabels(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
    ax.set_xticks([])
    ax.set_title("CommitMood — sentiment calendar")
    fig.colorbar(im, ax=ax, label="sentiment", fraction=0.02)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    print(f"Saved calendar image to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize the emotional tone of your git commit history."
    )
    parser.add_argument(
        "repo", nargs="?", default=".",
        help="Path to git repo (default: current directory)",
    )
    parser.add_argument(
        "--days", type=int, default=90,
        help="Number of days to analyze (default: 90)",
    )
    parser.add_argument(
        "--export", metavar="FILE.png",
        help="Export the calendar as a PNG image",
    )
    args = parser.parse_args()

    commits = get_commits(args.repo, args.days)
    daily_avg, daily_count = analyze_mood(commits)
    print_calendar(daily_avg, daily_count, args.days)

    if args.export:
        export_png(daily_avg, args.days, args.export)


if __name__ == "__main__":
    main()
