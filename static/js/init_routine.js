var uid = makeid(10);
var elements = {
  layouts: "dropdown",
  nodecolors: "dropdown",
  links: "dropdown",
  linkcolors: "dropdown",
  "slider-node_size": "slider",
  "slider-link_size": "slider",
  "slider-link_transparency": "slider",
  "slider-label_scale": "slider",
  main_tab: "tab",
};
function initElements(elem) {
  socket.emit("init", { uid: uid, ids: elem });
}
function initProject() {
  socket.emit("init", { uid: uid, ids: ["projects"] });
}
$(document).ready(function () {
  socket.on("init", function (data) {
    console.log("Init: " + JSON.stringify(data));
    ids = data.ids;
    console.log("ids: " + JSON.stringify(ids));
    if (data.uid != uid) {
      return;
    }
    Object.keys(ids).forEach(function (id) {
      val = ids[id];
      console.log("Updating: " + id + " with " + val);
      is_null = false;
      if (val == undefined) {
        val = 0;
        is_null = true;
      }
      if (id == "projects") {
        console.log("Updating Projects:" + id + " with " + val);
        console.log($("#" + id));
        $("#" + id).val(val);
        refreshWithoutEmit(id);
        message = { id: id, fn: "sel", opt: val };
        console.log(message);
        ue4("sel", message);
        initElements(["main_tab"]);
        setTimeout(function () {
          initElements(Object.keys(elements).slice(0, -1));
        }, 3000);
        return;
      }
      switch (elements[id]) {
        case "dropdown":
          console.log("Updating dropdown: " + id + " with " + val);
          $("#" + id).val(val);
          refreshWithoutEmit(id);
          message = { id: id, fn: "sel", opt: val };
          console.log(message);
          ue4("sel", message);
          break;
        case "slider":
          console.log("Updating Slider: " + id + " with " + val);
          if (is_null) {
            val = $("#" + id).slider("option", "middle");
          }
          $("#" + id).slider("value", val);
          message = { id: id, fn: "slider", val: val };
          ue4("slider", message);
          break;
        case "tab":
          console.log("Updating Tab: " + id + " with " + val);
          $("#tabs").tabs("option", "active", val);
          break;
      }
    });
  });
  socket.on("status", function (data) {
    console.log(data);
    if (data.uid == uid) {
      initProject();
    }
  });
});
