from bs4 import BeautifulSoup
import re 
from pprint import pprint
import csv

def get_collab_modules_sections(raw_html, save_dir):
    soup = BeautifulSoup(raw_html, features="lxml")
    grps = soup.findAll("span", class_="Mrphs-toolsNav__menuitem--title", text=re.compile(r'^Module.*'))

    gottem = []
    for g in grps:
        mod_items = g.find_parent('li')
        mod_items = mod_items.findAll("li")
        for mi in mod_items:
            gottem.append({'par': g.text, 'child': mi.text})

    keys = gottem[0].keys()
    with open(save_dir, 'w', newline='', encoding="latin-1")  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(gottem)

if __name__ == "__main__":
    src_html = r"D:\UVA\UVACollab _ DS 6014 F20 _ Overview.html"
    save_here = src_html.replace(" ", "_").replace(".html", ".csv")
    with open(src_html, "r", encoding="latin-1") as f:
        raw_html = f.read()
    get_collab_modules_sections(raw_html,save_here)