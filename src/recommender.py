import csv
from operator import itemgetter
from typing import List, Dict, Tuple
from dataclasses import dataclass

# Normalization divisors to bring each numeric feature into [0, 1].
_FEATURE_SCALE: Dict[str, float] = {
    "energy": 1.0,
    "valence": 1.0,
    "acousticness": 1.0,
    "tempo_bpm": 200.0,
    "instrumentalness": 1.0,
    "liveness": 1.0,
    "mode": 1.0,
}

# Weights for each component of the final score.
# Categorical matches (mood, genre) produce 1.0 or 0.0 before weighting.
_WEIGHTS: Dict[str, float] = {
    "energy": 3.0,
    "valence": 2.0,
    "acousticness": 2.0,
    "tempo_bpm": 1.0,
    "instrumentalness": 2.0,  # vocals vs. no vocals — high perceptual impact
    "liveness": 1.0,           # studio vs. live texture
    "mode": 2.0,               # major vs. minor key — strong emotional signal
    "mood": 3.0,
    "genre": 1.0,
}

_TOTAL_WEIGHT: float = sum(_WEIGHTS.values())  # 17.0


def _linear_score(song_value: float, preferred_value: float) -> float:
    """
    Linear decay scoring formula:
        score = max(0, 1 - |song_value - preferred_value|)

    Both values must already be normalized to [0, 1].
    Returns 1.0 for a perfect match, dropping linearly to 0.0
    when the difference reaches 1.0.
    """
    return max(0.0, 1.0 - abs(song_value - preferred_value))


def _weighted_score(song: Dict, user_vec: Dict) -> float:
    """
    Weighted average of linear decay scores (numeric features)
    and exact-match scores (mood, genre).

    total = Σ(weight_i · score_i) / Σ(weight_i)
    """
    total = 0.0
    for feature, scale in _FEATURE_SCALE.items():
        s = _linear_score(song[feature] / scale, user_vec[feature] / scale)
        total += _WEIGHTS[feature] * s
    total += _WEIGHTS["mood"]  * (1.0 if song["mood"]  == user_vec.get("mood")  else 0.0)
    total += _WEIGHTS["genre"] * (1.0 if song["genre"] == user_vec.get("genre") else 0.0)
    return total / _TOTAL_WEIGHT


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song against user preferences.

    Algorithm Recipe
    ----------------
    Categorical features — exact match awards full weight points:
      • Mood match  → +3.0 pts  (strongest signal: defines the listening context)
      • Genre match → +1.0 pt   (weaker signal: texture preference, not vibe)

    Numeric features — linear decay per feature, then multiplied by weight:
      • score = max(0, 1 - |song_value - preferred_value|)   [both normalized to 0–1]
      • energy        × 3  — intensity of the song
      • valence       × 2  — emotional positivity
      • acousticness  × 2  — organic vs. electronic texture
      • instrumentalness × 2 — vocals vs. no vocals
      • mode          × 2  — major (bright) vs. minor (dark) key
      • tempo_bpm     × 1  — speed (normalized over 200 BPM)
      • liveness      × 1  — studio vs. live recording

    Final score = Σ(weight × feature_score) / 17   → range [0.0, 1.0]

    Returns
    -------
    score   : float         — final weighted score between 0.0 and 1.0
    reasons : List[str]     — human-readable breakdown of what contributed
    """
    reasons: List[str] = []
    total: float = 0.0

    # ------------------------------------------------------------------
    # Step 1 — Categorical features (exact match → full points or zero)
    # ------------------------------------------------------------------

    # Mood match: worth 3.0 points — the most important single signal.
    # A "happy" user should not be recommended an "intense" track regardless
    # of how close the numeric features are.
    if song["mood"] == user_prefs.get("mood"):
        points = _WEIGHTS["mood"]           # 3.0
        total += points
        reasons.append(f"mood match: '{song['mood']}' (+{points:.1f})")
    else:
        reasons.append(f"mood mismatch: '{song['mood']}' vs '{user_prefs.get('mood')}' (+0.0)")

    # Genre match: worth 1.0 point — a soft preference signal.
    # Good songs outside the preferred genre should still surface, so this
    # weight is intentionally low.
    if song["genre"] == user_prefs.get("genre"):
        points = _WEIGHTS["genre"]          # 1.0
        total += points
        reasons.append(f"genre match: '{song['genre']}' (+{points:.1f})")
    else:
        reasons.append(f"genre mismatch: '{song['genre']}' vs '{user_prefs.get('genre')}' (+0.0)")

    # ------------------------------------------------------------------
    # Step 2 — Numeric features (linear decay × weight)
    # ------------------------------------------------------------------

    for feature, scale in _FEATURE_SCALE.items():
        # Normalize both values to [0, 1] before comparing.
        song_val = song[feature] / scale
        pref_val = float(user_prefs.get(feature, song_val)) / scale  # default: no penalty

        # Linear decay: perfect match = 1.0, drops to 0.0 as distance grows.
        raw = _linear_score(song_val, pref_val)
        weight = _WEIGHTS[feature]
        points = weight * raw
        total += points

        reasons.append(
            f"{feature}: song={song[feature]:.2f} pref={float(user_prefs.get(feature, song[feature])):.2f} "
            f"→ score={raw:.2f} × {weight:.0f} = +{points:.2f}"
        )

    # ------------------------------------------------------------------
    # Step 3 — Normalize to [0, 1] by dividing by the total possible weight
    # ------------------------------------------------------------------
    final_score = total / _TOTAL_WEIGHT

    return final_score, reasons


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float = 0.0
    liveness: float = 0.1
    mode: int = 1


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    prefers_instrumental: bool = False
    prefers_live: bool = False
    preferred_mode: int = 1  # 1 = major, 0 = minor


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _user_vector(self, user: UserProfile) -> Dict:
        """Convert a UserProfile into a numeric feature vector for scoring."""
        return {
            "energy": user.target_energy,
            "valence": 0.7 if user.target_energy >= 0.6 else 0.55,
            "acousticness": 0.85 if user.likes_acoustic else 0.15,
            "tempo_bpm": 130.0 if user.target_energy >= 0.6 else 85.0,
            "instrumentalness": 0.85 if user.prefers_instrumental else 0.1,
            "liveness": 0.7 if user.prefers_live else 0.1,
            "mode": float(user.preferred_mode),
            "mood": user.favorite_mood,
            "genre": user.favorite_genre,
        }

    def _song_dict(self, song: Song) -> Dict:
        """Convert a Song dataclass into a plain dict for scoring."""
        return {
            "energy": song.energy,
            "valence": song.valence,
            "acousticness": song.acousticness,
            "tempo_bpm": song.tempo_bpm,
            "instrumentalness": song.instrumentalness,
            "liveness": song.liveness,
            "mode": float(song.mode),
            "mood": song.mood,
            "genre": song.genre,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs sorted by weighted similarity to the user's profile."""
        user_vec = self._user_vector(user)
        return sorted(
            self.songs,
            key=lambda s: _weighted_score(self._song_dict(s), user_vec),
            reverse=True,
        )[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string explaining why a song was recommended."""
        reasons = []
        if abs(song.energy - user.target_energy) <= 0.15:
            reasons.append(f"energy matches your target ({song.energy:.2f})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood is '{song.mood}' which is your favorite")
        if user.likes_acoustic and song.acousticness >= 0.6:
            reasons.append(f"has an acoustic feel ({song.acousticness:.2f})")
        if not user.likes_acoustic and song.acousticness <= 0.3:
            reasons.append(f"has an electric/produced sound ({song.acousticness:.2f})")
        if user.prefers_instrumental and song.instrumentalness >= 0.6:
            reasons.append(f"mostly instrumental ({song.instrumentalness:.2f})")
        if not user.prefers_instrumental and song.instrumentalness <= 0.2:
            reasons.append(f"has vocals ({song.instrumentalness:.2f})")
        if song.mode == user.preferred_mode:
            key_feel = "major (bright)" if song.mode == 1 else "minor (dark)"
            reasons.append(f"{key_feel} key matches your preference")
        if not reasons:
            reasons.append("overall vibe is close to your profile")
        return "Recommended because: " + ", ".join(reasons) + "."


def load_songs(csv_path: str) -> List[Dict]:
    """
    Read songs.csv and return a list of song dictionaries.

    Each dictionary represents one song with correctly typed fields:
      - Text fields  (title, artist, genre, mood) → str
      - Float fields (energy, valence, danceability, acousticness,
                      instrumentalness, liveness, mode)   → float
      - Integer field (tempo_bpm)                         → int

    Returns an empty list and prints a message if the file cannot
    be opened, so the rest of the program can continue gracefully.
    """
    songs = []

    try:
        # Open the file in text mode; newline="" lets csv handle line endings
        # correctly on all platforms.
        with open(csv_path, newline="", encoding="utf-8") as f:

            # DictReader maps the header row to keys automatically,
            # so each `row` is already a {column_name: value} dict.
            reader = csv.DictReader(f)

            for row in reader:
                # Build a clean song dict with explicit type conversions.
                # Text fields are kept as-is; numeric fields are cast so the
                # scoring math works without extra conversions later.
                song = {
                    # --- identity fields (str) ---
                    "id":     int(row["id"]),      # unique row number
                    "title":  row["title"],
                    "artist": row["artist"],
                    "genre":  row["genre"],
                    "mood":   row["mood"],

                    # --- float features: all on a 0–1 scale ---
                    "energy":       float(row["energy"]),
                    "valence":      float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),

                    # --- int feature: raw beats per minute ---
                    "tempo_bpm": int(float(row["tempo_bpm"])),

                    # --- newer float features: use .get() so the function
                    #     still works on older CSV files that lack these columns ---
                    "instrumentalness": float(row.get("instrumentalness", 0.0)),
                    "liveness":         float(row.get("liveness", 0.1)),
                    "mode":             float(row.get("mode", 1)),
                }

                songs.append(song)

    except FileNotFoundError:
        # Tell the caller what went wrong without crashing the program.
        print(f"[load_songs] File not found: '{csv_path}'. "
              "Check that the path is correct and the file exists.")

    except KeyError as e:
        # A required column is missing from the CSV header.
        print(f"[load_songs] Missing expected column in CSV: {e}. "
              "Make sure the file has the correct headers.")

    # Return whatever was collected — could be an empty list if an error occurred.
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Rank every song in the catalog and return the top-k recommendations.

    This function is the ranking layer. It does not decide *how* a song is
    scored — that is score_song's job. It decides *which* songs to show the
    user by:
      1. Judging every song with score_song
      2. Sorting the full scored list highest-to-lowest
      3. Slicing the top k results

    Parameters
    ----------
    user_prefs : dict  — taste profile with target values for each feature
    songs      : list  — every song loaded from songs.csv
    k          : int   — how many recommendations to return (default 5)

    Returns
    -------
    List of (song_dict, score, explanation) tuples, sorted best-first.
    """

    # ------------------------------------------------------------------
    # Step 1 — Normalise user_prefs into a clean vector.
    # Explicit defaults mean score_song never receives a missing key.
    # ------------------------------------------------------------------
    user_vec = {
        "energy":           float(user_prefs.get("energy",           0.5)),
        "valence":          float(user_prefs.get("valence",          0.65)),
        "acousticness":     float(user_prefs.get("acousticness",     0.5)),
        "tempo_bpm":        float(user_prefs.get("tempo_bpm",        100.0)),
        "instrumentalness": float(user_prefs.get("instrumentalness", 0.1)),
        "liveness":         float(user_prefs.get("liveness",         0.1)),
        "mode":             float(user_prefs.get("mode",             1)),
        "mood":             user_prefs.get("mood"),
        "genre":            user_prefs.get("genre"),
    }

    # ------------------------------------------------------------------
    # Step 2 — The loop: use score_song to judge EVERY song individually.
    # The inner "for score, reasons in [...]" unpacks the tuple returned
    # by score_song so we can join reasons into a string in one expression.
    # Each song is evaluated in isolation — no song knows about any other.
    # ------------------------------------------------------------------
    scored = [
        (song, score, " | ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_vec, song)]
    ]

    # ------------------------------------------------------------------
    # Step 3 & 4 — Sort highest-to-lowest by score (index 1), slice top k.
    # sorted() returns a new list so we chain [:k] directly on one line.
    # ------------------------------------------------------------------
    return sorted(scored, key=itemgetter(1), reverse=True)[:k]
