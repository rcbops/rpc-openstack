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
    controller('rpc_heat', function ($scope, $sce, $modal, $log) {
      $scope.parameters = {};
      $scope.parameters.details = {}
      
      $scope.parse_parameter = function (parameter) {
        var parameter_details;
      
        function comma_delimited_list_parameter(parameter) {
          $scope.parameters.details[parameter.name] = parameter['default'];

          var item = '<div>' +
            '<label>' + parameter.label + ':</label>' +
            '<select name="' + parameter.name + '" ' +
              'value="' + parameter.default + '" ' +
              'tooltip="' + parameter.description + '" ' +
              'ng-model="parameters.details[\'' + parameter.name + '\']">';
              
          for (var i=0;i<parameter.constraints[0].allowed_values.length;i++) {
            item += '<option>' + parameter.constraints[0].allowed_values[i] + '</option>'
          }
              
          item += '</select>' +
            '</div>';
            
          return item;
        };
        
        function number_parameter(parameter) {
          $scope.parameters.details[parameter.name] = parameter['default'];

          return '<div>' + 
          '<label>' + parameter.label + ':</label>' +
          '<input type="number" name="' + parameter.name + '"' + 
            'value="' + parameter.default + '"' +
            'tooltip="' + parameter.description + 
            '" ng-model="parameters.details[\'' + parameter.name + '\']"></div>';
          
        };
        
        function string_parameter(parameter) {
          $scope.parameters.details[parameter.name] = parameter['default'];

          return '<div>' + 
          '<label>' + parameter.label + ':</label>' +
          '<input name="' + parameter.name + '"' + 
            'value="' + parameter.default + '"' +
            'tooltip="' + parameter.description + 
            '" ng-model="parameters.details[\'' + parameter.name + '\']"></div>';
          
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
        $scope.templates[i].short_desc_safe = $sce.trustAsHtml($scope.templates[i].short_desc);
        $scope.templates[i].long_desc_safe = $sce.trustAsHtml($scope.templates[i].long_desc);
      }
      
      $scope.more_info = function (table) {
        var templateHeader = '' +
            '<div class="modal-header">' +
            '    <img ng-if="table.logo!=\'None\'" ng-src="{$table.logo$}" style="max-width: 850px">' +
            '</div>';
            
        var templateBody = '' +
            '<div class="modal-body">' +
            '    <span ng-bind-html="table.long_desc_safe"></span>';
            
            for (var i=0;i<table.parameters.length;i++) {
              templateBody += $scope.parse_parameter(table.parameters[i]);
            }
            
        templateBody += '</div>';
            
        var templateFooter = '' +
            '<div class="modal-footer">' +
            '    <button class="btn btn-primary" ng-click="ok()">OK</button>' +
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
    
        modalInstance.result.then(function (parameters) {
          $log.debug(parameters);
        }, function () {
          $log.info('Modal dismissed at: ' + new Date());
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
    
        modalInstance.result.then(function (parameters) {
          $log.debug(parameters)
        });
      };

    });   


  horizonApp.
    controller('ModalInstanceCtrl', function ($scope, $modalInstance, table, parameters) {

    $scope.table = table;
    $scope.parameters = parameters;
  
    $scope.ok = function () {
      $modalInstance.close($scope.parameters);
    };
  
    $scope.cancel = function () {
      $modalInstance.dismiss('cancel');
    };
  });
}());
