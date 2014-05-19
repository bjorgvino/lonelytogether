$(function(){
  var username = $('input[data-name="username"]');
  $(username).keypress(function(event){
    if (event.charCode == '32') {
      event.preventDefault();
      return;
    }
  });
  $(document).keypress(function(event) {
    if (event.charCode == '32') {
      console.log('Taking a picture')
      takeSnapshot();
      username.focus();
    }
  });
});