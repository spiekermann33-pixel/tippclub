import anvil.secrets
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
import base64
from PIL import Image
import requests
from datetime import datetime, timedelta

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

def get_matchup_jackpot(season="2025/2026",gameday=1):
  gameday = app_tables.top_matches.get(season=season, gameday=gameday)
  return gameday["home_team"] + " : " + gameday["away_team"], gameday['jackpot']

# Hilfsfunktion: BlobMedia oder LazyMedia -> Base64-String
def to_data_url(media_obj):
  if not media_obj:
    return ""
  try:
    # sowohl LazyMedia als auch BlobMedia haben .get_bytes()
    data = media_obj.get_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:image/png;base64,{b64}"
  except Exception as e:
    print("⚠️ Fehler bei der Medienkonvertierung:", e)
    return ""
      
def get_team_logos(df):
  logos = app_tables.fav_teams.get(team_id=1)
  print(logos)
  df["Verein"] = to_data_url(logos["logo"])
  return df
  
@anvil.server.callable
def create_tip_image(gameday):
  df_user_tips = pd.DataFrame(get_user_tips(gameday=gameday))
  df_user_tips["Sieg"] = ""
  df_user_tips["Tipp"] = df_user_tips["Tipp"] + "\t"
  matchup, jackpot = get_matchup_jackpot(gameday=gameday)

  # Tabellenzeilen als HTML
  rows_html = ""
  for _, row in df_user_tips.iterrows():
    strafe_cell = (
      f'<td class="strafe">{row["Strafe"]}</td>'
      if row["Strafe"]
      else '<td></td>'
    )
    rows_html += f"""
      <tr>
        <td class="name">{row['Name']}</td>
        <td class="tipp">{str(row['Tipp']).strip()}</td>
        {strafe_cell}
        <td class="sieg">{row['Sieg']}</td>
      </tr>"""

  html_str = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    font-family: 'Helvetica Neue', Arial, sans-serif;
    background: #F4EFF4;
    margin: 0;
    padding: 28px;
  }}
  .card {{
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    max-width: 560px;
    margin: 0 auto;
  }}
  .header {{
    background: #6750A4;
    color: white;
    padding: 22px 28px 18px;
  }}
  .header .spieltag {{
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    opacity: 0.75;
    margin-bottom: 6px;
  }}
  .header .matchup {{
    font-size: 22px;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 14px;
  }}
  .header .meta {{
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    opacity: 0.88;
    border-top: 1px solid rgba(255,255,255,0.25);
    padding-top: 12px;
  }}
  .header .meta span {{
    font-weight: 500;
  }}
  .header .meta .value {{
    font-weight: 700;
    margin-left: 4px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
  }}
  thead tr {{
    background: #EDE7F6;
  }}
  thead th {{
    padding: 11px 20px;
    text-align: left;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #4A148C;
  }}
  thead th.center {{
    text-align: center;
  }}
  tbody tr:nth-child(even) {{
    background: #FAFAFA;
  }}
  tbody tr:nth-child(odd) {{
    background: #FFFFFF;
  }}
  tbody td {{
    padding: 13px 20px;
    font-size: 15px;
    border-bottom: 1px solid #F0EBF8;
    color: #1C1B1F;
  }}
  tbody tr:last-child td {{
    border-bottom: none;
  }}
  td.name {{
    font-weight: 500;
  }}
  td.tipp {{
    font-weight: 700;
    color: #6750A4;
    letter-spacing: 0.5px;
  }}
  td.strafe {{
    color: #B3261E;
    font-weight: 700;
    text-align: center;
  }}
  td.sieg {{
    color: #386A20;
    font-weight: 700;
    font-size: 18px;
    text-align: center;
  }}
  .footer {{
    padding: 10px 20px;
    text-align: right;
    font-size: 11px;
    color: #CAC4D0;
    letter-spacing: 0.3px;
  }}
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="spieltag">Spieltag {gameday}</div>
      <div class="matchup">{matchup}</div>
      <div class="meta">
        <span>Preisgeld: <span class="value">{jackpot} €</span></span>
        <span>Ergebnis: <span class="value">__________</span></span>
      </div>
    </div>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Tipp</th>
          <th class="center">Strafe</th>
          <th class="center">Sieg</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
    <div class="footer">TippClub · Saison 2025/2026</div>
  </div>
</body>
</html>"""

  # Mit WeasyPrint HTML -> PNG in Memory konvertieren
  png_bytes = weasyprint.HTML(string=html_str).write_png()

  img = Image.open(BytesIO(png_bytes))
  cropped = img.crop(img.getbbox())
  out = BytesIO()
  cropped.save(out, format="PNG")
  png_bytes = out.getvalue()

  # als BlobMedia zurückgeben
  return anvil.BlobMedia("image/png", png_bytes, name=f"Tipprunde_{gameday}.png")

# Konfiguration
BASE_URL = 'https://api.football-data.org/v4/'
HEADERS = {'X-Auth-Token': anvil.secrets.get_secret('football-data-api')}
LEAGUE = 'BL1' # Bundesliga

def get_data():
    # 1. Aktuelle Tabelle abrufen
    standings_url = f"{BASE_URL}competitions/{LEAGUE}/standings"
    standings_res = requests.get(standings_url, headers=HEADERS).json()
    # Mapping von Team-Name zu Tabellenplatz erstellen
    table = {}
    for entry in standings_res['standings'][0]['table']:
        table[entry['team']['name']] = entry['position']
    # 2. Nächsten Spieltag abrufen
    matches_url = f"{BASE_URL}competitions/{LEAGUE}/matches?status=SCHEDULED"
    matches_res = requests.get(matches_url, headers=HEADERS).json()
    # Wir nehmen den Spieltag des ersten gefundenen Spiels als "nächsten Spieltag"
    if not matches_res['matches']:
        return "Keine kommenden Spiele gefunden.", None
    next_matchday = matches_res['matches'][0]['matchday']
    upcoming_matches = [m for m in matches_res['matches'] if m['matchday'] == next_matchday]
    return table, upcoming_matches
  
@anvil.server.callable
def find_top_match():
  table, matches = get_data()
  top_match = None
  min_rank_sum = float('inf')
  best_single_rank = float('inf')
  weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

  for match in matches:
    home_team = match['homeTeam']['name']
    away_team = match['awayTeam']['name']

    # Zeitumrechnung: UTC zu MEZ/MESZ (vereinfacht +1h für Winterzeit, +2h für Sommerzeit)
    # Für eine exakte Lösung empfiehlt sich 'pytz' oder 'zoneinfo'
    dt_utc = datetime.strptime(match['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
    dt_local = dt_utc + timedelta(hours=1) # Standardmäßig +1h für deutsche Winterzeit

    formatted_date = f"{weekdays[dt_local.weekday()]}, {dt_local.strftime('%d.%m. %H:%M')}"

    home_rank = table.get(home_team)
    away_rank = table.get(away_team)

    if home_rank is not None and away_rank is not None:
      current_sum = home_rank + away_rank
      current_best_rank = min(home_rank, away_rank)

      if (current_sum < min_rank_sum) or \
      (current_sum == min_rank_sum and current_best_rank < best_single_rank):
        min_rank_sum = current_sum
        best_single_rank = current_best_rank
        top_match = {
          'home': home_team,
          'away': away_team,
          'home_rank': home_rank,
          'away_rank': away_rank,
          'sum': current_sum,
          'kickoff': formatted_date
        }

  return top_match
