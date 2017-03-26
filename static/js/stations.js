

function StationController ($stationCard) {
  this.card = $stationCard;

  this.activeStatusToggle = this.card.find('.active-status-toggle');
  
  this.sensorIndicatorEffect = this.card.find('.sensor .indicator-graphic .effect');
  this.sensorStatusValue = this.card.find('.sensor .controls .value');
  
  this.sprinklerStatusToggle = this.card.find('.sprinkler-status-toggle');
  this.sprinklerModeTabs = this.card.find('.sprinkler .mode-selector .tab');
  this.sprinklerIndicatorEffect = this.card.find('.sprinkler .indicator-graphic .effect');
  this.sprinklerStatusValue = this.card.find('.sprinkler .controls .value');

  this.stateUpdateUrl = this.card.data('updateUrl');
  this.maxHumidityAngle = this.sensorIndicatorEffect.data('maxHumidityAngle');
}
StationController.prototype.getState = function () {
  var state = {};
  state.is_active =  this.activeStatusToggle.hasClass('on');
  state.current_humidity = parseInt(this.sensorStatusValue.data('value'));
  if (isNaN(state.current_humidity)) {
    state.current_humidity = null;
  }
  state.sprinkler_mode = this.sprinklerModeTabs.filter('.active').data('value');
  state.sprinkler_status = this.sprinklerStatusValue.text();
  return state;
};
StationController.prototype.renderState = function (state) {
  // station active status
  if (state.is_active) {
    this.activeStatusToggle.addClass('on');
  } else {
    this.activeStatusToggle.removeClass('on');
  }
  // current_humidity value
  this.sensorStatusValue.data('value', state.current_humidity);
  if (!state.is_active || isNaN(state.current_humidity)) {
    this.sensorStatusValue.text('---');
  } else {
    this.sensorStatusValue.text(state.current_humidity + '%');
  }
  // current_humidity indicator
  var humidityAngle = (state.current_humidity / 100) * this.maxHumidityAngle;
  this.sprinklerIndicatorEffect.css('stroke-dasharray', humidityAngle + ' ' + this.maxHumidityAngle);
  // sprinkler status
  this.sprinklerStatusValue
  // sprinkler mode
  this.sprinklerModeTabs.removeClass('.active');
  this.sprinklerModeTabs.filter('[data-value="' + state.sprinkler_mode + '"]').addClass('active');
};
StationController.prototype.updateServerState = function (state) {
  $.ajax({
    method: 'POST',
    url: this.stateUpdateUrl,
    data: state,
    dataType: 'json'
  }).done(function( data, textStatus, jqXHR ) {
    this.renderState(data);
    this.showMessage('info', textStatus);
  }).fail(function( jqXHR, textStatus, errorThrown ) {
    this.showMessage('error', textStatus);
  });
};


$(document).ready(function () {
  var stations = [];
  $('.station.card').each(function () {
    var station = new StationController($(this));
    stations.push(station);
  });
});





  // function updateCaption() {
  //
  // }
  //
  // this.getStatus = function () {
  //   return this.button.hasClass(STATUS_ON) ? STATUS_ON : STATUS_OFF;
  // }
  //
  // this.setStatus = function (status) {
  //   // toggle the class on the button
  //   button.toggleClass('ON');
  //   // change the caption text to reflect the change if available:
  //   captionText = statusCaptionMap[this.getStatus()];
  //   if(caption && captionText ){
  //     caption.text(captionText);
  //   }
  // }
  //
  //
  // if(caption) {
  //   statusCaptionMap[STATUS_ON] = caption.data('captionOn');
  //   statusCaptionMap[STATUS_OFF] = caption.data('captionOff');
  // }