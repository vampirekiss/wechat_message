function EventSettingCtrl($scope, $http) {
    $scope.setting = setting;

    var key_dict = {
        'subscribe_reply_text': {
            'label': '用户关注时回复内容',
            'tip': '用户关注时自动回复的内容，留空则不发送'
        }
    };

    $scope.translate = function(key) {
        if (key_dict[key]) {
            return key_dict[key];
        }
        return key;
    };

    $scope.save_setting = function() {
        var setting = angular.copy($scope.setting);
        var json = angular.toJson(setting);
        var promise = $http({
            'url': 'event-setting',
            'method': 'POST',
            'data': json,
            'headers': {'Content-Type': 'application/json'}
        });
        promise.then(function (response) {
            var errcode = response.data.errcode;
            if (errcode != 0) {
                alert("保存失败，错误码：" + errcode + "，错误信息：" + response.data.errmsg);
            } else {
                alert("保存成功!");
            }
        }, function () {
            alert("保存失败，请稍后再试！");
        });
    }
}