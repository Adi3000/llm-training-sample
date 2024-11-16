import csv
import os
import re
import json

class Dialog:
    def __init__(self, name: str, text: str):
        self.name = name
        self.text = text
            
class Quest:
    def __init__(self, chapter: str, 
                 region: str, 
                 file: str, 
                 quest_id: str, 
                 quest_name: str, 
                 abstract: str, 
                 dialogs: list[Dialog]):
        self.quest_id = quest_id
        self.chapter = chapter
        self.region = region
        self.file = file
        self.quest_name = quest_name
        self.abstract = abstract
        self.dialogs = dialogs
    def to_dict(self):
        return {
            "chapter": self.chapter,
            "quest_id": self.quest_id,
            "region": self.region,
            "file": self.file,
            "quest_name": self.quest_name,
            "abstract": self.abstract,
            "dialogs": [ dialog.__dict__ for dialog in self.dialogs ]
        }
        
SUBJECT = "Willy et Coton"
gender_replacement1 = r"<If\(PlayerParameter\(4\)\)>.*<Else/>(.*?)</If>"
gender_replacement2 = r"<If\(PlayerParameter\(4\)\)>.*(.*?)</If>"
subject_replacement = r"<Split(<Highlight>ObjectParameter(1)</Highlight>, ,1)/>"
daytime_replacement = r"<If\(LessThan\(PlayerParameter\(11\),12\)\)><If\(LessThan\(PlayerParameter\(11\),4\)\)>.*<Else/>(.*?)</If><Else/><If\(LessThan\(PlayerParameter\(11\),17\)\)>.*<Else/>.*</If></If>"
object_replacement = r"<If\(<Sheet\(.*,.*,.*\)/>\)>(.*?)<Else/>(.*?)</If>"
folder = "/mnt/g/Utils/SaintCoinach/2024.08.21.0000.0000"
        
def find_quest_file(name: str):
    root_quest_folder = os.path.join(folder, "exd", "quest")
    filename= f"{name}.csv"
    for subfolder in os.listdir(root_quest_folder):
        quest_folder = os.path.join(root_quest_folder, subfolder)
        if os.path.isdir(quest_folder):
            for quest_file in os.listdir(quest_folder):
                if quest_file == filename:
                    return os.path.join(quest_folder, quest_file)

               
def parse_quest_file(quest_filename: str, quest_id: str, chapter: str, region: str, quest_name: str):
    dialogs = []
    abstract = ""
    with open( quest_filename, mode="r") as quest_file:
        quest_csv = csv.reader(quest_file)
        for quest_details in quest_csv:
            if quest_details[2]:
                text = parse_text(quest_details[2])
                if "SEQ" in quest_details[1]:
                    abstract += f"{text}\n"
                elif "TODO" in quest_details[1]:
                    abstract += f"* Vous devez {text}.\n"
                elif "TEXT" in quest_details[1]:
                    dialog_id = quest_details[1].split("_")
                    speaker = dialog_id[3] if not dialog_id[3].isdigit() else dialog_id[4]
                    dialog = Dialog(speaker, text)
                    dialogs += [dialog]
        quest = Quest(chapter, region, quest_filename, quest_id, quest_name, abstract, dialogs)
        return quest

def parse_text(text: str):
    text = text.replace("<SoftHyphen/>","-")
    text = text.replace("<Hyphen/>","-")
    text = text.replace("<Indent/>"," ")
    text = text.replace("<Emphasis>"," ")
    text = text.replace("</Emphasis>"," ")
    text = re.sub(gender_replacement1, r"\1", text)
    text = re.sub(gender_replacement2, r"\1", text)
    text = re.sub(daytime_replacement, r"\1", text)
    text = re.sub(object_replacement, r"\1\\u00B7\2", text)
    text = text.replace(subject_replacement, SUBJECT)
    return text

with open( f"{folder}/exd/Quest.csv", mode="r") as quests_file:
    quests_csv = csv.reader(quests_file)
    dataset = []
    for quest in quests_csv:
        quest_file = find_quest_file(quest[2])
        if quest_file:
            quest = parse_quest_file(quest_file, quest[2], quest[1515], quest[1514], quest_name=quest[1] )
            print (f"=={quest.quest_id}== {quest.quest_name} [{quest.chapter}/{quest.region}]  ({quest.file}) ")
            dataset += [quest.to_dict()]         

    sorted_dataset = sorted(dataset, key=lambda item: item["quest_id"] )
    with open("../data/dataset.json", "w") as json_file:
        json.dump(dataset, json_file, indent=4)