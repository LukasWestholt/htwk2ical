$(function () {

  // Create calendar
  // ---------------------------------------------------------------------------

  // make button disappear and show input instead
  $('#create-calendar-cta').click(function(e){
    e.preventDefault();
    $('#create-calendar-wrapper').slideUp(200);
    $('#group-title-wrapper').fadeIn(400);
  });


  // Show transfer info
  // ---------------------------------------------------------------------------

  $('#show-transfer-info').click(function(e) {
    e.preventDefault();
    $('#donate-transfer-info').slideToggle();
  });


  // Contact/Donate link
  // ---------------------------------------------------------------------------
  $('#contact-mail, #donate-mail').click(function () {
    let isDonate = this.id === 'donate-mail',
        address = '@' + 'lukaswestholt.de', // weird concatenation stuff for making spam bots' lives a little harder
        subject = 'HTWK2iCal' + (isDonate ? ' Kontodaten' : '');
    address = 'mailto:support' + address + '?subject=' +
              encodeURIComponent(subject);
    $(this).attr('href', address);
  });
});
