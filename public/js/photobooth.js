var video;
var canvas;
var context;
var imageFilter;

// Alias the vendor prefixed variants of getUserMedia so we can access them
// via navigator.getUserMedia
navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || 
  navigator.mozGetUserMedia || navigator.msGetUserMedia;

// Alias the vendor prefixed variants of the URL object so that we can access them
// via window.URL
window.URL = window.URL || window.webkitURL || window.mozURL || window.msURL;

// Alias the vendor prefixed variants of requestAnimationFrame so that we can access
// them via window.requestAnimationFrame fallback to setTimeout at 60hz if not supported.
window.requestAnimationFrame = (function(){
  return  window.requestAnimationFrame       || 
          window.webkitRequestAnimationFrame || 
          window.mozRequestAnimationFrame    || 
          window.oRequestAnimationFrame      || 
          window.msRequestAnimationFrame     || 
          function( callback ){
            window.setTimeout(callback, 1000 / 60);
          };
})();

function showStatus(s) {
  var status = document.querySelector("#status");
  if (status){
    document.querySelector("#status").innerHTML = s;
  }
}

// This function will be called if a webcam is available and the user has
// granted access for the web application to use it.
function successCallback(stream) {
  // Firefox has a special property that you can use to associate the stream with the
  // video object.  Other browsers require you to use createObjectURL.
  if (video.mozSrcObject !== undefined) {
    video.mozSrcObject = stream;
  } 
  else {
    video.src = (window.URL && window.URL.createObjectURL(stream)) || stream;
  }
  video.play(); 
  
  // Show the DOM elements that contain the rest of the UI
  document.querySelector("#videodivs").style.display = "block"; 
  showStatus("You should be seeing video from your camera.");
  
  // capture the first frame of video and start the animation loop that
  // continuously update the video to the screen
  update();
}

// This function will be called if there is no webcam available or the user has
// denied access for the web application to use it.
function failureCallback() {
  showStatus("No camera is available or you have denied access.");
}

// grayscale filter using an arithmetic average of the color 
// components
grayscale = function (pixels, args) {
  var d = pixels.data;
  for (var i = 0; i < d.length; i += 4) {
    var r = d[i];
    var g = d[i + 1];
    var b = d[i + 2];
    d[i] = d[i + 1] = d[i + 2] = (r+g+b)/3;
  }
  return pixels;
};

// sepia-style filter that gives a warm antique feel to an image
sepia = function (pixels, args) {
  var d = pixels.data;
  for (var i = 0; i < d.length; i += 4) {
    var r = d[i];
    var g = d[i + 1];
    var b = d[i + 2];
    d[i]     = (r * 0.393)+(g * 0.769)+(b * 0.189); // red
    d[i + 1] = (r * 0.349)+(g * 0.686)+(b * 0.168); // green
    d[i + 2] = (r * 0.272)+(g * 0.534)+(b * 0.131); // blue
  }
  return pixels;
};
      
// filter that shifts all color information to red
red = function (pixels, args) {
  var d = pixels.data;
  for (var i = 0; i < d.length; i += 4) {
    var r = d[i];
    var g = d[i + 1];
    var b = d[i + 2];
    d[i] = (r+g+b)/3;        // apply average to red channel only
    d[i + 1] = d[i + 2] = 0; // zero out green and blue channel
  }
  return pixels;
};

// filter that brightens an image by adding a fixed value 
// to each color component
// a javascript closure is used to parameterize the filter 
// with the delta value
brightness = function(delta) {
    return function (pixels, args) {
      var d = pixels.data;
      for (var i = 0; i < d.length; i += 4) {
        d[i] += delta;     // red
        d[i + 1] += delta; // green
        d[i + 2] += delta; // blue   
      }
      return pixels;
    };
};

function processImage() {
  if (canvas.width > 0 && canvas.height > 0) {
    if (imageFilter) {      
      context.putImageData(imageFilter.apply(null, [context.getImageData(0, 0, 
        canvas.width, canvas.height)]), 0, 0);
    }
  }
}

function processVideoFrame() {
  // We have to check for the video dimensions here.
  // Dimensions will be zero until they can be determined from
  // the stream.
  if (context && video.videoWidth > 0 && video.videoHeight > 0) {
    // Resize the canvas to match the current video dimensions
    if (canvas.width != video.videoWidth) 
      canvas.width = video.videoWidth;
    if (canvas.height != video.videoHeight) 
      canvas.height = video.videoHeight;
    
    // Copy the current video frame by drawing it onto the 
    // canvas's context
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    processImage(canvas);
  }
}

var frameNumber = 0;
var startTime = null;

function update(){

  processVideoFrame();
  
  frameNumber++;
  if (startTime == null)
    startTime = (new Date).getTime(); // in milliseconds  
  // Every 60 frames calculate our actual framerate and display it
  if (frameNumber >= 60) {
      var currentTime = (new Date).getTime();            // in milliseconds
      var deltaTime = (currentTime - startTime)/1000.0;  // in seconds
      var fps = document.querySelector("#fps");
      if (fps){
        fps.innerHTML = (Math.floor(frameNumber/deltaTime) + " fps");
      }
      startTime = currentTime;
      frameNumber = 0;
  }         
  requestAnimationFrame(update); 
};

function onLoad() {

  setFilter(null);
  
  // Get the DOM object that matches the first video tag on the page
  video = document.querySelector('video');

  canvas = document.querySelector("canvas");
  context = canvas.getContext("2d");

  showStatus("Waiting for you to grant access to the camera...");
  
  // We can retrieve the video dimensions from the video object once we have
  // registered for and received the loadeddata event
  video.addEventListener('loadeddata', function(e) {
    console.log('loadeddata Video dimensions: ' + video.videoWidth + ' x ' + video.videoHeight);
    }, false);

  video.addEventListener('playing', function(e) {
    console.log('play Video dimensions: ' + video.videoWidth + ' x ' + video.videoHeight);
    }, false);

  if (navigator.getUserMedia) {
    // Ask the user for access to the camera
    navigator.getUserMedia({video: true}, successCallback, failureCallback);     
  } 
  else {
    showStatus('The navigator.getUserMedia() method not supported in this browser.');
  }
}

function takeSnapshot() {
  var url = canvas.toDataURL();
  //console.log(url);
  // Set the src of the image url to the data url
  document.querySelector("#snapshot").src = url;
  // Display the DOM elements that contain the snapshot
  document.querySelector("#snapshotdiv").style.display="block";
  return url;
}

function setFilter(f) {
  imageFilter = f;
}