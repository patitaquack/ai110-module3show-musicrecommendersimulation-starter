"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from recommender import load_songs, recommend_songs        # python src/main.py
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs    # python -m src.main


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Taste profile — target values for every scored feature.
    # Numeric features use the same 0–1 scale as songs.csv (tempo_bpm uses BPM).
    user_prefs = {
        # --- Categorical preferences ---
        "genre":  "indie pop",   # preferred genre (weak signal, w=1)
        "mood":   "happy",       # preferred mood  (strong signal, w=3)

        # --- Numeric feature targets ---
        "energy":           0.75,  # upbeat but not exhausting
        "valence":          0.80,  # positive, feel-good vibe
        "acousticness":     0.30,  # leans produced, some organic texture ok
        "tempo_bpm":       118.0,  # mid-high tempo — energetic but not frantic
        "instrumentalness": 0.05,  # prefers songs with vocals
        "liveness":         0.12,  # studio recordings preferred
        "mode":             1.0,   # major key (bright, uplifting)
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # ----------------------------------------------------------------
    # Output — formatted recommendation cards
    # Each card shows rank, title, artist, score bar, and per-feature
    # reasons broken out on individual lines for easy reading.
    # ----------------------------------------------------------------
    total = len(recommendations)
    divider = "-" * 60

    print(f"\n{'TOP RECOMMENDATIONS':^60}")
    print(divider)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        # Score bar: 20 blocks scaled to the 0-1 score
        filled = round(score * 20)
        bar = "#" * filled + "." * (20 - filled)

        print(f"  #{rank} of {total}  |  {song['title']} -- {song['artist']}")
        print(f"      Genre: {song['genre']:<12}  Mood: {song['mood']}")
        print(f"      Score: [{bar}] {score:.2f}")
        print(f"      Why:")
        for reason in explanation.split(" | "):
            print(f"        - {reason}")
        print(divider)


if __name__ == "__main__":
    main()
