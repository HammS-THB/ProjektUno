import cairosvg

# Kartengröße
card_width = 240
card_height = 360

# Koordinaten der gewünschten Karte (Spalte 2, Zeile 1)
col = 2
row = 1

x = col * card_width
y = row * card_height

# Input- und Output-Dateien
svg_file = "UNO_cards_deck.svg"
output_file = "uno_card_2_1.png"

# Zuschneiden und als PNG speichern
for row in range(8):
    for col in range(13):
        x = col * card_width
        y = row * card_height
        output_file = f"uno_card_{row}_{col}.png"
        cairosvg.svg2png(
            url=svg_file,
            write_to=output_file,
            output_width=card_width,
            output_height=card_height,
            x=x,
            y=y,
        )

