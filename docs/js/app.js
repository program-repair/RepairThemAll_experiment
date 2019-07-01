angular.module('defects4j-website', ['ngRoute', 'ui.bootstrap', 'anguFixedHeaderTable'])
	.config(function($routeProvider, $locationProvider) {
		$routeProvider
			.when('/bug/:benchmark/:project/:id', {
				controller: 'bugController'
			})
			.when('/bug/:benchmark/:project/', {
				controller: 'bugController'
			})
			.when('/', {
				controller: 'mainController'
			});
		// configure html5 to get links working on jsfiddle
		$locationProvider.html5Mode(false);
	})
	.directive('keypressEvents', [
		'$document',
		'$rootScope',
		function($document, $rootScope) {
			return {
				restrict: 'A',
				link: function() {
					$document.bind('keydown', function(e) {
						$rootScope.$broadcast('keypress', e);
						$rootScope.$broadcast('keypress:' + e.which, e);
					});
				}
			};
		}
	]).directive('diff', ['$http', function ($http) {
		return {
			restrict: 'A',
			scope: {
				patch: '=diff'
			},
			link: function (scope, elem, attrs) {
				function printDiff(patch) {
					var diff = patch.diff;
					if (diff == null) {
						diff = patch.patch;
					}
					if (diff == null) {
						diff = patch.PATCH_DIFF_ORIG;
					}
					if (diff != null) {
						origin = /--- ([^ ]+).*/.exec(diff)[1]
						dest = /\+\+\+ ([^ ]+).*/.exec(diff)[1]
						if (dest.indexOf(origin) > 0) {
							diff = diff.replace(dest, origin)
						}
						diff = diff.replace(/\\"/g, '"').replace(/\\n/g, "\n").replace(/\\t/g, "\t")
						var diff2htmlUi = new Diff2HtmlUI({ diff: diff });
						diff2htmlUi.draw($(elem), {inputFormat: 'java', showFiles: false, matching: 'none'});
						diff2htmlUi.highlightCode($(elem));
					}
				}
				scope.$watch('patch', function() {
					printDiff(scope.patch);
				})
				printDiff(scope.patch);
			}
		}
		}])
	.controller('welcomeController', function($uibModalInstance) {
		this.ok = function () {
			$uibModalInstance.close();
		};
	})
	.controller('bugModal', function($scope, $rootScope, $uibModalInstance, bug, human_patches) {
		var $ctrl = this;
		$ctrl.bug = bug;
		$ctrl.human_patches = human_patches;

		$ctrl.humanPatch = function (bug) {
			if (bug == null) {
				return null;
			}
			var benchmark = bug.benchmark;
			var humanPatches = human_patches[benchmark];
			if (humanPatches == null) {
				return null;
			}
			
			if (benchmark == "Bears") {
				for (var patch of humanPatches) {
					var bugID = patch.builds.buggyBuild.id + "-" + patch.builds.fixerBuild.id
					if (patch.repository.name == bug.project && bugID == bug.bug_id) {
						return patch;
					}
				}
				return null;
			}
			if (benchmark == "Bugs.jar") {
				for (var patch of humanPatches) {
					if (patch.project.toLowerCase() == bug.project.toLowerCase() && bug.bug_id.indexOf(patch.commit) != -1) {
						return patch;
					}
				}
				return null;
			}
			if (benchmark == "Defects4J") {
				for (var patch of humanPatches) {
					if (patch.project == bug.project && bug.bug_id == patch.bugId) {
						return patch;
					}
				}
				return null;
			}
		}
		$scope.$watch('$ctrl.human_patches', function () {
			$ctrl.human = $ctrl.humanPatch(bug)	
		}, true)
		$ctrl.human = $ctrl.humanPatch(bug)
		

		$rootScope.$on('new_bug', function(e, bug) {
			$ctrl.bug = bug;
			$ctrl.human = $ctrl.humanPatch(bug)
		});
		$ctrl.ok = function () {
			$uibModalInstance.close();
		};
		$ctrl.nextPatch = function () {
			$rootScope.$emit('next_bug', 'next');
		};
		$ctrl.previousPatch = function () {
			$rootScope.$emit('previous_bug', 'next');
		};
	})
	.controller('bugController', function($scope, $location, $rootScope, $routeParams, $uibModal) {
		var $ctrl = $scope;
		$ctrl.bugs = $scope.$parent.filteredBugs;
		$ctrl.human_patches = $scope.$parent.human_patches;
		$ctrl.index = -1;
		$ctrl.bug = null;

		$scope.$watch("$parent.filteredBugs", function () {
			$ctrl.bugs = $scope.$parent.filteredBugs;
			$ctrl.index = getIndex($routeParams.benchmark, $routeParams.project, $routeParams.id);
		});

		var getIndex = function (benchmark, project, bug_id) {
			if ($ctrl.bugs == null) {
				return -1;
			}
			for (var i = 0; i < $ctrl.bugs.length; i++) {
				if ($ctrl.bugs[i].benchmark == benchmark 
					&& $ctrl.bugs[i].project == project 
					&& ($ctrl.bugs[i].bug_id == bug_id || bug_id == null)) {
					return i;
				}
			}
			return -1;
		};

		$scope.$on('$routeChangeStart', function(next, current) {
			$ctrl.index = getIndex(current.params.benchmark, current.params.project, current.params.id);
		});

		var modalInstance = null;
		$scope.$watch("index", function () {
			if ($scope.index != -1) {
				if (modalInstance == null) {
					modalInstance = $uibModal.open({
						animation: true,
						ariaLabelledBy: 'modal-title',
						ariaDescribedBy: 'modal-body',
						templateUrl: 'modelPatch.html',
						controller: 'bugModal',
						controllerAs: '$ctrl',
						size: "lg",
						resolve: {
							bug: function () {
								return $scope.bugs[$scope.index];
							},
							human_patches: $ctrl.human_patches
						}
					});
					modalInstance.result.then(function () {
						modalInstance = null;
						$location.path("/");
					}, function () {
						modalInstance = null;
						$location.path("/");
					})
				} else {
					$rootScope.$emit('new_bug', $scope.bugs[$scope.index]);
				}
			}
		});
		var nextPatch = function () {
			var index  = $scope.index + 1;
			if (index == $ctrl.bugs.length)  {
				index = 0;
			}
			$location.path( "/bug/" + $ctrl.bugs[index].benchmark + "/" + $ctrl.bugs[index].project + "/" + $ctrl.bugs[index].bug_id );
			return false;
		};
		var previousPatch = function () {
			var index  = $scope.index - 1;
			if (index < 0) {
				index = $ctrl.bugs.length - 1;
			}
			$location.path( "/bug/" + $ctrl.bugs[index].benchmark + "/" + $ctrl.bugs[index].project + "/" + $ctrl.bugs[index].bug_id );
			return false;
		};

		$scope.$on('keypress:39', function () {
			$scope.$apply(function () {
				nextPatch();
			});
		});
		$scope.$on('keypress:37', function () {
			$scope.$apply(function () {
				previousPatch();
			});
		});
		$rootScope.$on('next_bug', nextPatch);
		$rootScope.$on('previous_bug', previousPatch);
	})
	.controller('mainController', function($scope, $location, $rootScope, $http, $uibModal) {
		$scope.sortType     = ['benchmark', 'project', 'bug_id']; // set the default sort type
		$scope.sortReverse  = false;
		$scope.match  = "all";
		$scope.filters = {};
		$scope.benchmarks = ["Bears", "Defects4J", "IntroClassJava", "Bugs.jar", "QuixBugs"];
		$scope.tools = ["NPEFix", "Nopol", "DynaMoth", "GenProg-A", "jGenProg", "Kali-A", "jKali", "ARJA", "RSRepair-A", "Cardumen", "jMutRepair"];

		$scope.human_patches = {};

		for(var benchmark of $scope.benchmarks) {
			((benchmark => {
				$http.get("data/" + benchmark.toLowerCase() + ".json").then(response => {
					$scope.human_patches[benchmark] = response.data;
				}, error => {
					// ignore
				})
			}))(benchmark)
		}
		
		// create the list of sushi rolls 
		$scope.patches = [];
		$scope.bugs = [];

		$http.get("data/patches.json").then(function (response) {
			$scope.patches = response.data;
			
			var bugs = {}
			for (var patch of $scope.patches) {
				if (bugs[patch.benchmark+patch.project+patch.bug_id] == null) {
					bugs[patch.benchmark+patch.project+patch.bug_id] = {
						benchmark: patch.benchmark,
						project: patch.project,
						bug_id: patch.bug_id,
						repairs: []
					}
				}
				bugs[patch.benchmark+patch.project+patch.bug_id].repairs.push(patch)
			}

			for (var key in bugs){
				$scope.bugs.push(bugs[key]);
			}


			var element = angular.element(document.querySelector('#menu')); 
			var height = element[0].offsetHeight;

			angular.element(document.querySelector('#mainTable')).css('height', (height-160)+'px');
		});

		$scope.openBug = function (bug) {
			$location.path( "/bug/" + bug.benchmark + "/" + bug.project + "/" + bug.bug_id );
		};

		$scope.sort = function (sort) {
			if (sort == $scope.sortType || (sort[0] == 'benchmark' && $scope.sortType[0] == 'benchmark')) {
				$scope.sortReverse = !$scope.sortReverse; 
			} else {
				$scope.sortType = sort;
				$scope.sortReverse = false; 
			}
			return false;
		}

		$scope.countBugs = function (key, filter) {
			if (filter == null) {
				filter = {
				}
			}
			if (filter.count) {
				return filter.count;
			}
			var count = 0;
			console.log(key)
			for(var i = 0; i < $scope.bugs.length; i++) {
				if ($scope.bugs[i].benchmark.toLowerCase() === key.toLowerCase()) {
					count++;
				} else if ($scope.bugs[i].benchmark === key) {
					count++;
				}
			}
			filter.count = count;
			return count;
		};

		$scope.naturalCompare = function(a, b) {
			return naturalSort(a, b);
		}
		$scope.bugsFilter = function (bug, index, array) {
			var allFalse = true;
			for (var i in $scope.filters) {
				if ($scope.filters[i] === true) {
					allFalse = false;
					break;
				}
			}
			var matchSearch = ($scope.search == '' || $scope.search == null || bug.benchmark.toLowerCase().indexOf($scope.search.toLowerCase()) !== -1);
			if (allFalse) {
				return matchSearch;
			}

			
			var hasBenchmark = false;
			var hasRepair = false;
			for (var filter in $scope.filters) {
				if ($scope.filters[filter] != true) {
					continue
				}
				hasBenchmark = hasBenchmark || $scope.benchmarks.indexOf(filter) != -1;
				hasRepair = hasRepair || $scope.tools.indexOf(filter) != -1;
			}
			

			var matchBenchmark = $scope.filters[bug.benchmark] == true || !hasBenchmark;

			var matchTools = false;
			if (hasRepair) {
				for (var repair of bug.repairs) {
					matchTools = $scope.filters[repair.tool] == true;
					if (matchTools) {
						break
					}
				}
			} else {
				matchTools = true;
			}

			return matchBenchmark && matchTools;
		};
	});
