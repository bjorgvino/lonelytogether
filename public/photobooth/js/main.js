$(function(){
  var $username = $('input[data-name="username"]');
  var $video = $('#videodivs');
  var $preview = $('#snapshotdiv');
  var readyToSubmit = false;
  var currentDataUrl = '';

  function getKeyCode(event){
    return (typeof event.which == "number") ? event.which : event.keyCode;
  }

  function grabImage(){
    currentDataUrl = takeSnapshot();
    $username.focus();
    $video.hide();
    readyToSubmit = true;
  }

  function discardImage(){
    $video.show();
    $preview.hide();
    $username.val('');
    readyToSubmit = false;
    currentDataUrl = '';
  }

  function submitImage(){
    console.log('Sending image to server...');
    //console.log(currentDataUrl);
    // TODO: Do some stuff...

    // Wait for the response, display the result for a while, then discard...
    discardImage();
  }

  $username.keydown(function(event){
    var keyCode = getKeyCode(event);
    if (keyCode == '32') {
      // Disable space in username input
      event.preventDefault();
      return;
    } else if (keyCode == '13') {
      // Submit image
      submitImage();
    }
  });

  $(document).keydown(function(event) {
    var keyCode = getKeyCode(event);
    if (keyCode == '32') {
      // Disable space
      event.preventDefault();
      // Take a picture
      grabImage();
    }
    else if (keyCode == '27') {
      // Cancel
      discardImage();
    }
  });
});