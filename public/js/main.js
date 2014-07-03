$(function(){
  var uploadUrl = '/api/upload';
  var $username = $('input[data-name="username"]');
  var $video = $('#videodivs');
  var $preview = $('#snapshotdiv');
  var $previewImage = $('#resultimage');
  var $previewImageContainer = $('#resultdiv');
  var $loading = $('#loaderImage');
  var readyToSubmit = false;
  var submitting = false;
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
    submitting = false;
    currentDataUrl = '';

    $preview.hide();
    $previewImageContainer.fadeOut(animationSpeed, function(){
      $video.fadeIn(animationSpeed, function(){
        readyToSubmit = false;
      });
    });    
  }

  function submitImage(){
    if (!$username.val()){
      console.log('Username missing...aborting.')
      return;
    }
    console.log('Sending image to server....');
    submitting = true;
    startAnimation();

    $.post(uploadUrl, {'dataUrl': currentDataUrl, 'username': $username.val()})
    .done(function(data){
      console.log(data);
      stopAnimation();
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
      stopAnimation();
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
      if (!submitting){
        submitImage();  
      }
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

  // Loader animation
  var cSpeed=9;
  var cWidth=64;
  var cHeight=64;
  var cTotalFrames=12;
  var cFrameWidth=64;
  var cImageSrc='/img/loading_sprites.png';

  var cImageTimeout=false;
  var cIndex=0;
  var cXpos=0;
  var cPreloaderTimeout=false;
  var SECONDS_BETWEEN_FRAMES=0;

  function startAnimation(){
    $loading.css('background-image', 'url(' + cImageSrc + ')')
            .css('width', cWidth + 'px')
            .css('height', cHeight + 'px')
            .show();
    
    //FPS = Math.round(100/(maxSpeed+2-speed));
    FPS = Math.round(100/cSpeed);
    SECONDS_BETWEEN_FRAMES = 1 / FPS;
    
    cPreloaderTimeout=setTimeout(function() { continueAnimation(); }, SECONDS_BETWEEN_FRAMES/1000);
  }

  function continueAnimation(){
    cXpos += cFrameWidth;
    //increase the index so we know which frame of our animation we are currently on
    cIndex += 1;
     
    //if our cIndex is higher than our total number of frames, we're at the end and should restart
    if (cIndex >= cTotalFrames) {
      cXpos =0;
      cIndex=0;
    }
    
    $loading.css('backgroundPosition', (-cXpos)+'px 0');
    cPreloaderTimeout=setTimeout(function() { continueAnimation(); }, SECONDS_BETWEEN_FRAMES*1000);
  }

  function stopAnimation(){//stops animation
    $loading.hide();
    clearTimeout(cPreloaderTimeout);
    cPreloaderTimeout=false;
  }
});