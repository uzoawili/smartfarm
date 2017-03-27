
var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
var pollInterval = 2000;
var stations = [];



function StationController ($stationCard) {
  this.card = $stationCard;

  this.activeStatusToggle = this.card.find('.active-status-toggle');
  this.controls = this.card.find('.station-controls');

  this.sensorIndicatorEffect = this.card.find('.sensor .indicator-graphic .effect');
  this.sensorStatusValue = this.card.find('.sensor .controls .value');
  
  this.sprinklerStatusToggle = this.card.find('.sprinkler-status-toggle');
  this.sprinklerModeTabs = this.card.find('.sprinkler .mode-selector .tab');
  this.sprinklerIndicatorEffect = this.card.find('.sprinkler .indicator-graphic .effect');
  this.sprinklerStatusValue = this.card.find('.sprinkler .controls .value');

  this.fetchStateUrl = this.card.data('fetchUrl');
  this.updateStateUrl = this.card.data('updateUrl');
  this.maxHumidityAngle = this.sensorIndicatorEffect.data('maxHumidityAngle');

  this.activeStatusToggle.click(this.handleAnyStateChange.bind(this));
  this.sprinklerStatusToggle.click(this.handleAnyStateChange.bind(this));
  this.sprinklerModeTabs.click(this.handleAnyStateChange.bind(this));
}

StationController.prototype.getState = function () {
  var state = {};
  state.is_active =  this.activeStatusToggle.hasClass('on');
  state.current_humidity = parseInt(this.sensorStatusValue.data('value'));
  if (isNaN(state.current_humidity)) {
    state.current_humidity = null;
  }
  state.sprinkler_mode = this.sprinklerModeTabs.filter('.active').data('value');
  state.sprinkler_is_on = this.sprinklerStatusValue.data('value');
  return state;
};

StationController.prototype.renderState = function (state) {
  // station active status
  this.activeStatusToggle.toggleClass('on', state.is_active);
  this.controls.toggleClass('disabled', !state.is_active);
  // current_humidity value and angle
  this.sensorStatusValue.data('value', state.current_humidity);
  if (state.is_active && $.isNumeric(state.current_humidity)) {
    this.sensorStatusValue.text(state.current_humidity + '%');
  } else {
    this.sensorStatusValue.text('---');
  }
  // current_humidity indicator angle
  this.sensorIndicatorEffect.css('stroke-dasharray', this.getHumidityAngle(state) + ' ' + this.maxHumidityAngle);
  // sprinkler status value
  this.sprinklerStatusValue.data('value', state.sprinkler_is_on);
  this.sprinklerStatusValue.text((state.sprinkler_is_on ? 'on' : 'off'));
  // sprinkler indicator effect and toggle
  this.sprinklerIndicatorEffect.toggleClass('on', state.sprinkler_is_on);
  this.sprinklerStatusToggle.toggleClass('on', state.sprinkler_is_on);
  this.sprinklerStatusToggle.toggleClass('hidden', (state.sprinkler_mode=='Auto'));
  // sprinkler mode tabs
  this.sprinklerModeTabs.each(function () {
    var tab = $(this);
    tab.toggleClass('active', (state.sprinkler_mode==tab.data('value')));
    tab.toggleClass('disabled', !state.is_active);
  });
};

StationController.prototype.fetchServerState = function () {
  $.ajax({
    method: 'GET',
    url: this.fetchStateUrl,
    dataType: 'json',
    })
  .done(function(data) {
    this.renderState(data);
    }.bind(this))
  .fail(function() {
    toastr.error('Sorry, an error occured and the action could not be completed.');
    }.bind(this));
};

StationController.prototype.updateServerState = function (state) {
  $.ajax({
    method: 'POST',
    url: this.updateStateUrl,
    data: JSON.stringify(state),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
    headers: {'X-CSRFToken': csrfToken}
    })
  .done(function(data) {
    this.renderState(data);
    }.bind(this))
  .fail(function() {
    toastr.error('Sorry, an error occured and the action could not be completed.');
    }.bind(this));
};

StationController.prototype.handleAnyStateChange = function (e) {
  var target = $(e.currentTarget);
  var state = this.getState();
  var state_changed = false;
  // detect the state change
  if (target.is(this.activeStatusToggle)) {
    state.is_active = !state.is_active;
    state_changed = true;
  } else if (target.is(this.sprinklerStatusToggle)) {
    state.sprinkler_is_on = !state.sprinkler_is_on;
    state_changed = true;
  } else if (this.sprinklerModeTabs.filter(target).length && !target.hasClass('active')) {
    state.sprinkler_mode = $(target).data('value');
    state_changed = true;
  }
  // update the server only if the state changed
  if (state_changed) {
    this.updateServerState(state);
  }
};

StationController.prototype.getHumidityAngle = function (state) {
  if (!state.is_active || isNaN(state.current_humidity)) return 0;
  return (state.current_humidity / 100) * this.maxHumidityAngle;
};



$(document).ready(function () {

  // initialize toastr:
  toastr.options = {
    "closeButton": false,
    "positionClass": "toast-top-center",
    "preventDuplicates": true,
    "showDuration": "200",
    "hideDuration": "700",
    "timeOut": "5000"
  }

  // initialize the  stations
  $('.station.card').each(function () {
    stations.push(new StationController($(this)));
  });

  //  start the polling
  // stations[0].fetchServerState();
  setInterval(function () {
    stations.forEach(function(station) {
      station.fetchServerState();
    });
  }, pollInterval);

});