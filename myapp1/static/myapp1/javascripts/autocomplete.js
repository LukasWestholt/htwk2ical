$(function () {

  // Autocomplete by jquery-ui
  // ---------------------------------------------------------------------------

  let groupData,          // complete data (label + id)
      groupDataArr = [],  // labels only
      $submitLink    = $('#submit-link'),
      sgData; // studium generale data

  // set up an input field for autocomplete, also used in calendar.js
  $.fn.setUpAutocomplete = function(useSgData, sgCallback) {
    return $(this).autocomplete({
      source: useSgData ? sgData : groupData,

      // save group-ID as data-attribute of input
      select: useSgData ? sgCallback : function(event, ui) {
        $(this).data('group-id', ui.item.id);
      }
    });
  };


  // fetch group data for autocomplete
  if ($(".group-title-bg").length > 0) {
    $.get(DJANGO_group, null, function (data) {
      groupData = data["groups"];
      $(".group-title-bg").find('input').setUpAutocomplete();

      // save labels only so we can use '$.inArray' for easier validation
      $.each(groupData, function (i, val) {
        groupDataArr.push(val.label);
      });
    });
  }

  // fetch group data for autocomplete
  if ($('.choose-modules').length > 0) {
    $.get(DJANGO_studium_generale, null, function (data) {
      sgData = data["studium_generale"];
      sgData = Object.keys(sgData).map((key) => sgData[key]);
    });
  }


  // Group validation
  // ---------------------------------------------------------------------------

  // trigger submit when clicking on button
  $submitLink.click(function (e) {
    let $groupTitles = $('.group-titles'),
        groupIdArr = [];

    // check if each inserted value is inside our array of possible values
    $groupTitles.each(function (i, el) {
      let $el       = $(el),
          val       = $el.val(),
          groupID = $el.data('group-id');

      // skip empty values
      if (!val)
        return;

      // if value is invalid: prevent submit and show tooltip
      if (groupDataArr.indexOf(val) < 0) {

        if (!e.isDefaultPrevented()) { // make sure error tooltips are only shown once
          e.preventDefault();
          $el.showErrorPopover();
        }

      // we have at least one valid group title, so let's save its group-ID
      } else if (groupID) {
        groupIdArr.push(groupID);
      }
    });


    // if we have no errors until now
    if (!e.isDefaultPrevented()) {

      // if we have empty fields only, let's show an error popover
      if (groupIdArr.length > 0) {
        // we have valid inputs, so build the target url
        // replace dummy url with real group-IDs
        let groupIdStr = groupIdArr.join(DJANGO_divider);
        $submitLink.prop('href', DJANGO_dummy_href.replace(DJANGO_dummy_id_str, groupIdStr));
      } else {
        e.preventDefault();
        $groupTitles.eq(0).showErrorPopover();
      }
    }
  });


  // attaches popover and shows it
  $.fn.showErrorPopover = function () {
    return this.addClass('error').setUpPopover({
      title:     'Bitte Studiengang aus der Liste wählen!',
      content:   'Einfach die ersten Buchstaben des Studiengangs eintippen und den Richtigen aus den Ergebnisliste heraussuchen.',
      placement: 'top',
      trigger:   'manual'
    });
  };

  // remove error class and tooltip when user starts correcting wrong identifier
  $('#group-title-wrapper').on('focus', '.group-titles.error', function () {
    $(this).removeClass('error').deletePopover();
  });
});