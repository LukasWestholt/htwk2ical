$.fn.setUpTooltip = function (options) {
    options['trigger'] = 'manual';
    let tooltip1 = new bootstrap.Tooltip($(this)[0], options);
    tooltip1.show();
    return $(this);
};

$.fn.deleteTooltip = function () {
    let tooltip1 = bootstrap.Tooltip.getInstance($(this)[0]);
    if (tooltip1) {
        tooltip1.dispose();
        return true;
    }
    return false;
};

$.fn.setUpPopover = function (options) {
    let popover1 = new bootstrap.Popover($(this)[0], options);
    popover1.show();
    return $(this);
};

$.fn.deletePopover = function () {
    let popover1 = bootstrap.Popover.getInstance($(this)[0]);
    if (popover1) {
        popover1.dispose();
        return true;
    }
    return false;
};
