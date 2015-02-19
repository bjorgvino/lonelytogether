var api = '/api/';
var imageFolder = '/uploads/';
var $photogrid = $('#photogrid');
var lastId = 0;
var maxCount = 2000;

$(function () {
  sizeHeader();

  // Initialize the masonry plugin
  $photogrid.masonry({
    itemSelector: '#photogrid li'
  });

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
  $.ajax({
    method: 'get',
    dataType: 'json',
    url: api + 'getfeed',
    data: { count: maxCount, lastId: lastId },
  })
  .done(function(data) {
    if (data && data.length > 0) {
      renderImages(data);
      lastId = data[0].id;
    }
  })
  .fail(function(jqXHR, textStatus, error) {
    if (typeof(window.console) !== "undefined") {
      console.log("Status: ", error.status);
      console.log("Response: ", error.responseText);
    }
  })
  .always(function() {
    // Schedule next poll
    setTimeout(fetchImages, 10000);
  });
}

function renderImages(data) {
  var elements = [];
  var count = 0;
  for (var i in data) {
    var imgSrc = imageFolder + data[i].source + '_images/' + data[i].image_filename;
    var imgAlt = data[i].left_username + ' and ' + data[i].right_username;
    var element = document.createElement('li');
    element.innerHTML = '<a href="/entry/' + data[i].id + '"><img src="' + imgSrc + '" alt="' + imgAlt + '" /></a>';
    if (count++ % 5  == 1) {
      element.className = 'double';
    }
    elements.push(element);
  }

  $photogrid.prepend(elements).imagesLoaded(function () {
    $photogrid.masonry('prepended', elements);
  });
}
