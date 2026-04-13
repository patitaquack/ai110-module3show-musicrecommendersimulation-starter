# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: MiZona

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

-A ranked list of the top 5 songs from an 18-song catalog. Each result includes the song title, artist, a similarity score between 0 and 1, and a per-feature breakdown explaining exactly what matched and what didn't.

What assumptions does it make about the user:

The user can describe their taste with specific values — a target energy level, a preferred mood, a favorite genre
Their preferences are consistent and stable for a given session (it cannot handle "I want both chill and intense")
Their mood and genre labels are spelled and cased exactly as they appear in the dataset
They have at least some numeric preferences — a fully blank profile produces meaningless results
Is this for real users or classroom exploration:
This is a classroom exploration project. Its purpose is to make the inner workings of a recommender system transparent and understandable — every weight is visible in the code, every score is fully explainable, and every recommendation comes with a reason. It is not designed for production use, and it does not learn, adapt, or personalize over time. 

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

Algorithm Summary: 
The program compares each song to what the user says they like. Every song gets a score from 0 to 1, where 1 is the best match. Songs with higher scores are recommended first.
Mood and genre must match exactly to earn points. Features like energy or tempo earn more points when they are closer to the user’s preference. Some features matter more than others, so they are given extra weight. All points are added together to create the final score.




## 4. Data  

Describe the dataset the model uses.  

18 songs total — 10 from the original starter file, 8 added during development to expand genre and mood coverage.

Genres respresented: lofi, pop, rock, ambient, synthwave, jazz, indie pop, hip-hop, classical, r&b, country, metal, reggae, blues, edm — 15 genres in total.Most have exactly one song each. Only lofi (3 songs) and pop (2 songs) have more than one representative.

moods repesrented: chill, happy, intense, relaxed, moody, focused, confident, peaceful, romantic, nostalgic, angry, uplifting, melancholic, euphoric — 14 moods in total. Only chill (3 songs), happy (2 songs), and intense (2 songs) appear more than once.

Eight songs were added to fill gaps in genre and mood coverage. The additions brought in hip-hop, classical, r&b, country, metal, reggae, blues, and edm — none of which existed in the starter set. Three new numeric features were also added to every song: instrumentalness, liveness, and mode. No songs were removed.


Musical taste missing in the dataset:

tempo feel vs. tempo value — 90 BPM jazz and 90 BPM hip-hop are stored identically but feel completely different due to groove and rhythm patterns
Loudness — a quiet acoustic guitar and a loud distorted guitar can share the same energy value
Key signature — beyond major/minor, the specific musical key affects emotional color in ways mode alone cannot capture
Language and lyrics — whether a song has English lyrics, no lyrics, or lyrics in another language matters to many listeners
Era and familiarity — a 1960s blues track and a modern blues track score identically despite sounding very different
Emotional complexity — songs that feel both happy and melancholic simultaneously (bittersweet) cannot be represented by a single mood label



Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  


The system gives genre very little importance in the scoring formula, so it has less impact than many other features. This means that even if a user clearly says they prefer EDM, songs from other genres could  rank higher if their energy, valence, or acousticness values are closer to the user’s preferences. While testing..  a profile that selected EDM did not return any EDM songs in the top five results. Instead, ambient and lofi songs ranked higher. This shows the system may ignore one of the user’s specific preferences.
- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected.

profiles tested:

Seven user profiles 

1.Default Profile — indie pop / happy / energy 0.75. Used as the baseline to confirm the system ranked Rooftop Lights first (0.99) and Sunrise City second (0.91), which matched intuition.

2.Conflicting mood vs. energy — mood: melancholic, energy: 0.90. Designed to see which signal would win when the two highest-weighted features pointed in opposite directions. Mood won: "Three AM and Rain" (blues, melancholic, energy 0.33) ranked first despite being far from the energy target.

3.When all features were set to the maximum value of 1.0 with genre set to EDM, only “Strobe Garden” scored close at 0.88. Every other song scored much lower, showing the system does not give high scores to poor matches.

4.When acousticness was set to 0.95 and genre to EDM, those preferences did not fit the dataset. The system returned ambient and lofi songs in the top 5 with zero EDM songs, showing that genre (weight 1) was weaker than acousticness (weight 2).

5.When only mood and energy were entered and all other fields were left blank, the system filled in missing values automatically. This caused songs to receive easy points, and top scores increased from 0.75 to 0.88. The system rewarded users for giving less information.


6.Case sensitivity trap-mood: "Happy", genre: "Indie Pop" (capitalized). The same profile as the default, but with different casing. Every song scored as if no mood or genre preference existed at all, dropping Rooftop Lights from 0.99 to 0.75. The ranking happened to stay the same by coincidence, which made the bug nearly invisible in the output.

7.Perfectly neutral— all numeric features set to 0.5, mood and genre set to None. The top 5 scores clustered between 0.58 and 0.60 — a spread of only 0.02 across four completely different genres (jazz, lofi, reggae, r&b). The system had no meaningful way to differentiate between them.



The most surprising result happened when the user left parts of the profile blank. It seemed like missing information would lower the scores. Instead, the scores became higher because the system used the song’s own values as a match. This made songs look better than they really were. It shows a problem in how the system handles missing information.

The case sensitivity problem was strange because everything looked normal and still gave results but some user preferences were ignored without any warning. I noticed that the recommendations a little worse than usual.

The energy test also showed that songs with very high or very low energy were pushed down the rankings for users who preferred medium energy. Because energy has a strong weight, some songs stayed near the bottom even when other features matched well.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  
The system could be improved by letting users choose a range, such as energy between 0.6 and 0.8, instead of only one exact value. It should also allow users to block genres they dislike, such as metal or lofi. Different users should be able to choose what matters most to them, since some care more about genre while others care more about mood or energy. It would also help to have different profiles for different times of day, like focus music in the morning and calm music at night. 

I would like to use  Gaussian scoring for my next project.
the scoring could be smarter by being more forgiving for small differences while still lowering scores for songs that are far from the user’s preferences.


- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
