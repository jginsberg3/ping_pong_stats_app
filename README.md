# Ping Ping Statistics App

This is an app to calculate odds of winning a ping pong game based on the historical win/loss record of matches between two players.

The app is made using the Plotly Dash library.  The statistics use a simple Beta distribution to determine the likely range of the true winning probability based on the a prior (user-editable) and observed win/loss data.  