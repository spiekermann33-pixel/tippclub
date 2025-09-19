import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from io import BytesIO
from PIL import Image, ImageDraw
import pandas as pd

def get_user_tips(season="2025/2026",gameday=1):
  gameday = app_tables.top_matches.get(season=season, gameday=gameday)

  user_tips = []
  for user in app_tables.users.search(active=True):
    user_tip = app_tables.tips.get(user=user, gameday=gameday)
    if user_tip:
      user_tip_string = str(user_tip["home_score"]) + " : " + str(user_tip["away_score"])
      user_tips.append({"Nane":user['user_name'], "Tipp": user_tip_string,"Strafe":""})
    else:
      user_tips.append({"Nane":user['user_name'], "Tipp": "","Strafe":"2€"})
  return user_tips
    
@anvil.server.callable
def create_tip_image():
  df_user_tips = pd.DataFrame(get_user_tips(gameday=4))

  print(df_user_tips)
  img = Image.new("RGB", (600, 400), color="white")
  d = ImageDraw.Draw(img)
  y = 10
  for line in df_user_tips.astype(str).values.tolist():
    d.text((10, y), " | ".join(line), fill="black")
    y += 20
  
  buf = BytesIO()
  img.save(buf, format="PNG")
  buf.seek(0)
  
  return anvil.BlobMedia("image/png", buf.read(), name="tabelle.png")
