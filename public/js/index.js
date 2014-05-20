$(function () {
	sizeHeader();
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