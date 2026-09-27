Tennis Match Predictor

A tennis-only stats and machine learning project that analyzes player performance, tracks Elo ratings, and predicts match outcomes based on playstyle and historical data.
<img width="442" height="387" alt="image" src="https://github.com/user-attachments/assets/4bfb5123-2e4b-40cf-971c-b4b209a108b8" />



Player Stats & Head-to-Head
<img width="517" height="276" alt="image" src="https://github.com/user-attachments/assets/cac3f9ac-6c10-4b50-9e2c-ade787dbceff" />



Tracks per-player performance metrics including ace rate, first/second serve win %, break points saved/converted %, return points won %, and head-to-head records between any two players, presented as side-by-side comparisons for a given matchup.


Elo Ratings

A surface-specific Elo rating system (hard, clay, grass) that adjusts starting Elo and K-factor by tournament tier (ATP 250/500/1000, Grand Slams), giving a more accurate picture of player strength than a single overall rating.

<img width="548" height="328" alt="image" src="https://github.com/user-attachments/assets/ac2f80b5-7522-4c2e-8dc4-9a80265bff4e" />


ML Model

A scikit-learn model trained on aggregate match stats (serve %, break points, surface, recent form, head-to-head) to predict match outcomes for top-100 players. Currently sitting at 63.4% accuracy, with ongoing work to improve performance before adding situational features (big points, serve tendencies) for top players in a later phase.
