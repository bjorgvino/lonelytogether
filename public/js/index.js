var api = '/api/';
var imageFolder = '/uploads/photobooth_images/';
//var api = 'http://localhost:5000/api/';
//var imageFolder = 'http://lonelytogether.bjorgv.in/uploads/photobooth_images/';
var $photogrid = $('#photogrid');
var lastId = 0;

$(function () {
	sizeHeader();
  fetchImages();

  function fetchImages(){
    console.log('Fetching images...');
    $.when($.ajax({
      method: 'get',
      dataType: 'json',
      url: api + 'getfeed',
      data: { count: 240, lastId: lastId },
      //success: success
    })).then(function(data){
      if (data && data.length > 0){
        renderImages(data);
        lastId = data[0].id;
      }
    }, function(error){
      console.log(error);
    }).done(function(){
      // Schedule next poll
      setTimeout(fetchImages, 10000);
    });
  }

  function renderImages(data){
    console.log('Fetched images: ', data);
    for (var i in data){
      var $row = $photogrid.find('div.row:first');
      var imageDiv = '<div class="col-sm-2"><img src="' + imageFolder + data[i].image_filename + '" alt="" /></div>';
      if (lastId == 0){
        // First render
        $row.append(imageDiv);
      } else {
        // Incremental render
        $row.prepend(imageDiv);
      }
    }
    console.log('Done with images');
  }

	var s = skrollr.init({
		constants: {
			logooffset: function() {
				return ($(window).height() - $('#logo img').height()) / 2;
			}
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
