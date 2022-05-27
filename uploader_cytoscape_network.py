import csv
import json
import os
from io import StringIO

from engineio.payload import Payload
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from GlobalData import *
from PIL import Image


def makeProjectFolders(name):
    path = "static/projects/" + name
    pfile = {}
    pfile["name"] = name
    pfile["layouts"] = []
    pfile["layoutsRGB"] = []
    pfile["links"] = []
    pfile["linksRGB"] = []
    pfile["selections"] = []

    try:
        os.mkdir(path)
        os.mkdir(path + "/layouts")
        os.mkdir(path + "/layoutsl")
        os.mkdir(path + "/layoutsRGB")
        os.mkdir(path + "/links")
        os.mkdir(path + "/linksRGB")

        with open(path + "/pfile.json", "w") as outfile:
            json.dump(pfile, outfile)

    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


def loadProjectInfo(name):
    folder = "static/projects/" + name + "/"
    layoutfolder = folder + "layouts"
    layoutRGBfolder = folder + "layoutsRGB"
    linksRGBfolder = folder + "linksRGB"
    linkfolder = folder + "links"

    if os.path.exists(folder):

        layouts = [name for name in os.listdir(layoutfolder)]
        layoutsRGB = [name for name in os.listdir(layoutRGBfolder)]
        links = [name for name in os.listdir(linkfolder)]
        linksRGB = [name for name in os.listdir(linksRGBfolder)]

        return jsonify(
            layouts=layouts, layoutsRGB=layoutsRGB, links=links, linksRGB=linksRGB
        )
    else:
        return "no such project"


def loadAnnotations(name):
    namefile = "static/projects/" + name + "/names.json"
    f = open(namefile)
    data = json.load(f)
    return data


def listProjects():
    folder = "static/projects"
    sub_folders = [
        name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))
    ]
    print(sub_folders)
    return sub_folders


def makeNodeTex(project, name, nodes):

    elem = len(nodes)
    hight = 128 * (int(elem / 16384) + 1)

    print("hight is " + str(hight))
    size = 128 * hight
    path = "static/projects/" + project

    texh = [(0, 0, 0)] * size
    texl = [(0, 0, 0)] * size
    texc = [(0, 0, 0, 0)] * size

    new_imgh = Image.new("RGB", (128, hight))
    new_imgl = Image.new("RGB", (128, hight))
    new_imgc = Image.new("RGBA", (128, hight))
    attrlist = {}
    attrlist["names"] = []
    for elem in nodes:
        position = elem["pos"]
        attrlist["names"] = elem["uniprotid"]
        coords = [0, 0, 0]  # x,y,z
        color = [255, 0, 0, 255]  # r,g,b

        for i, _ in enumerate(position):
            coords[i] = int(float(position[i]) * 65280)
            # channels[i] = int(float()) # TODO deside on color
        high = [value // 255 for value in coords]
        low = [value % 255 for value in coords]

        texh[i] = tuple(high)
        texl[i] = tuple(low)
        texc[i] = tuple(color)

    new_imgh.putdata(texh)
    new_imgl.putdata(texl)
    new_imgc.putdata(texc)

    with open(path + "/names.json", "w") as outfile:
        json.dump(attrlist, outfile)
    pathXYZ = path + "/layouts/" + name + "XYZ.bmp"
    pathXYZl = path + "/layoutsl/" + name + "XYZl.bmp"
    pathRGB = path + "/layoutsRGB/" + name + "RGB.png"

    if os.path.exists(pathXYZ):
        return (
            '<a style="color:red;">ERROR </a>' + name + " Nodelist already in project"
        )
    else:
        new_imgh.save(pathXYZ)
        new_imgl.save(pathXYZl)
        new_imgc.save(pathRGB, "PNG")
        return '<a style="color:green;">SUCCESS </a>' + name + " Node Textures Created"


def makeLinkTex(project, name, edges, nodes):

    # elem = len(edges)
    hight = 512  # int(elem / 512)+1
    path = "static/projects/" + project

    texl = [(0, 0, 0)] * 1024 * hight
    texc = [(0, 0, 0, 0)] * 512 * hight
    new_imgl = Image.new("RGB", (1024, hight))
    new_imgc = Image.new("RGBA", (512, hight))
    node_ids = {}
    for i, node in enumerate(nodes):
        node_ids[node] = i
    i = 0
    for edge in edges:
        source = node_ids[edge["source"]]
        target = node_ids(edge["target"])
        sx = int(source) % 128
        syl = int(int(source) / 128) % 128
        syh = int(int(source) / 16384)

        ex = int(target) % 128
        eyl = int(int(target) / 128) % 128
        eyh = int(int(target) / 16384)
        # TODO Add Color if wished
        r = 0
        g = 100
        b = 255
        a = 90

        pixell1 = (sx, syl, syh)
        pixell2 = (ex, eyl, eyh)
        pixelc = (r, g, b, a)

        if i >= 262144:
            break

        texl[i * 2] = pixell1
        texl[i * 2 + 1] = pixell2
        texc[i] = pixelc

        i += 1

    new_imgl.putdata(texl)
    new_imgc.putdata(texc)
    pathl = path + "/links/" + name + "XYZ.bmp"
    pathRGB = path + "/linksRGB/" + name + "RGB.png"

    if os.path.exists(pathl):
        return (
            '<a style="color:red;">ERROR </a>' + name + " linklist already in project"
        )
    else:
        new_imgl.save(pathl, "PNG")
        new_imgc.save(pathRGB, "PNG")
        return '<a style="color:green;">SUCCESS </a>' + name + " Link Textures Created"


def upload_files(request):
    # print("namespace", request.args.get("namespace"))
    form = request.form.to_dict()
    # print(request.files)
    # print(form)
    prolist = listProjects()
    namespace = ""
    if form["namespace"] == "New":
        namespace = form["new_name"]

    else:
        namespace = form["existing_namespace"]
    if not namespace:
        return "namespace fail"

    # GET LAYOUT

    if namespace in prolist:
        print("project exists")
    else:
        # Make Folders
        makeProjectFolders(namespace)

    folder = "static/projects/" + namespace + "/"
    pfile = {}

    with open(folder + "pfile.json", "r") as json_file:
        pfile = json.load(json_file)
    json_file.close()

    state = ""
    layout_files = request.files.getlist("layouts")

    if len(layout_files) > 0 and len(layout_files[0].filename) > 0:
        print("loading layouts", len(layout_files))
        print(layout_files[0])
        for file in layout_files:
            # TODO: fix the below line to account for dots in filenames
            name = file.filename.split(".")[0]
            contents = file.read().decode("utf-8")
            state = state + " <br>" + makeNodeTex(namespace, name, contents)
            pfile["layouts"].append(name + "XYZ")
            pfile["layoutsRGB"].append(name + "RGB")

            # print(contents)
            # x = validate_layout(contents.split("\n"))
            # print("layout errors are", x)
            # if x[1] == 0:

        # Upload.upload_layouts(namespace, layout_files)

    # GET EDGES
    edge_files = request.files.getlist("links")
    if len(edge_files) > 0 and len(edge_files[0].filename) > 0:
        print("loading links", len(edge_files))
        # Upload.upload_edges(namespace, edge_files)
        for file in edge_files:
            name = file.filename.split(".")[0]
            contents = file.read().decode("utf-8")
            pfile["links"].append(name + "XYZ")
            pfile["linksRGB"].append(name + "RGB")
            state = state + " <br>" + makeLinkTex(namespace, name, contents)

    # update the projects file
    with open(folder + "pfile.json", "w") as json_file:
        json.dump(pfile, json_file)

    global sessionData
    sessionData["proj"] = listProjects()

    return state


sessionData["proj"] = listProjects()
