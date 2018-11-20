var charts = {};
var seriesMap = {};
var typeText = {
    private: '专用',
    rss: '工作集',
    peak_wset: '峰值工作集'
};

var oriJsonData = jsonData;

function eachLogData(data, callback) {
    Object.keys(data).forEach(function (key) {
        var jsonItemData = data[key];
        jsonItemData.value.forEach(function (item, itemIndex) {
            callback(item, itemIndex, jsonItemData);
        })
    });
}

function formatData() {
    Object.keys(jsonData).forEach(function (key) {
        var jsonItemData = jsonData[key];
        jsonItemData.value.forEach(function (item, itemIndex) {
            Object.keys(item).forEach(function (itemKey) {

                if(itemKey === 'data') {
                    return;
                }

                if (item.data && vue.visibleEvents.indexOf(item.data.event) === -1) {
                    return;
                }

                if (vue.displayTypes.indexOf(itemKey) === -1) {
                    return;
                }

                var dataKey = key + '_' + itemKey;

                var data = seriesMap[dataKey];
                if (!data) {
                    data = {
                        name: dataKey,
                        data: [],
                        key: key,
                        itemKey: itemKey,
                        dataType: itemKey,
                        visible: vue.seriesVisibleState[dataKey] !== false,
                        pointData: [],
                        yData: []
                    };
                    seriesMap[dataKey] = data;
                }


                var time = parseInt(jsonItemData.time[itemIndex]) * 1000;
                var value = item[itemKey];

                var event = item.data;
                var point = {
                    x: time,
                    y: value,
                    color: event ? 'pink': '',
                    marker: event ? {
                        enabled: true
                    } : {
                        enabled: false
                    },
                    event: event ? [event] : null
                };

                var lastPoint = data.pointData[data.pointData.length - 1];

                // 去除间隔小于1s的点
                if (lastPoint && Math.abs(lastPoint.x - point.x) < 1000) {
                    if (event && !lastPoint.event) {
                        data.pointData.pop();
                        data.yData.pop();
                    } else if (event && lastPoint.event) {
                        lastPoint.event.push(event);
                        return;
                    } else {
                        return;
                    }
                }

                data.pointData.push(point);
                data.yData.push(value);

                if (!vue.displayTime) {
                    point = item[itemKey];
                }
                data.data.push(point);
            });
        });
    });
}

function formatMemory(value, withoutUnit) {
    //value = parseInt(value / 1024 / 1024);
    value = (value / 1024 / 1024).toFixed(1);
    return  withoutUnit ? value : value + 'Mb';
}

function getLineChartSeries() {
    return Object.keys(seriesMap).map(function (key) {
        var seriesItem = Object.assign({}, seriesMap[key]);
        seriesItem.data = vue.displayTime ? seriesItem.pointData : seriesItem.yData;
        return seriesItem;
    });
}

function drawLineChart() {

    if(charts.line) {
        charts.line.series.forEach(function(seriesItem) {
            var userOptions = seriesItem.userOptions;
            seriesItem.setData(
                [],
                false
            );
        });
        charts.line.redraw();

        charts.line.series.forEach(function(seriesItem) {
            var userOptions = seriesItem.userOptions;
            seriesItem.setData(
                vue.displayTime ? userOptions.pointData : userOptions.yData,
                false
            );
        });
        charts.line.redraw();
        return;
    }

    var series = getLineChartSeries();

    charts.line = Highcharts.chart('line-container', {
        chart: {
            type: 'spline',
        },
        title: {
            text: '内存使用趋势'
        },
        plotOptions: {
            series: {
                marker: {
                    enabled: true
                },
                turboThreshold: 10000,
                events: {
                    legendItemClick: function() {
                        var name = this.name;
                        vue.seriesVisibleState[name] = !this.visible;
                    }
                }
            },
            spline: {
                tooltip: {
                    xDateFormat: '%Y-%m-%d %H:%M:%S',
                    pointFormatter: function () {
                        var seriesName = this.series.name;
                        var seriesColor = this.series.color;
                        var value = formatMemory(this.y);
                        var event = this.event;
                        var ret = ['<span style="color:' + seriesColor + '">\u25CF</span> ' + seriesName + ': <b>' + value + '</b>'];

                        if (event) {
                            event.forEach(function(e) {
                                ret.push('<span style="color:' + seriesColor + '">\u25CF</span> event: <b>' + e.event + '</b>');
                                ret.push('<span style="color:' + seriesColor + '">\u25CF</span> msg: <b>' + e.msg + '</b>');
                            });

                        }

                        return ret.join('<br>');
                    }
                }
            }
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: '内存大小'
            },
            labels: {
                formatter: function () {
                    return formatMemory(this.value);
                }
            }
        },
        series: series
    });
}


function formatRageData() {
    var categories = Object.keys(seriesMap).filter(function(key) {
        var data = seriesMap[key];
        return data.dataType === vue.rangeDataType;
    });
    var seriesEmptyData = Array(categories.length).fill(0);
    var series = [];

    var startTime = new Date(vue.startTime).getTime();
    var endTime = new Date(vue.endTime).getTime();
    var startIndex = -1;
    var endIndex = -1;

    categories.forEach(function (key, index) {
        var data = seriesMap[key];

        if (startIndex === -1) {
            startIndex = data.pointData.findIndex(function(point) {
                return point.x >= startTime;
            });

            if (startIndex === -1) {
                startIndex = 0;
            }

            endIndex = data.pointData.findIndex(function(point) {
                return point.x >= endTime;
            });

            if (endIndex === -1) {
                endIndex = data.pointData.length - 1;
            }

        }

        var end = endIndex;
        if (end > data.pointData.length - 1) {
            end = data.pointData.length - 1;
        }

        var init = data.yData[startIndex];
        var total = data.yData[end];

        var item = {
            category: key,
            init: init,
            total: total,
            increaseSize: total - init,
            increaseRate: (total - init) / init
        };

        series.push(item);
    });

    return series;
}

function doSort(sortKey, series) {
    series.sort(function(a, b) {
        return b[sortKey] - a[sortKey];
    });
}


function drawRangeChart() {

    var seriesData = formatRageData();

    doSort(vue.sortBy, seriesData);

    var chartData = {
        init: [],
        increaseSize: [],
        categories: [],

    }
    seriesData.forEach(function(item) {
        chartData.categories.push(item.category);
        chartData.init.push(item.init);
        chartData.increaseSize.push(item.increaseSize);
    });


    if(charts.range) {
        charts.range.xAxis[0].update({
            categories: chartData.categories
        });
        charts.range.series.forEach(function(seriesItem) {
            var dataType = seriesItem.userOptions.dataType;
            seriesItem.setData(
                chartData[dataType]
            );
        });

        charts.range.redraw();
        return;
    }


    charts.range = Highcharts.chart('range-container', {
        chart: {
            type: 'column'
        },
        title: {
            text: '内存初始值与增量'
        },
        xAxis: {
            categories: chartData.categories
        },
        yAxis: {
            min: 0,
            title: {
                text: '内存大小'
            },
            labels: {
                formatter: function () {
                    return formatMemory(this.value);
                }
            },
            stackLabels: {
                enabled: true,
                formatter: function() {
                    return formatMemory(this.total, true);
                }
            }
        },
        legend: {
            align: 'right',
            x: -30,
            verticalAlign: 'top',
            y: 25,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
            borderColor: '#CCC',
            borderWidth: 1,
            shadow: false
        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.x + '</b><br/>' +
                    '<b>' + this.series.name + ':</b> ' + formatMemory(this.y) + '<br/>' +
                    '<b>总量:</b> ' + formatMemory(this.point.stackTotal);
            }
        },
        plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: {
                    enabled: false,
                    formatter: function() {
                        return formatMemory(this.y, true);
                    }
                }
            }
        },
        series: [{
            name: '增量',
            data: chartData.increaseSize,
            color: '#F56C6C',
            dataType: 'increaseSize'
        }, {
            name: '初始',
            data: chartData.init,
            color: '#17c1c5',
            dataType: 'init'
        }]
    });
}

function initPage() {
    if (charts.line) {
        charts.line.destroy();
        charts.range.destroy();
    }

    charts = {};
    seriesMap = {};

    formatData();
    drawLineChart();
    drawRangeChart();
}

function getEvents(data) {
    var map = {};
    eachLogData(data, function(item) {
        if (!item.data) {
            return;
        }

        if (!map[item.data.event]) {
            map[item.data.event] = 1
        }

    });

    return Object.keys(map);
}

function getTimeRage(data) {
    var key = Object.keys(data)[0];
    var times = data[key].time;
    return {
        start: new Date(parseInt(times[0]) * 1000).toISOString(),
        end: new Date(parseInt(times[times.length - 1]) * 1000).toISOString()
    };

}

var dataItems = Object.keys(jsonData);

var vue = new Vue({
    el: '#body',
    data: {
        displayTime: true,
        sortBy: 'total',
        removeCongestedPoint: true,
        dataKeys: dataItems,
        curDataKey: dataItems[dataItems.length - 1],
        events: [],
        visibleEvents: ['navigate_to', 'click'],
        startTime: '',
        endTime: '',
        displayTypes: ['private'],
        rangeDataType: 'private',
        seriesVisibleState: {},
        showAll: true
    },
    watch: {
        displayTime: function() {
            drawLineChart()
        },
        sortBy: function() {
            drawRangeChart();
        },
        removeCongestedPoint: function() {
            initPage();
        },
        curDataKey: function(value) {
            jsonData = oriJsonData[value].data;

            vue.events = getEvents(jsonData);
            var timeRange = getTimeRage(jsonData);
            vue.startTime = timeRange.start;
            vue.endTime = timeRange.end;

            initPage();
        },
        visibleEvents: function() {
            initPage();
        },
        startTime: function() {
            setTimeout(drawRangeChart, 20);
        },
        endTime: function() {
            setTimeout(drawRangeChart, 20);
        },
        displayTypes: function(types) {
            initPage();

            if (types.length && types.indexOf(this.rangeDataType) === -1) {
                this.rangeDataType = types[0];
            }
        },
        rangeDataType: function() {
            drawRangeChart();
        },
        showAll: function(value) {
            if (value) {
                this.seriesVisibleState = {};
            } else {
                var vm = this;
                Object.keys(seriesMap).forEach(function(key) {
                    vm.seriesVisibleState[key] = false;
                });
            }

            initPage();
        }
    }
});

jsonData = jsonData[
    vue.curDataKey
].data;

vue.events = getEvents(jsonData);
var timeRange = getTimeRage(jsonData);
vue.startTime = timeRange.start;
vue.endTime = timeRange.end;

initPage();