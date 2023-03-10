import json

from project import Project

idata = {"mes": "dfhdfhfh", "usr": "NaS7QA89nxLg9nKQAAAn", "tag": "flask"}

scb1Data = [
    {"msg": "TMP", "id": "#button1"},
    {"msg": "MMU", "id": "#button2"},
    {"msg": "PAM", "id": "#button3"},
    {"msg": "CHR", "id": "#button3"},
    {"msg": "OMG", "id": "#button3"},
    {"msg": "WTF", "id": "#button3"},
    {"msg": "HH2H", "id": "#button3"},
    {"msg": "ASS1", "id": "#button3"},
]
pairs = [("a", "1"), ("b", "2"), ("c", "3")]
sliders = [("ddfd", "1"), ("bfsd", "2"), ("cdfsdf", "3")]

# prolist = json.dumps(listProjects())
sessionData = {
    "proj": ["ere", "rrr"],
    "actPro": "dummy",
    "connectedUsers": [],
    "selected": [10, 50, 30, 59, 60, 20, 12, 45],
    "selections": {},
}


pfile = {}
names = {}


def save_pfile(pfile):
    project = pfile.get("project")
    if project is None:
        return
    project = Project(project, read=False)
    project.pfile = pfile
    project.write_pfile()
