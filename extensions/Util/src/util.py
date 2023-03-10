import json
import os
import random
import shutil
import time
import traceback
import multiprocessing as mp

import GlobalData as GD
import pandas as pd
from project import PROJECTS_DIR, Project, COLOR, NODE, LINK

from . import const, highlight
import numpy as np
from PIL import Image

MAX_ANNOT = 50


def highlight_selected_node_links(message):

    mode = message.get("mode", "highlight")
    layout = message.get("layout")
    layout_rgb = message.get("nodecolors")
    linkl = message.get("links")
    link_rgb = message.get("linkcolors")
    tab = message.get("main_tab")

    node_color = message.get("node_color")
    if node_color:
        node_color = hex_to_rgb(node_color)
    link_color = message.get("link_color")
    if link_color:
        link_color = hex_to_rgb(link_color)
    project = Project(GD.sessionData["actPro"])
    project.pfile = GD.pfile
    state_data = project.pfile.get("stateData")
    if state_data is None:
        return
    selected = state_data.get("selected")

    selected_links = state_data.get("selectedLinks")

    # selected = random.choices(range(16421), k=100)
    if selected is not None:
        selected = [int(i) for i in selected]

    if layout is None:
        layout = project.get_all_layouts()[0]
    if layout_rgb is None:
        layout_rgb = project.get_all_node_colors()[0]
    if linkl is None:
        linkl = project.get_all_links()[0]
    if link_rgb is None:
        link_rgb = project.get_all_link_colors()[0]
    if project.origin:
        project = Project(project.origin)

    process = Project("process", read=False)
    process.pfile = GD.pfile
    if "stateData" not in process.pfile:
        process.pfile["stateData"] = {}
    for key, layout_list in zip(
        ["layouts", "nodecolors", "links", "linkcolors"],
        ["layouts", "layoutsRGB", "links", "linksRGB"],
    ):
        if key not in process.pfile["stateData"]:
            process.pfile["stateData"][key] = project.pfile[layout_list][0]
    process.pfile["stateData"]["main_tab"] = tab
    process.set_pfile_value("origin", project.name)

    if process.exists():
        process.remove()

    ignore = shutil.ignore_patterns(
        "names.json", "nodes.json", "links.json", "annotations.json"
    )
    project.copy(process.location, ignore=ignore)
    process.set_pfile_value("name", "tmp")
    process.write_pfile()

    nodes_args = (
        process,
        selected,
    )
    links_args = (
        process,
        selected_links,
        selected,
        mode,
    )

    if selected is None or len(selected) == 0:
        selected = highlight.mask_links(*links_args)
        nodes_args = (
            nodes_args[0],
            selected,
        )
        nodes = highlight.mask_nodes(*nodes_args)
    else:
        nodes = mp.Process(
            target=highlight.mask_nodes,
            args=nodes_args,
        )
        links = mp.Process(
            target=highlight.mask_links,
            args=links_args,
        )

        for proc in [nodes, links]:
            proc.start()
        for proc in [nodes, links]:
            proc.join()
    jobs = []
    for node_lay in process.get_all_node_colors():
        jobs.append(
            (
                process.name,
                node_lay,
                NODE,
                COLOR,
            )
        )
    for link_lay in process.get_all_link_colors():
        jobs.append(
            (
                process.name,
                link_lay,
                LINK,
                COLOR,
            )
        )
    n = len(jobs)
    if n > os.cpu_count() - 1:
        n = os.cpu_count() - 1
    with mp.Pool(n) as p:
        p.starmap(highlight.apply_mask, jobs)
    p.close()
    p.join()
    tmp = Project("tmp", read=False)
    for data_type in [NODE, LINK]:
        process.delete_bitmap("mask", data_type, COLOR)
    if tmp.exists():
        tmp.remove()
    process.copy(tmp.location)
    process.remove()


def select_nodes(message):
    proj = GD.sessionData["actPro"]
    proj = Project(proj)
    proj.read_nodes()
    nodes = pd.DataFrame(proj.nodes["nodes"])
    dtype = message.get("dtype")
    annotation = message.get("annotation")
    value = message.get("value")
    if dtype in ["float", "int"]:
        operator = message["operator"]
        if operator == 0:
            nodes = nodes[nodes[annotation] <= value]
        elif operator == 1:
            nodes = nodes[nodes[annotation] == value]
        elif operator == 2:
            nodes = nodes[nodes[annotation] >= value]
    elif dtype in ["object", "category", "bool"]:
        if isinstance(value, str):
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False

        nodes = nodes[nodes[annotation] == value]

    elif dtype in ["str"]:
        if value.endswith("..."):
            value = value[:-3]
        check = nodes[annotation].copy()
        check = check.fillna("")
        nodes = check.where(check.str.startswith(value)).dropna()
    GD.sessionData["selected"] = nodes.index.tolist()
    return GD.sessionData["selected"]


def select_links(message):
    proj = GD.sessionData["actPro"]
    proj = Project(proj)
    proj.read_links()
    links = pd.DataFrame(proj.links["links"])
    dtype = message["dtype"]
    annotation = message["annotation"]
    value = message["value"]
    if dtype in ["float", "int"]:
        operator = message["operator"]
        if operator == 0:
            links = links[links[annotation] <= value]
        elif operator == 1:
            links = links[links[annotation] == value]
        elif operator == 2:
            links = links[links[annotation] >= value]
    elif dtype in ["object", "bool"]:
        links = links[links[annotation] == value]
    GD.sessionData["selected_links"] = links.index.tolist()
    return GD.sessionData["selected_links"]


def process_annotation(message, return_dict):
    project = message["project"]
    project = Project(project)
    annotation_type = message["type"]
    project.read_nodes()
    if annotation_type == "node":
        df = pd.DataFrame(project.nodes["nodes"])
    if annotation_type == "link":
        project.read_links()
        df = pd.DataFrame(project.links["links"])
        names = pd.DataFrame(project.nodes["nodes"])[const.NAME_COL]
    dtypes = df.dtypes.astype(str).to_dict()
    for col in const.IGNORE_COLS:
        if col in df.columns:
            df = df.drop(columns=col)
    lengths = {}
    # print(project.name, annotation_type, len(df.columns))

    def extract_annot(col, dtypes, names=None):
        name = str(col.name)
        dtype = dtypes[name]
        annot = {"dtype": dtype}
        if name in [const.START_COL, const.END_COL]:
            annot["dtype"] = "int"
            annot["min"] = 0
            annot["max"] = len(names) - 1
            annot["values"] = names.tolist()
        elif name == const.NAME_COL and annotation_type == "node":
            annot["dtype"] = "int"
            annot["min"] = 0
            annot["max"] = len(col) - 1
            annot["values"] = col.tolist()
        elif pd.api.types.is_integer_dtype(dtype):
            annot["min"] = int(col.min())
            annot["max"] = int(col.max())
            annot["dtype"] = "int"
            if annot["min"] == annot["max"]:
                return
        elif pd.api.types.is_float_dtype(dtype):
            annot["min"] = float(col.min())
            annot["max"] = float(col.max())
            if annot["min"] == annot["max"]:
                return
            annot["dtype"] = "float"
        elif pd.api.types.is_string_dtype(dtype):
            # TODO: check if there is a better way to do this maybe creating a new series of every new value and make it true if this value is in the row
            class SetCounter:
                def __init__(self):
                    self.set = set()
                    self.counter = {}

                def add(self, value):
                    self.set.add(value)

                def add_value(self, value):
                    if isinstance(value, str) and len(value) > 20:
                        value = value[:20] + "..."
                    value = str(value)
                    self.add(value)
                    if value not in self.counter:
                        self.counter[value] = 0
                    self.counter[value] += 1

            options = SetCounter()

            def collect_values(x, options: SetCounter):
                if isinstance(x, str):
                    options.add_value(x)
                if pd.api.types.is_list_like(x):
                    for val in x:
                        if pd.isna(val):
                            continue
                        options.add_value(val)

            for i, row in col.iteritems():
                if pd.api.types.is_list_like(row):
                    return
            col.swifter.progress_bar(False).apply(collect_values, args=(options,))
            for k, v in options.counter.items():
                if v <= 1:
                    options.set.remove(k)
            if len(options.set) < 2:
                for k, v in options.counter.items():
                    if v <= 1:
                        if k in options.set:
                            options.set.remove(k)
            if len(options.set) == len(col):
                return
            options.set = sorted(
                options.set, key=lambda x: options.counter[x], reverse=True
            )
            if len(options.set) > MAX_ANNOT:
                options.set = options.set[:MAX_ANNOT]
            if len(options.set) == 0:
                return
            if len(options.set) > 3:
                annot["dtype"] = "str"
            else:
                annot["dtype"] = "category"
            annot["options"] = list(options.set)
        elif dtype == "object":
            return
        elif dtype == "bool":
            annot["dtype"] = "bool"
            annot["options"] = [True, False]
        else:
            print("not implemented dtype:", name, dtype)
            return
        return annot

    if annotation_type == "link":
        annotations = df.swifter.progress_bar(False).apply(
            extract_annot, args=(dtypes, names)
        )
    else:
        annotations = df.swifter.progress_bar(False).apply(
            extract_annot, args=(dtypes, None)
        )

    if annotations.empty:
        return
    if isinstance(annotations, pd.Series):
        annotations = pd.DataFrame(annotations.to_dict())
    annotations = annotations.dropna(how="all", axis=1)
    annotations_transposed = annotations.T
    option_annots = annotations_transposed[annotations_transposed["dtype"] == "str"]

    # limit the number of annotations to 20 to reduce traffic
    if len(annotations) + len(option_annots) > MAX_ANNOT and not option_annots.empty:
        print("=====================================")
        print("TO MANY ANNOTATIONS", len(annotations), len(option_annots), MAX_ANNOT)
        print("=====================================")
        annotations = annotations.drop(columns=option_annots.index)
        space = MAX_ANNOT - len(annotations)
        lengths = option_annots.apply(lambda x: len(x["options"]), axis=1)
        lengths = lengths.sort_values(ascending=True)
        option_annots = option_annots.loc[lengths.index[:space]].T
        annotations = pd.concat([annotations, option_annots], axis=1)
        # if project.name == "string_ecoli_ppi":
        #     if "zinc ion binding:GO:0008270" in option_annots:
        #         print(option_annots["zinc ion binding:GO:0008270"])
        # print("=" * 20)
        # print(
        #     project.name,
        #     annotation_type,
        # )
        # print(annotations)
        # print("=" * 20)
    # Fill nan values with None to filter them out
    annotations = annotations.where(pd.notnull(annotations), None)
    annotations = {
        k: {k1: v1 for k1, v1 in v.items() if v1 is not None}
        for k, v in annotations.to_dict().items()
    }

    return_dict["annotations"] = annotations
    return annotations


def get_selection(message):
    print("Handling selection request:", message)
    if message["type"] == "node":
        if message["annotation"] in [const.NAME_COL, const.SUID_COL]:
            message["dtype"] = "object"
        selection = select_nodes(message)
        GD.pfile["stateData"]["node_annotation"] = message["annotation"]
        GD.pfile["stateData"]["selected"] = selection
    elif message["type"] == "link":
        if message["annotation"] in [const.START_COL, const.END_COL, const.ID_COL]:
            message["dtype"] = "object"
        selection = select_links(message)
        GD.pfile["stateData"]["link_annotation"] = message["annotation"]
        GD.pfile["stateData"]["selectedLinks"] = selection

    message["data"] = "selection"
    message["selection"] = selection
    message["type"] = message["type"]
    return message


def highlight_func(message):
    mode = message.get("mode", "highlight")
    if mode == "store":
        response = store_highlight(message)
    else:
        selected = GD.pfile.get("stateData", {}).get("selected")
        selectedLinks = GD.pfile.get("stateData", {}).get("selectedLinks")
        if selected is None and selectedLinks is None:
            response = {"status": "error", "message": "No nodes or links selected!"}
            message.update(response)
            return message
        try:
            highlight_selected_node_links(message)
            response = {
                "message": "Selection highlighted!",
                "status": "success",
                "set_project": True,
            }
        except Exception as e:
            print(traceback.format_exc(e))
            response = {"message": str(e), "status": "error"}
    message.update(response)
    return message


def store_highlight(message):
    project = GD.sessionData["actPro"]
    project = Project(project)
    origin = project.get_pfile_value("origin")
    if not origin:
        message = {
            "message": "Nothing highlighted!",
            "status": "error",
            "set_project": False,
        }
        return message
    project = Project(origin)
    new_name = project.name + "_highlight"
    i = 1
    if new_name in GD.sessionData["proj"]:
        while True:
            if new_name + str(i) not in GD.sessionData["proj"]:
                new_name += str(i)
                break
            i += 1
    project.copy(os.path.join(PROJECTS_DIR, new_name), ignore=True)
    highlight = Project(new_name)
    highlight.pfile = GD.pfile
    GD.sessionData["proj"].append(new_name)

    highlight.set_pfile_value("origin", origin)

    stateData = highlight.pfile.get("stateData", {})
    stateData["main_tab"] = message["main_tab"]
    highlight.set_pfile_value("stateData", stateData)
    highlight.write_pfile()
    message = {
        "message": f"Highlighting store as {new_name}",
        "status": "success",
        "projectName": new_name,
    }
    return message


def hex_to_rgb(hex):
    return tuple(int(hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
