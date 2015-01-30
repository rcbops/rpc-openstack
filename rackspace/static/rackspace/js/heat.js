// Redfining the entire horizonApp here because I can't find any other way of
// loading the ui.bootstrap module I want to use.
// TODO: Check with Richard Jones that this is sane.
var horizon_dependencies = ['hz.conf', 'hz.utils', 'ngCookies', 'ui.bootstrap'];
dependencies = horizon_dependencies.concat(angularModuleExtension);
var horizonApp = angular.module('hz', dependencies)
  .config(['$interpolateProvider', '$httpProvider',
    function ($interpolateProvider, $httpProvider) {
      $interpolateProvider.startSymbol('{$');
      $interpolateProvider.endSymbol('$}');
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
      $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    }])
  .run(['hzConfig', 'hzUtils', '$cookieStore',
    function (hzConfig, hzUtils, $cookieStore) {
      //expose the configuration for horizon legacy variable
      horizon.conf = hzConfig;
      horizon.utils = hzUtils;
      angular.extend(horizon.cookies = {}, $cookieStore);
      horizon.cookies.put = function (key, value) {
        //cookies are updated at the end of current $eval, so for the horizon
        //namespace we need to wrap it in a $apply function.
        angular.element('body').scope().$apply(function () {
          $cookieStore.put(key, value);
        });
      };
    }]);

(function () {
  'use strict';
  horizonApp.
    controller('rpc_heat', function ($scope, $sce, $modal, $log, $http) {
      $scope.alerts = []
      $scope.parameters = {};
      $scope.parameters.details = {}
      
       $scope.closeAlert = function(index) {
        $scope.alerts.splice(index, 1);
      };
      
      $scope.parse_parameter = function (parameter) {
        var parameter_details;
        
        function safe_input_name(input_name) {
          return input_name.replace(/-/g,'_');
        }
      
        function comma_delimited_list_parameter(parameter) {
          var input_name = safe_input_name(parameter.name);

          $scope.parameters.details[parameter.name] = parameter['default'];

          var item = '<div class="control-group" ' +
            'ng-class="{ error: templateForm.' + input_name + '.$error.required}"' +
            '>' + 
            '<label>' + parameter.label + ':</label>' +
            '<select name="' + input_name + '" ' +
              ' class="form-control"' +
              ' value="' + parameter.default + '" ' +
              ' tooltip="' + parameter.description + '" ' +
              ' ng-model="parameters.details[\'' + parameter.name + '\']" required>';
              
          for (var i=0;i<parameter.constraints[0].allowed_values.length;i++) {
            item += '<option>' + parameter.constraints[0].allowed_values[i] + '</option>'
          }
              
          item += '</select>' +
          //'        <tt>templateForm.'+ input_name +'.$valid = {$templateForm.' + input_name + '.$valid$}</tt><br/>' +
          //'        <tt>templateForm.'+ input_name +'.$required = {$templateForm.' + input_name + '.$required$}</tt><br/>' +
            '</div>';
            
          return item;
        };
        
        function number_parameter(parameter) {
          var input_name = safe_input_name(parameter.name);

          $scope.parameters.details[parameter.name] = parameter['default'];

          return '<div class="control-group" ' +
          'ng-class="{ error: (templateForm.' + input_name + '.$error.required || templateForm.' + input_name + '.$error.number)}"' +
          '>' + 
          '<label for="' + input_name + '">' + parameter.label + ':</label>' +
          //'<div class="control-group">' +
          '    <input type="number" id="' + input_name + '" name="' + input_name + '"' + 
          '      class="form-control"' +
          '      value="' + parameter.default + '"' +
          '      placeholder="' + parameter.description + '"' +
          '      tooltip="' + parameter.description + '"' +
          '      ng-model="parameters.details[\'' + parameter.name + '\']"' +
          '      required' +
          '    >' +
          '    <span class="help-inline" ng-show="templateForm.' + input_name + '.$error.required">' + parameter.label + ' is a required field.</span>' +
          '    <span class="help-inline" ng-show="templateForm.' + input_name + '.$error.number">Please enter a valid number.</span>' +
          //'</div>' +
          '</div>';
          
        };
        
        function string_parameter(parameter) {
          var input_name = safe_input_name(parameter.name);

          $scope.parameters.details[parameter.name] = parameter['default'];
          
          var input_name = parameter.name.replace('-','_');

          return '<div class="control-group" ' +
          'ng-class="{ error: (templateForm.' + input_name + '.$error.required || templateForm.' + input_name + '.$error.number)}"' +
          '>' + 
          '<label>' + parameter.label + ':</label>' +
          '<input name="' + input_name + '"' + 
            ' class="form-control"' +
            ' value="' + parameter.default + '"' +
            ' placeholder="' + parameter.description + '"' +
            ' tooltip="' + parameter.description + 
            '" ng-model="parameters.details[\'' + parameter.name + '\']" required>' +
            '  <span class="help-inline" ng-show="templateForm.' + input_name + '.$error.required">' + parameter.label + ' is a required field.</span>' +
            '</div>';
          
        };
                
        switch (parameter.type) {
          case 'comma_delimited_list':
            parameter_details = comma_delimited_list_parameter(parameter);
            break;
          case 'string':
            parameter_details = string_parameter(parameter);
            break;
          case 'number':
            parameter_details = number_parameter(parameter);
            break;
          default:
            parameter_details = '<p>Don\'t know how to deal with a ' + parameter.type + '</p>';
        }
        
        return '<div>' + parameter_details + '</div>'
      };
      
      $scope.templates = rpc_templates;

      for (var i=0;i<$scope.templates.length;i++) {
        $scope.templates[i].title_safe = $sce.trustAsHtml($scope.templates[i].title);
        $scope.templates[i].short_desc_safe = $sce.trustAsHtml($scope.templates[i].short_desc);
        $scope.templates[i].long_desc_safe = $sce.trustAsHtml($scope.templates[i].long_desc);
        $scope.templates[i].architecture_safe = $sce.trustAsHtml($scope.templates[i].architecture);
      }
      
      $scope.more_info = function (table) {
        var templateHeader = '' +
            '<div class="modal-header">' +
            '    <img ng-if="table.logo!=\'None\'" ng-src="{$table.logo$}" style="max-width: 850px">' +
            '</div>';
            
        var templateBody = '' +
            '<div class="modal-body">' +
            '    <h2 ng-bind-html="table.title_safe"></h2><div ng-bind-html="table.long_desc_safe"></div>' +
            '    <h3>Architecture</h3><div ng-bind-html="table.architecture_safe"></div>' +
            '    <h3>Design Specs</h3><ul style="list-style-type: disc">'
        
        for (var i=0;i<table.design_specs.length;i++) {
            templateBody += '<li>' + table.design_specs[i] + '</li>'
        }

        templateBody += '    </ul><h3>Parameters</h3>' +
            '<form name="templateForm">';
            
        for (var i=0;i<table.parameters.length;i++) {
            templateBody += $scope.parse_parameter(table.parameters[i]);
        }
            
        templateBody += '    </form>' +
          //'        <tt>templateForm.input.$valid = {$templateForm.input.$valid$}</tt><br/>' +
          //'        <tt>templateForm.input.$error = {$templateForm.input.$error$}</tt><br/>' +
          //'        <tt>templateForm.$valid = {$templateForm.$valid$}</tt><br/>' +
          //'        <tt>templateForm.$error.required = {$!!templateForm.$error.required$}</tt><br/>'
          '</div>';
            
        var templateFooter = '' +
            '<div class="modal-footer">' +
            '    <button class="btn btn-primary" ng-disabled="!templateForm.$valid" ng-click="ok()">Launch Solution</button>' +
            '    <button class="btn btn-warning" ng-click="cancel()">Cancel</button>' +
            '</div>';
        
        var templateText = templateHeader + templateBody + templateFooter;

        var modalInstance = $modal.open({
          template: templateText,
          controller: 'ModalInstanceCtrl',
          size: 'lg',
          resolve: {
            table: function () {
              return table;
            },
            parameters: function() {
              return $scope.parameters;
            }
          }
        });
    
        modalInstance.result.then(function (solution) {
          $http.post(solution.launch_url, solution.details).
            success(function(data, status, headers, config) {
              // this callback will be called asynchronously
              // when the response is available
              //$log.debug('Solution Launched');
              //$scope.alerts.push({ type: 'success', msg: 'Solution launched.'+data });
              window.location = data; // server sends redirect URL in body
            }).
            error(function(data, status, headers, config) {
              // called asynchronously if an error occurs
              // or server returns response with an error status.
              //$log.error('Failed to launch solution');
              $scope.alerts.push({type: 'danger', msg: 'Failed to launch solution.'});
            });
        }, function () {
        });
      };

      $scope.open = function (size) {
    
        var modalInstance = $modal.open({
          templateUrl: 'myModalContent.html',
          controller: 'ModalInstanceCtrl',
          size: size,
          resolve: {
            items: function () {
              return $scope.items;
            }
          }
        });
    
        //modalInstance.result.then(function (solution) {
          ////$log.debug(solution);
          ////$http.post(solution.launch_url, solution.details).
            ////success(function(data, status, headers, config) {
              ////// this callback will be called asynchronously
              ////// when the response is available
              ////$log.debug('Solution Launched')
            ////}).
            ////error(function(data, status, headers, config) {
              ////// called asynchronously if an error occurs
              ////// or server returns response with an error status.
            ////});
        //});
      };

    });   


  horizonApp.
    controller('ModalInstanceCtrl', function ($scope, $modalInstance, table, parameters) {

    $scope.table = table;
    $scope.parameters = parameters;
  
    $scope.ok = function () {
      $scope.parameters['id'] = table.id;
      $scope.parameters['launch_url'] = table.launch_url;
      $modalInstance.close($scope.parameters);
    };
  
    $scope.cancel = function () {
      $modalInstance.dismiss('cancel');
    };
  });
}());
