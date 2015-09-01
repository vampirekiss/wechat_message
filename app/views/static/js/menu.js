function MenuCtrl($scope, $http) {
    $scope.buttons = buttons;

    $scope.action_url_show_class = {};
    $scope.add_submenu_show_class = 'hidden';
    $scope.selected_button = null;
    $scope.selected_sub_button = false;
    $scope.is_add_root_button = false;
    $scope.is_rename_menu = false;
    $scope.all_buttons = [];
    $scope.current_button_name = "";
    $scope.show_dialog_class = 'hidden';
    $scope.dialog_menu_name = '';

    $scope.$watch('buttons', function (buttons) {
        $scope.all_buttons = [];
        angular.forEach(buttons, function (button) {
            $scope.all_buttons.push(button);
            angular.forEach(button.sub_button, function (sub_button) {
                $scope.all_buttons.push(sub_button);
            })
        });
    }, true);

    var new_button = function (name, url) {
        return {
            'type': 'view',
            'name': name,
            'url': url || '',
            'sub_button': []
        }
    };

    var set_to_view_button = function (button) {
        button.type = "view";
        delete button.key;
    };

    $scope.dialog_close = function () {
        $scope.dialog_menu_name = '';
        $scope.show_dialog_class = 'hidden';
        $scope.is_add_root_button = false;
        $scope.is_rename_menu = false;
    };

    $scope.dialog_confirm = function () {
        if (!$scope.selected_button && !$scope.is_add_root_button) {
            return;
        }
        if ($scope.is_rename_menu) {
            $scope.selected_button.name = $scope.dialog_menu_name;
        } else {
            var button = new_button($scope.dialog_menu_name);
            if ($scope.is_add_root_button) {
                $scope.buttons.push(button)
            } else {
                $scope.selected_button.sub_button.push(button);
            }
            $scope.selected_button = button;
        }
        $scope.dialog_close();
    };

    $scope.add_root_menu = function () {
        if ($scope.buttons.length >= 3) {
            alert("最多创建最多3个一级菜单，每个一级菜单下最多可创建5个二级菜单。");
            return;
        }
        $scope.show_dialog_class = 'show';
        $scope.is_add_root_button = true;
    };

    $scope.dialog_set_menu = function (button) {
        if (!$scope.selected_button && !button) {
            return;
        }
        button = button || $scope.selected_button;
        if (button.sub_button.length >= 5) {
            alert("最多创建最多3个一级菜单，每个一级菜单下最多可创建5个二级菜单。");
            return;
        }
        if (button.sub_button.length == 0 && button.url && !confirm("使用二级菜单后，当前编辑的消息将会被清除。确定使用二级菜单？")) {
            return;
        } else {
            button.url = '';
        }
        $scope.selected_button = button;
        $scope.show_dialog_class = 'show';
    };

    $scope.add_menu = function (button, is_sub_button) {
        $scope.selected_button = button;
        $scope.selected_sub_button = is_sub_button || false;
        $scope.current_button_name = button.name;
        angular.forEach($scope.action_url_show_class, function (value, key) {
            $scope.action_url_show_class[key] = "hidden";
        });
        $scope.add_submenu_show_class = "hidden";
        if (button.sub_button.length > 0) {
            $scope.add_submenu_show_class = "show";
        } else {
            $scope.action_url_show_class[button.$$hashKey] = "show";
        }
    };

    $scope.rename_menu = function () {
        if (!$scope.selected_button) {
            return;
        }
        $scope.show_dialog_class = 'show';
        $scope.is_rename_menu = true;
        $scope.dialog_menu_name = $scope.selected_button.name;
    };

    $scope.remove_menu = function () {
        if (!$scope.selected_button) {
            return;
        }
        if (!confirm('确认要删除此菜单吗?')) {
            return;
        }
        angular.forEach(buttons, function (button, index) {
            if (button == $scope.selected_button) {
                buttons.splice(index, 1);
            } else {
                angular.forEach(button.sub_button, function (sub_button, sub_index) {
                    if (sub_button == $scope.selected_button) {
                        button.sub_button.splice(sub_index, 1);
                    }
                });
            }
        });
        $scope.selected_button = null;
    };

    $scope.save_menu = function () {
        var buttons = angular.copy($scope.buttons);
        var error_messages = [];
        angular.forEach(buttons, function (button) {
            if (button.sub_button.length == 0 && !button.url) {
                error_messages.push('菜单"' + button.name + '" 未设置网页地址');
            } else {
                angular.forEach(button.sub_button, function (sub_button) {
                    if (!sub_button.url) {
                        error_messages.push('菜单"' + sub_button.name + '" 未设置网页地址');
                    }
                    set_to_view_button(sub_button);
                });
            }
            set_to_view_button(button);
        });
        if (error_messages.length > 0) {
            alert(error_messages.join("\n"));
            return;
        }
        var json = angular.toJson(buttons);
        var promise = $http({
            'url': 'menu',
            'method': 'POST',
            'data': json,
            'headers': {'Content-Type': 'application/json'}
        });
        promise.then(function (response) {
            var errcode = response.data.errcode;
            if (errcode != 0) {
                alert("发布失败，错误码：" + errcode + "，错误信息：" + response.data.errmsg);
            } else {
                alert("发布成功!");
            }
        }, function () {
            alert("请求数据错误，发布失败，请稍后再试！");
        });
    };
}

