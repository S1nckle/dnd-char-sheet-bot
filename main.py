from playersheetapi import *

sheet = PlayerSheet()
sheet.fill_header()
sheet.fill_stats()

print(sheet)