# tf2-stats
Pulling tf2 related stats for predictive analysis

Run ETF2L_Stats for gui to draw an interactive graph of player progress through https://etf2l.org divisions, and store account info on a MySQL server

Enter ETF2L id and run to see their match history sorted by division, marker size is dependent on the player's performance in that match (see log_processer.py)
Cross marker means no log info could be found for that match

The ETF2L user id can be found on a player's page url

![ETF2L user id](/media/etf2l_id.jpg)

The progress graph should appear like this once the data is downloaded and processed

![The progress graph](/media/progress_graph.jpg)

Coming soon™
* Threading so it doesn't freeze when downloading data
* Sensible window(and textbox) size
* The actual predictive analysis


Requires Windows and an internet connection

Icon made by [Pixel Perfect](https://www.flaticon.com/authors/pixel-perfect)
From [Flaticon](https://www.flaticon.com/)
