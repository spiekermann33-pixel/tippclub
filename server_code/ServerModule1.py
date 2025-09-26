import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.media

from io import BytesIO
import pandas as pd
from great_tables import GT
import weasyprint
import io
import os

def get_user_tips(season="2025/2026",gameday=1):
  gameday = app_tables.top_matches.get(season=season, gameday=gameday)

  user_tips = []
  for user in app_tables.users.search(active=True):
    user_tip = app_tables.tips.get(user=user, gameday=gameday)
    if user_tip:
      user_tip_string = str(user_tip["home_score"]) + " : " + str(user_tip["away_score"])
      user_tips.append({"Name":user['user_name'], "Tipp": user_tip_string,"Strafe":""})
    else:
      user_tips.append({"Name":user['user_name'], "Tipp": "","Strafe":"2 €"})
  return user_tips

def get_matchup(season="2025/2026",gameday=1):
  gameday = app_tables.top_matches.get(season=season, gameday=gameday)
  return gameday["home_team"] + " : " + gameday["away_team"]
  
@anvil.server.callable
def create_tip_image():
  gameday = 5
  df_user_tips = pd.DataFrame(get_user_tips(gameday=gameday))
  df_user_tips["Sieg"] = ""
  df_user_tips["Tipp"] = df_user_tips["Tipp"] + "\t"
  matchup = get_matchup(gameday=gameday)

  nbsp = "\u00A0" 
  header_string = f"Spieltag: {gameday} {nbsp*8} Begegnung: {matchup}"
  subtitle_string = f"Preisgeld: {48} € {nbsp*45} Ergebnis: __________"
  # Tabelle mit great-tables
  gt_tbl = (
    GT(df_user_tips)
      .tab_header(title=header_string, subtitle=subtitle_string)
      .tab_options(table_font_size="14px")
  )

  # HTML erzeugen
  html_str = gt_tbl.as_raw_html()

  # Mit WeasyPrint HTML -> PNG in Memory konvertieren
  png_bytes = weasyprint.HTML(string=html_str).write_png()

  # als BlobMedia zurückgeben
  return anvil.BlobMedia("image/png", png_bytes, name="Tipprunde.png")
