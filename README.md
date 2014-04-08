king_of_northampton
===================

An experimental dice based game made with Django on Google App Engine.

Loosely based on the board game 'King of Tokyo'.

Each turn consists of 3 rolls of the 6 die. After each roll you can choose which die you want to hold.

The dice are five sided with the following faces: Attack, Heart, 1, 2, 3

Get three of the same numbers (either 1, 2 or 3) to earn that number of victory points. Get 1 extra point for each addition dice of the same face.

Each attack takes 1 health point off your opponent. Each heart recovers 1 health point for yourself.

Each player starts on 10 health and 0 victory points. Win by killing your opponent (getting their health to zero), or reaching 20 victory points.
