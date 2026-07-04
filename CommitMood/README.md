# CommitMood 🎭

Turn your git history into a mood ring.

CommitMood reads your commit messages and builds a GitHub-style
contribution calendar — except instead of coloring each day by how
*many* commits you made, it colors each day by how your commits
*felt*. Grumpy commit messages before a deadline? Cheerful ones right
after fixing that annoying bug? Now you can actually see it.

```
CommitMood — sentiment calendar

Sun  ░ ░ ▒ ▓ █ ▒ ░ ░ ▓ ░ ░ ░ ▒
Mon  ░ ▓ ▒ ▓ ▓ ░ ░ ▓ ▓ ░ ░ ▒ ░
Tue  ░ █ ░ ▒ ░ ░ ▓ ▒ ░ ░ ░ ░ ░
Wed  ▒ ▓ ░ ▓ ░ ▓ ▒ ░ ░ ▓ ░ ░ ░
Thu  ░ ▒ ▓ ░ ░ ▒ ░ ░ ▓ ░ ▒ ░ ░
Fri  ▓ ░ ░ ▓ ░ ░ ░ ▓ ░ ░ ░ ▓ ░
Sat  ░ ░ ▒ ░ ░ ░ ▒ ░ ░ ░ ░ ░ ░

Legend:  █ very negative  ▓ negative  ▒ neutral  ▓ positive  █ very positive  ░ no commits

Total commits analyzed: 84
Overall mood score: +0.112  (content)
```

## How it works

1. Reads `git log` from any local repo.
2. Scores each commit message with [VADER sentiment analysis](https://github.com/cjhutto/vaderSentiment)
   (built for short, informal text — a good fit for commit messages).
3. Averages sentiment per day and renders it as a colored calendar,
   right in your terminal.
4. Optionally exports the same calendar as a PNG heatmap.

## Install

```bash
git clone https://github.com/yourusername/commitmood.git
cd commitmood
pip install -r requirements.txt
```

## Usage

Analyze the repo you're standing in, last 90 days (default):

```bash
python commitmood.py
```

Analyze a different repo, over a custom time range:

```bash
python commitmood.py /path/to/other/repo --days 180
```

Export a PNG version of the calendar:

```bash
python commitmood.py --export mood.png
```

## Why this exists

Commit messages are an honest, unfiltered log of how a project (and
the person behind it) was doing. `git log` already gives you the raw
data — CommitMood just makes the pattern visible at a glance, the
same way GitHub's contribution graph makes activity visible.

Ideas for where this could go:
- Track mood trends across a team, not just one contributor.
- Correlate mood dips with release dates or incident reports.
- Compare mood across multiple repos/projects.

Pull requests welcome.

## License

MIT — see [LICENSE](LICENSE).
