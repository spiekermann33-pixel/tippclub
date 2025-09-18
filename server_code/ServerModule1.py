import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

@anvil.server.callable
def create_tip_image():
  from io import BytesIO
  from PIL import Image, ImageDraw
  # Beispielbild erstellen
  img = Image.new("RGB", (400, 200), color="white")
  d = ImageDraw.Draw(img)
  d.text((10,10), "Hallo Tipp-Runde!", fill="black")

  # In Bytes konvertieren
  buf = BytesIO()
  img.save(buf, format="PNG")
  buf.seek(0)

  # An Anvil zurückgeben
  return anvil.BlobMedia("image/png", buf.read(), name="tabelle.png")
