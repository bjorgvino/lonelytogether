var api = '/api/';
var imageFolder = '/uploads/';
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
});

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
      console.log("Status: ", error.status);
      console.log("Response: ", error.responseText);
    }
  }).done(function() {
    // Schedule next poll
    setTimeout(fetchImages, 10000);
  });
}

function renderImages(data) {
  var imgHtml = '';

  for (var i in data) {
    imgHtml += '<li><a href="/entry/' + data[i].id + '"><img src="' + imageFolder + data[i].source + '_images/' + data[i].image_filename + '" alt="' + data[i].left_username + ' and ' + data[i].right_username + '" /></a></li>';
  }

  $photogrid.prepend(imgHtml);
}
