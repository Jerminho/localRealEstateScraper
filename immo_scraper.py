import os
import time
import webbrowser
import requests
from bs4 import BeautifulSoup

# Regio instellingen (Postcode: Naam)
REGIONS = {
    "7700": "Moeskroen / Mouscron",
    "7730": "Estaimpuis",
    "7740": "Pecq",
    "8500": "Kortrijk",
    "8790": "Waregem"
}

# Tweetalige keywords voor achterstallig onderhoud
KEYWORDS = [
    "op te frissen", "renovatie", "opfrisbeurt", "kluswoning", "koer", "tuin",
    "à rafraîchir", "renovation", "rénover", "travaux", "jardin", "cour"
]

def scrape_zimmo():
    leads = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("🚀 Scraper gestart voor regio Moeskroen - Kortrijk - Waregem...")

    for postcode, region_name in REGIONS.items():
        print(f"🔍 Zoeken in {postcode} ({region_name})...")
        url = f"https://zimmo.be{postcode}/te-koop/panden/"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Kon {postcode} niet laden (Status: {response.status_code})")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            # Let op: class_ namen kunnen wijzigen per website-update. 
            # 'property-item' is momenteel de standaard container op Zimmo.
            panden = soup.find_all('div', class_='property-item') 
            
            for pand in panden:
                title_el = pand.find('h3', class_='property-item_title')
                desc_el = pand.find('p', class_='property-item_description')
                link_el = pand.find('a', href=True)
                price_el = pand.find('span', class_='property-item_price')
                
                title = title_el.text.strip() if title_el else "Geen titel"
                desc = desc_el.text.strip() if desc_el else ""
                price = price_el.text.strip() if price_el else "Prijs op aanvraag"
                link = "https://zimmo.be" + link_el['href'] if link_el else "#"
                
                # Check op keywords
                combined_text = (title + " " + desc).lower()
                if any(kw in combined_text for kw in KEYWORDS):
                    leads.append({
                        "postcode": postcode,
                        "regio": region_name,
                        "titel": title,
                        "beschrijving": desc[:150] + "...",
                        "prijs": price,
                        "link": link
                    })
            
            time.sleep(2) # Voorkom IP-blokkades
            
        except Exception as e:
            print(f"❌ Fout in {postcode}: {e}")
            
    return leads

def generate_dashboard(leads):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="nl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Immo Klus Leads Dashboard</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }}
            .container {{ max-width: 1000px; margin: auto; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            .stats {{ margin-bottom: 20px; font-weight: bold; color: #7f8c8d; }}
            .card {{ background: white; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #3498db; }}
            .card.waal {{ border-left-color: #e74c3c; }} /* Rode rand voor Waalse kant */
            .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
            .badge {{ background: #3498db; color: white; padding: 5px 10px; border-radius: 20px; font-size: 12px; }}
            .badge.waal {{ background: #e74c3c; }}
            .title {{ font-size: 18px; margin: 0; color: #2c3e50; }}
            .desc {{ color: #555; font-size: 14px; line-height: 1.5; }}
            .price {{ font-weight: bold; color: #27ae60; margin-top: 10px; }}
            .btn {{ display: inline-block; background: #2c3e50; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; font-size: 14px; margin-top: 10px; }}
            .btn:hover {{ background: #34495e; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Potentiële Schoonmaak & Onderhoudsklussen</h1>
            <div class="stats">Aantal leads gevonden: {len(leads)}</div>
    """
    
    if not leads:
        html_content += "<p>Geen panden gevonden met de geselecteerde keywords. Probeer later opnieuw of voeg keywords toe.</p>"
    else:
        for lead in leads:
            is_wallonia = lead['postcode'] in ["7700", "7730", "7740"]
            card_class = "card waal" if is_wallonia else "card"
            badge_class = "badge waal" if is_wallonia else "badge"
            
            html_content += f"""
            <div class="{card_class}">
                <div class="card-header">
                    <h2 class="title">{lead['titel']}</h2>
                    <span class="{badge_class}">{lead['regio']} ({lead['postcode']})</span>
                </div>
                <p class="desc">{lead['beschrijving']}</p>
                <div class="price">{lead['prijs']}</div>
                <a href="{lead['link']}" target="_blank" class="btn">Bekijk Pand op Zimmo ↗</a>
            </div>
            """
            
    html_content += """
        </div>
    </body>
    </html>
    """
    
    file_path = "immo_leads.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"\n✨ Dashboard succesvol gegenereerd! Openen van {file_path}...")
    webbrowser.open('file://' + os.path.realpath(file_path))

if __name__ == "__main__":
    found_leads = scrape_zimmo()
    generate_dashboard(found_leads)
