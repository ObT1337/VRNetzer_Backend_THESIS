# VRNetzer Backend

This is a flask server that provides the network data to the UnrealEngine VRNetzer VR Clients

## INSTALLATION

1. run backend

   - install python 3.9 plus
   - windows: run `Buildandrun.ps` in console
   - linux: run `linux_buildandrun.sh` in console
   - mac: run `linux_buildandrun.sh` in console

   If all dependencies installed correctly, the console should show </br>
   `The server is now running at 127.0.0.1:5000`

   As on mac port 5000 is already occupied by the systems control center, on mac the server will run on port 3000 (instead of 5000).

2. upload data and create new project

   - open a browser (Chrome or Firefox) and go to [127.0.0.1:5000/upload](http://127.0.0.1:5000/upload) / [127.0.0.1:3000/upload](http://127.0.0.1:3000/upload)(mac)
   - make sure "create new project" is checked and assign a name
   - choose a layout file from "static/csv" (or more) or use your own
   - pick a link file from "static/csv" (same name as above) or use your own
   - click upload

   After a success message was shown, the uploader has now created a new folder in "static/projects/yourprojectname" containing all the data in the VRNetzer format.

3. use the WebGL preview to have a look at your project without having to use VR hardware

   - go to [127.0.0.1:5000/preview](http://127.0.0.1:5000/preview) / [127.0.0.1:3000/upload](http://127.0.0.1:3000/upload)(mac)
   - select your project from the dropdown

4. run the VR
   you need:
   - a VR ready windows computer
   - a SteamVR compatible headset
   - SteamVR installed
   - download the VRNetzer executable
   - open "VRNetzer/Colab/Content/data/config.txt and make sure it contains the adress the VRNetzer backend is running at
   - run VRnetzer.exe

## DOCUMENTATION

<details>
  <summary><h3> VRNetzer Dataformat</h3></summary>
    
The VRNetzer acts as a multiplayer gameserver for one or more VR clients.
Its purpose is to serve the connected players with big network datasets - as quickly as possible.
That is the reason why most properties are stored (and transmitted over the network) as images.

Every folder in "static/projects/ contains 3 JSON files (check out the file dataframeTemplate.json for the exact structure)
as well as 5 subfolders containing textures

- static/projects/projectname/
  - nodes.json
  - links.json
  - pfile.json
  - layouts
  - layoutsl
  - layoutsRGB
  - links
  - linksRGB

layouts + layoutsl -> Node Positions

this needs a little explaining:
Think as a texture as a dataset of the following format: [[R,G,B],[R,G,B],[R,G,B],..] where every [R,G,B] is a pixel.
This can be used to store a location (X->R Y->G Z->B) per pixel.
Because a .bmp only has 8 bit depth we need a second texture to get a resolution of 65536 per axis. this is where "layoutsl" comes into play.
NOTE: node positions need to be in a 0 - 1 range (!), the conversion works like this:

floor(x _ 256) -> layouts
floor(x _ 65536 % 256) -> layoutsl

| Column 1 Header | Column 2 Header | Column 3 Header |
| --------------- | --------------- | --------------- |
| Row 1 Column 1  | Row 1 Column 2  | Row 1 Column 3  |
| Row 2 Column 1  | Row 2 Column 2  | Row 2 Column 3  |
| Row 3 Column 1  | Row 3 Column 2  | Row 3 Column 3  |

</details>

<details>
<summary><h3>HOW TO MAKE YOUR OWN USER INTERFACE</h3></summary>
The User Interfaces for the VRNetzer are realized with html and js and are rendered in the UnrealEngine in-game webbrowser, which is Chromium. Data is passed between the flask server and the html clients in JSON format. The html pages also act as a middleman between the UnrealEngine VR Module and the flask server.
Here is a series of examples that explain in detail how to create your own user interfaces.
(you have to run the flask server locally to see those pages)

- a flask route, some JSON
- socketIO, multicasting basic UI elements
- custom elements 1, using html templates
- custom elements 2, using D3js graphs
- server side variable
</details>