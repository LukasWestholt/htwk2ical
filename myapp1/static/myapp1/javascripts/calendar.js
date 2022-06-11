let regex_text = /^((?:.*)+?-)(\d+)(-(?:[^-]*)+)$/;

$(function () {
  /* CHOOSE MODULES ACTION
   * ---------------------------------------------------------------------------
   */

  // studium generale link
  // -----------------------------------------------------------------------------
  $('#studium_generale_link').on('click', function(e) {
    e.preventDefault();

    let sgAutocompleteInputID = 'studium_generale_autocomplete';

    // hide link and add input for autocomplete
    $(this).hide().before(
      $('<input>').attr({
        id:    sgAutocompleteInputID,
        class: 'studium-generale-autocomplete form-control',
        type:  'text'
      })
    );
    $('#' + sgAutocompleteInputID).focus()
      // set up autocomplete and give callback
      .setUpAutocomplete(true, function(event, ui) {
        let sgModuleID    = ui.item.id,
            sgModuleTitle = ui.item.label;
        add_sg_module($(this), sgModuleTitle, sgModuleID);
        $('#studium_generale_link').show();
        $(this).remove();
      })
      // init popup for entering name
      .setUpTooltip({
        title:     'Gib den Namen des Studium Generale an.',
        placement: 'bottom'
      })
      // hide popup when user starts typing
      .on('keypress', function(e) {
        let deleted = $(this).deleteTooltip();
        if (deleted) {
          $(this).unbind(e);
        }
      });
  });

  let tooltip1_identifier = 'associatedTooltip';
  let $form_el = $('.choose-modules');
  $form_el.one('mouseenter', '.input-group', function () {
    // apply tooltip and show it
    let $elForTooltip = $(this).children().filter('[type="text"]');
    $elForTooltip.addClass(tooltip1_identifier).setUpTooltip(
        {
        title: 'Klicke in das Textfeld und bestimme den Namen des Moduls selbst.',
        html: true,
        container: 'body'
    }
    );
  // pulsate tooltip as soon as it's there
  }).on('shown.bs.tooltip', function () {
    $('.tooltip .tooltip-inner').addClass('pulsate');
  // hide tooltip when user focuses an input element
  }).on('focus', 'input[type="text"]', function (e) {
    let deleted = $('.choose-modules .input-group .' + tooltip1_identifier).removeClass(tooltip1_identifier).deleteTooltip();
    if (deleted) {
       // tooltip is only shown once, so only hide it once
      $(this).unbind(e);
    }
  });

  // save changes in cookie when leaving modules page to add another group
  // ---------------------------------------------------------------------------

  $('#choose-more-groups-cta').on('click', function() {

    // give feedback
    $(this).addClass('disabled');

    // read modules
    let modules = [];
    $('.choose-modules').find('input').filter('.form-control').each(function(i, el) {
      let alias = el.value;
      let id = $(el).siblings('input[type=hidden]')[0].value;
      let sg = $(el).parent().hasClass('sg_item');
      modules.push({
        id:      id,
        alias:   alias,
        disabled: $(el).prop("disabled"),
        sg: sg
      });
    });
    // save modules in cookie
    Cookies.set('modules', JSON.stringify(modules),
      { sameSite: 'strict', expires: 1 }
    );
  });

  if ($form_el.length > 0) {
    // check for cookie modules
    let modules = Cookies.get('modules');
    // apply aliases if we have any
    if (modules) {
      /**
       * @typedef {Object} module
       * @property {string} id The id of the module.
       * @property {string} alias The alias of the module.
       * @property {boolean} disabled Disabled property of the module.
       * @property {boolean} sg Module is a studium generale.
       */
      /** @type module[] */
      modules = JSON.parse(modules);
      let edit = false;
      for (let i = 0; i < modules.length; i++) {
        if (!modules[i].id) {
          continue;
        }
        let el = $('.choose-modules input[value=' + modules[i].id + ']');
        if (el.length > 0) {
          el.siblings('.form-control').val(modules[i].alias);
          if (modules[i].disabled) {
            let source = el.closest('.input-group');
            delete_module(source);
          }
          edit = true;
        } else if (modules[i].sg) {
          let $el = $('.choose-modules #studium_generale_link');
          add_sg_module($el, modules[i].alias, modules[i].id);
          edit = true;
        }
      }
      if (edit) {
        showToast("Es wurden frühere Änderungen an den Modulen aus den Cookies übernommen.",
            {
              autohide: false
            }
        );
      }
    }
  }

  // Buttons
  // -----------------------------------------------------------------------------

  $('.reset-selection').each(function() {
    $(this).hide().on('click', (e) => {
      let $group_wrapper = $(e.target).parent('.group-wrapper');
      $group_wrapper.children('.group-modules-wrapper').children('.input-group').show()
        .children('.form-control').prop("disabled", false);
      $group_wrapper.find('.add-selection').hide().children().remove();
      $(this).hide();
    });
  })

  $(".add-selection").each(function() {
    $(this).hide().on("click", (e) => {
      let $el = $(e.target);
      $el.parents('.group-wrapper').children('.group-modules-wrapper')
          .find('.input-group #' + $el[0].id)
          .prop("disabled", false).parents().show();
      $el.remove();
      if ($(this).children().length <= 0) {
        $(this).hide();
        $('.reset-selection').hide();
      }
    });
  });

  $('.group-modules-wrapper').each(function() {
    $(this).on('click', '.del_el', (e) => {
        e.preventDefault();
        let source = $(e.target).closest('.input-group');
        let dropdown1 = bootstrap.Dropdown.getInstance(source.children('.dropdown-toggle'));
        if (dropdown1) {
            dropdown1.hide();
        }
        delete_module(source);
    });
    $(this).on('change', ':radio', (e) => {
        let source = $(e.target);
        if (source.parents('.dropdown-item').hasClass('default-item')) {
            source.closest('.input-group').find('.dropdown-icon').removeClass('bi-gear-fill').addClass('bi-gear');
        } else {
            source.closest('.input-group').find('.dropdown-icon').removeClass('bi-gear').addClass('bi-gear-fill');
        }
    });
  });

  // SPECIAL: no modules in group
  // -----------------------------------------------------------------------------

  $('.input-group').each(function() {
    let $found = $(this).children('input[type=hidden]').filter(function() {
      return this.id.match(regex_text) && this.value === '';
    })
    if ($found.length > 0) {
      console.log("Group is empty, so disable auto-generated empty module");
      $found.parent().hide().children('.form-control').prop("disabled", true);
    }
  });

  /* CHOOSE GROUPS ACTION
   * ---------------------------------------------------------------------------
   */

  // create new input field for another group
  // ---------------------------------------------------------------------------

  $('#add-group-title').click(function (e) {
    e.preventDefault();

    let groupCount = $('.group-title-bg').length,
        max = typeof groupMax == 'undefined' ? 3 : groupMax,
        $oldInputGroup = $('.group-title-bg.active'),

        // make new inputs' ID and clone present one
        newInputID = 'group-title-' + (++groupCount),
        $newEl     = $oldInputGroup
          .removeClass('active')
            // make input group a single input wrapper
          .removeClass('input-group')
          .clone();

      // remove addButton (we only need it once), change inputs' id, remove present value and initialize autocomplete
      $newEl
        .find('a')
        .remove()
        .end()
        .find('input')
        .attr('id', newInputID)
        .val('')
        .setUpAutocomplete();

    // insert our new input
    $newEl.insertBefore('#submit-link');
    let $addButton = $(this);
    if (groupCount >= max) {
      // if we have reached maximum remove addButton
      $addButton.remove();
    } else {
      // if we haven't reached the maximum make new input the active input group and move addButton down
      $newEl.addClass('active input-group');
      $addButton.appendTo($newEl);
    }
  });
});

function delete_module($source) {
    let $el2 = $source.children('.form-control');
    let $new_button = $('<input/>').attr({
      type: "button",
      id: $el2[0].id,
      value: $el2[0].value
    });
    $el2.closest('.group-wrapper').children('.add-selection').show().append($new_button);
    $('.reset-selection').show();
    $source.hide();
    $el2.prop("disabled", true);
}

function replacer(match, p1, p2, p3) {
    return [p1, parseInt(p2) + 1, p3].join('');
}

function add_sg_module(source, title, id) {
  let $el_parent = source.parents('.group-modules-wrapper');
  let $el = $el_parent.children('.input-group').last();
  let $clone = $el.clone();
  let input1 = $clone.children('.form-control').first();
  let replace_name1 = input1.attr('name').replace(regex_text, replacer);
  let replace_id1 = input1.attr('id').replace(regex_text, replacer);
  let input2 = input1.siblings('input[type=hidden]');
  let replace_name2 = input2.attr('name').replace(regex_text, replacer);
  let replace_id2 = input2.attr('id').replace(regex_text, replacer);

  input1.attr({
        id: replace_id1,
        value: title,
        name: replace_name1,
        disabled: false
      }).val(title);
  input2.attr({
        id: replace_id2,
        value: id,
        name: replace_name2
      }).val(id);
  $clone.addClass('sg_item').show();

  $el_parent.children().filter(function() {
    return this.id.match(/^id_module-form-(\d+)(-form-TOTAL_FORMS)$/);
  }).val(function(index, value) {
    return parseInt(value) + 1;
  });

  $el.after($clone);
}

function showToast(text, options) {
    $(document.body).append(
        '<div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">\n' +
        '  <div class="toast hide" role="alert" aria-live="assertive" aria-atomic="true">\n' +
        '    <div class="toast-header">\n' +
        '      <strong class="me-auto">HTWK2iCal</strong>\n' +
        '      <small><div id="time"></div></small>\n' +
        '      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>\n' +
        '    </div>\n' +
        '    <div class="toast-body">' + text + '</div>\n' +
        '  </div>\n' +
        '</div>'
    );
    $('#time').data('time',(new Date().getTime() / 1000).toFixed(0))
    updateClock(); // initial call
    let $toast = $('.toast');
    new bootstrap.Toast($toast, options).show();
    $toast.on('hidden.bs.toast', function () {
        $toast.parent().remove();
    })
}

function updateClock() {
    let $time = $('#time');
    if (!$time.length) return;
    let old_date = new Date($time.data('time') * 1000);
    let now = new Date();
    let diff = (now.getTime() - old_date.getTime()) / 1000;

    // set the content of the element with the ID time to the formatted string
    if (diff < 60) {
        $time.html("Jetzt");
        setTimeout(updateClock, 10*1000);
    } else if (diff < 120) {
        $time.html(diff.toFixed(0) + " Sekunden");
        setTimeout(updateClock, 1000);
    } else {
        $time.html((diff / 60).toFixed(0) + " Minuten");
        setTimeout(updateClock, 60*1000);
    }
}