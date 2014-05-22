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
      data: { count: 20, lastId: lastId },
      //success: success
    })).then(function(data){
      if (data && data.length > 0){
        lastId = data[0].id;
        renderImages(data);
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
      if (i % 6 == 0){
        $photogrid.append('<div class="row"></div>');
      }
      $photogrid.find('div.row:last').append('<div class="col-sm-2"><img src="'+imageFolder+data[i].image_filename+'" alt="" /></div>');
    }
    console.log('Done with images');
  }
});

$(window).resize(function() {
	sizeHeader();
})

function sizeHeader($container, $logo) {
	var $container = $('#logo'),
		$logo = $container.find('img'),
		viewportheight = $(window).height();

	$container.css('height', viewportheight).css('padding-top', (viewportheight - $logo.height()) / 2);
}
