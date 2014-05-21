$(function(){
  var $username = $('input[data-name="username"]');
  var $video = $('#videodivs');
  var $preview = $('#snapshotdiv');
  var $previewImage = $('#resultimage');
  var $previewImageContainer = $('#resultdiv');
  var readyToSubmit = false;
  var currentDataUrl = '';
  var animationSpeed = 'slow';

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
    $username.val('');
    currentDataUrl = '';

    $preview.hide();
    $previewImageContainer.fadeOut(animationSpeed, function(){
      $video.fadeIn(animationSpeed, function(){
        readyToSubmit = false;
      });
    });    
  }

  function submitImage(){
    console.log('Sending image to server....');

    $.post('http://localhost:5000/api/upload', {'dataUrl': currentDataUrl, 'username': $username.val()})
    .done(function(data){
      console.log(data);
      $previewImage.attr('src', data);
      $preview.fadeOut(animationSpeed, function(){
        $previewImageContainer.fadeIn(animationSpeed, function() {
          setTimeout(function() {
            discardImage();
          }, 3000);
        });
      });
    })
    .fail(function(error){
      console.log(error);
      discardImage();
    })
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