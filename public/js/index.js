var api = '/api/';
var imageFolder = '/uploads/photobooth_images/';
//var api = 'http://localhost:5000/api/';
//var imageFolder = 'http://lonelytogether.bjorgv.in/uploads/photobooth_images/';
var $photogrid = $('#photogrid');
var lastId = 0;
var maxCount = 2000;

$(function () {
  sizeHeader();
  fetchImages();

  var s = skrollr.init({
    constants: {
      logooffset: function() {
        return ($(window).height() - $('#logo img').height()) / 2;
      }
    },
    mobileCheck: function() {
      return false;
    }
  });
});

$(window).resize(function() {
  sizeHeader();
})

function sizeHeader() {
  var $container = $('#logo'),
      $logo = $container.find('img'),
      viewportheight = $(window).height();

  $container.css('height', viewportheight).css('padding-top', (viewportheight - $logo.height()) / 2);
}

function fetchImages() {
  $.when(
    $.ajax({
      method: 'get',
      dataType: 'json',
      url: api + 'getfeed',
      data: { count: maxCount, lastId: lastId },
    })
  ).then(function(data) {
    if (data && data.length > 0) {
      renderImages(data);
      lastId = data[0].id;
    }
  }, function(error){
    if (typeof(window.console) !== "undefined") {
      console.log(error);
    }
  }).done(function() {
    // Schedule next poll
    setTimeout(fetchImages, 10000);
  });
}

function renderImages(data) {
  for (var i in data){
    var $row = $photogrid.find('div.row:first');
    var imageDiv = '<div class="col-sm-2"><a href="/entry/' + data[i].id + '"><img src="' + imageFolder + data[i].image_filename + '" alt="' + data[i].left_username + ' and ' + data[i].right_username + '" /></a></div>';
    if (lastId == 0){
      // First render
      $row.append(imageDiv);
    } else {
      // Incremental render
      $row.prepend(imageDiv);
    }
  }
}