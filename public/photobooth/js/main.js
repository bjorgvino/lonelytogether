console.log('Starting photo booth');
$('#photobooth').photobooth().on('image', function(event, dataUrl){
  $('#gallery').append('<img src="' + dataUrl + '" >');
});