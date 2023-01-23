// SOME FUNCTIONS TO CREATE MULTICASTED (via socketIO) UI ELEEMENTS LIKE BUTTONS, DROPDOWNS, SLIDERS, CHECKBOXES

function initDropdown(id, data, active) {

  $('#' + id).selectmenu();

  for (let i = 0; i < data.length; i++) {
  $('#' + id).append(new Option(data[i]));
  }

  $('#' + id).val(active);
  $('#' + id).selectmenu("refresh");

  $('#' + id).on('selectmenuselect', function() {
    var name = $('#' + id).find(':selected').text();
    socket.emit('ex', { id: id, opt: name, fn: "sel" });
    ///logger($('#selectMode').val());
  });

}

function initMyStructureDropdown(id, data, active, message_id,gif_id) {
  $('#' + id).selectmenu();

  for (let i = 0; i < data.length; i++) {
   $('#' + id).append(new Option(data[i]));
  }

  $('#' + id).val(active);
  $('#' + id).selectmenu("refresh");

  $('#' + id).on('selectmenuselect', function() {
    var name = $('#' + id).find(':selected').text();
    var base_url = "http://" + window.location.href.split("/")[2];
    var url = base_url + "/vrprot/fetch?id=" + name;
    document.getElementById(gif_id).style.display = "block";
    $.ajax({
      type: "POST",
      url: url,
      cache: false,
      contentType: false,
      processData: false,
      success: function(data) {
        console.log(data)
        if (data["already_exists"].includes(name)) {
          $("#" + message_id).html("<h4 style=color:green;font-size:20px>Structure loaded. Turn on overwrite to reprocess it.</h4>");
        } else if (name in data["results"]) {
          $("#" + message_id).html("<h4 style=color:green;font-size:20px>Structure downloaded! </h4>");
        } else if (data["not_fetched"].includes(name)){
          $("#" + message_id).html("<h4 style=color:red;font-size:20px>Could not fetch a structure with this UniProt ID from AlphaFold DB! </h4>");
        };
        document.getElementById(gif_id).style.display = "none" ;
        socket.emit('ex', { id: id, opt: name, fn: "sel" });
        setTimeout(function() {
          $("#" + message_id).html("");
        }, 10000);

      },
      error: function(err) {
        console.log(err);
        $("#" + message_id).html("<h4 style=color:yellow;font-size:20px;>ProteinStructureFetch is not installed. Structure will be loaded, if you manually prepared it.</h4>");
        setTimeout(function() {
          $("#" + message_id).html("");
        }, 5000);
        document.getElementById(gif_id).style.display = "none" ;
        socket.emit('ex', { id: id, opt: name, fn: "sel" });
      }
    });
  });
}

/// a test to add json string as attribute to dropdown option
function initDropdownX(id, data, active) {

  $('#' + id).selectmenu();

  for (let i = 0; i < data.length; i++) {

    var addata ={id:i, size: 99, city: makeid(5)};
    
    $('<option>').val("object.val").text(data[i]).attr('data-x', JSON.stringify(addata)).appendTo('#' + id);
  }

  $('#' + id).val(active);
  $('#' + id).selectmenu("refresh");

  $('#' + id).on('selectmenuselect', function() {
    var name = $('#' + id).find(':selected').text();
    var x = $('#' + id).find(':selected').attr("data-x");
    socket.emit('ex', { id: id, opt: name, fn: "sel", data: x });
    console.log(JSON.parse(x));
  });

}


function initSlider(id) {

  $('#' + id).slider({
    animate: true,
    range: "max",
    min: 0,
    max: 255,
    value: 128,
    slide: function(event, ui) {
      socket.emit('ex', { id: id, val: ui.value, fn: "sli" });
    }
  });

}


function initCheckbox(id) {
  $('#' + id).on("click", function() {
    socket.emit('ex', { id: id, val: $('#' + id).is(":checked"), fn: "chk" });
  });

}


function initButton(id) {
  $('#' + id).on("click", function() {
    var $this = $(this);
    socket.emit('ex', { id: id, val: "clicked", fn: "but" });
  });
}








function makeid(length) {
  var result = '';
  var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  var charactersLength = characters.length;
  for (var i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() *
      charactersLength));
  }
  return result;
}
function deactivateTabs(id) {
  // Deactivate all tabs which are not contained in the html
  var tabs = document.getElementById(id);
  var items = tabs.getElementsByTagName('li');
  for (var i = 0; i < items.length; i++) {
    hyperlink = items[i].getElementsByTagName('a')[0];
    var id = hyperlink.href.split('#')[1];
    if (!(document.getElementById(id))) {
      items[i].style.display = 'none';
    } else {
      items[i].style.display = 'inline';
    }
  };
};
function setHref(id, uniprot,link) {
  var href = link.replace("<toChange>", uniprot)
  console.log(href)
  $('#' + id).attr('href', href);
}
function followLink(link) {
  var url = "http://" + window.location.href.split("/")[2];
  window.location.href= url + link;
}