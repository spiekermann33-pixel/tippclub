import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

def get_user_tips(season="2025/2026",gameday=1):
  gameday = app_tables.top_matches.get(season=season, gameday=gameday)

  user_tips = []
  for user in app_tables.users.search(active=True):
    user_tip = app_tables.tips.get(user=user, gameday=gameday)
    if user_tip:
      user_tip_string = str(user_tip["home_score"]) + " : " + str(user_tip["away_score"])
      user_tips.append({"Name":user['user_name'], "Tipp": user_tip_string,"Strafe":""})
    else:
      user_tips.append({"Name":user['user_name'], "Tipp": "","Strafe":"2 EUR"})
  return user_tips

def get_matchup(season="2025/2026",gameday=1):
  gameday = app_tables.top_matches.get(season=season, gameday=gameday)
  return gameday["home_team"] + " : " + gameday["away_team"]
  
@anvil.server.callable
def create_tip_image():
  gameday = 4
  df_user_tips = pd.DataFrame(get_user_tips(gameday=gameday))
  matchup = get_matchup(gameday=gameday)

  # Tabellenparameter
  col_widths = [150, 100, 100, 100]  # Spaltenbreiten
  row_height = 40
  header_height = 50

  # Höhe für die Überschrift reservieren
  title_height = 80
  img_width = sum(col_widths)
  img_height = title_height + header_height + row_height * len(df_user_tips)

  img = Image.new("RGB", (img_width, img_height), "white")
  draw = ImageDraw.Draw(img)

  # Schriftarten
  try:
    font = ImageFont.truetype("arial.ttf", 20)
    font_title = ImageFont.truetype("arial.ttf", 26)
  except:
    font = ImageFont.load_default()
    font_title = font

    # --- Überschrift ---
  title_text = f"Spieltag {gameday}                                         Begegnung: {matchup}"
  prize_text = f"Preisgeld: {192} EUR                     Ergebnis: ____"

  draw.text((10, 10), title_text, fill="black", font=font_title)
  draw.text((10, 45), prize_text, fill="black", font=font)

  # --- Tabellenüberschriften ---
  headers = ["Name", "Tipp", "Strafe", "Sieg"]
  x = 0
  for i, h in enumerate(headers):
    draw.rectangle(
      [x, title_height, x + col_widths[i], title_height + header_height],
      outline="black",
      width=2,
    )
    draw.text((x + 10, title_height + 10), h, fill="black", font=font)
    x += col_widths[i]

    # --- Zeilen zeichnen ---
  y = title_height + header_height
  for _, row in df_user_tips.iterrows():
    x = 0
    for i, key in enumerate(headers):
      text = str(row.get(key, ""))
      draw.rectangle(
        [x, y, x + col_widths[i], y + row_height],
        outline="black",
        width=1,
      )
      draw.text((x + 10, y + 10), text, fill="black", font=font)
      x += col_widths[i]
    y += row_height

    # In Bytes konvertieren
  buf = BytesIO()
  img.save(buf, format="PNG")
  buf.seek(0)

  return anvil.BlobMedia("image/png", buf.read(), name="tabelle.png")
