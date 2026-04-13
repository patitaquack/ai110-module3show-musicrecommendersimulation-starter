# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
- For example: genre, mood, energy, tempo

Every song has descriptive labels like "genre" and " mood". It also has numeric measurements from 0 -1. This will measure energy, valence (positive or negative emotion), acousticness, and tempo_bpm.


- What information does your `UserProfile` store:

The user profile captues what a listener is looking for. Such as favorite genre, mood, energy, and preferred sounds like acoustic or non acoustic.

- How does your `Recommender` compute a score for each song

The recommender uses a weighted scoring formula. It checks each song and how close the song is to the user's preferences across every feature and combines it into a final score.

- How do you choose which songs to recommend: 
It first scores every song independently using weighted formula. It then sorts all the songs from highest to lowest score. Finally, it will retun the top k. The default is 5.

Song 1 ──► score() ──► 0.90 ──┐
Song 2 ──► score() ──► 0.52   │
Song 3 ──► score() ──► 0.85   ├──► sort descending ──► top k songs returned
Song 4 ──► score() ──► 0.61   │
Song 5 ──► score() ──► 0.58 ──┘


With my algorithm recipe, the system might "over-reward" songs that match on mood and energy since both capture emotion and are weighted equally at 3. A sond could score top 3 by being the right mood even if the key ot acousticness feel wrong.


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

The system looks at several features of each song, such as energy, mood, tempo, genre, whether it has vocals, and whether it sounds acoustic or electronic. The user then enters their preferences, like wanting a happy, fast, high-energy song. The program compares each song to those preferences and gives more points when the song is closer to what the user wants. Some features, like energy and mood, matter more than others, so they have a bigger effect on the score. After adding everything together, each song gets a final score from 0 to 1, and the top five songs are recommended.

## 4. Data


18 songs total — 10 from the original starter file, 8 added during development to expand genre and mood coverage.

Genres respresented: lofi, pop, rock, ambient, synthwave, jazz, indie pop, hip-hop, classical, r&b, country, metal, reggae, blues, edm — 15 genres in total.Most have exactly one song each. Only lofi (3 songs) and pop (2 songs) have more than one representative.

moods repesrented: chill, happy, intense, relaxed, moody, focused, confident, peaceful, romantic, nostalgic, angry, uplifting, melancholic, euphoric — 14 moods in total. Only chill (3 songs), happy (2 songs), and intense (2 songs) appear more than once.

Eight songs were added to fill gaps in genre and mood coverage. The additions brought in hip-hop, classical, r&b, country, metal, reggae, blues, and edm — none of which existed in the starter set. Three new numeric features were also added to every song: instrumentalness, liveness, and mode. No songs were removed.

---

## 5. Strengths

Where does your recommender work well:

The system works best when the user gives clear and matching preferences. In those cases, it creates strong rankings and the best song is easy to identify. It also does a good job separating opposite styles, such as calm vs intense or acoustic vs electronic music. Another strength is that it clearly explains why each song was recommended by showing what features matched. When one song matches almost everything, the results are easy to trust. It is also a useful learning tool because the weights and scoring process are easy to see and understand.


## 6. Limitations and Bias

The system has some important weaknesses. It gives very little importance to genre, so users may not get the styles they clearly ask for, such as EDM. It uses the same fixed weights for every user, even though different people care about different features like genre, tempo, or energy. Some genres and moods are harder to recommend because their song values or labels are less common in the dataset. This means some users may get worse recommendations without knowing why. In a real product, this could create unfair and less accurate results for certain listeners.

## 7. Evaluation

How did you check your system


I tested 7 profiles in total. 
Comparing it to Spotify or other platforms, I noticed that it is better to use multiple ways to "detect" preferences. Specially by behaviour, which is something that my program can not do.



I used score values (0–1) — the weighted similarity score itself was the only number we tracked. We used it to compare songs against each other and to spot when profiles produced inflated or collapsed scores.
Score gaps — we looked at how far apart the top results were (e.g., 0.99 vs 0.91 vs 0.70) to judge whether the ranking felt meaningful or arbitrary.
Manual intuition checks — we asked "does this result make sense?" after each run. If the top song matched on mood + energy and the explanation backed it up, we called it correct.

---

## 8. Future Work

If you had more time, how would you improve this recommender

I definitely would have liked to include a dislike option, or a way the user can specify about any genres or  artists they'd like to avoid completly. Also a way that a user can provide feedback for a recommendation. If the user disagrees with a recommendation, it will avoid using the same evaluations.


---

## 9. Personal Reflection

A few sentences about what you learned:

My biggest learning moment was understanding how song features like tempo, energy, and mood can be turned into numbers and used to recommend music. It was interesting to see how data can guide recommendations. It was amazing that recommendations could be made just by comparing tempo, energy, and other song features.



