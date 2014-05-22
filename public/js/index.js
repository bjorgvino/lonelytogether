$(function () {
	sizeHeader();

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

function sizeHeader($container, $logo) {
	var $container = $('#logo'),
		$logo = $container.find('img'),
		viewportheight = $(window).height();

	$container.css('height', viewportheight).css('padding-top', (viewportheight - $logo.height()) / 2);
}