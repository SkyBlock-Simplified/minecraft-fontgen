from fontTools.ttLib import newTable

def create_font_hmetrics_table(font):
    print("→ 📄 Generating horizontal metrics table...")
    font["hmtx"] = newTable("hmtx")
