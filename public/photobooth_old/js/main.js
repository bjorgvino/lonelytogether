console.log('Starting photo booth');
$('#photobooth').photobooth().on('image', function(event, dataUrl){
  //$('#gallery').append('<img src="' + dataUrl + '" >');
  // TODO:
  // Space should capture image
  // Popup opens with the captured image and focuses on an input box for the instagram username
  // Escape closes the popup and enter submits the content
  // User gets a popup of the generated image...close it with ESC
});

$(document).keypress(function(event) {
  var shutter = $('#photobooth li.trigger');
  var username = $('input[data-name="username"]');
  if (event.charCode == '32') {
    console.log('Taking a picture')
    shutter.click();
    username.focus();
  }
});