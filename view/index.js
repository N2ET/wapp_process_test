var charts = {};
var seriesMap = {};
var typeText = {
    private: '专用',
    rss: '工作集',
    peak_wset: '峰值工作集'
};
var defaultVisible = ['private'];

var dataItems = Object.keys(jsonData);
jsonData = jsonData[
    dataItems[dataItems.length - 1]
].data;

function formatData() {
    Object.keys(jsonData).forEach(function (key) {
        var jsonItemData = jsonData[key];
        jsonItemData.value.forEach(function (item, itemIndex) {
            Object.keys(item).forEach(function (itemKey) {
                var dataKey = key + '_' + itemKey;

                if(vue.onlyPrivate) {
                    if(itemKey !== 'private') {
                        return;
                    }
                    dataKey = key;
                }

                var data = seriesMap[dataKey];
                if (!data) {
                    data = {
                        name: dataKey,
                        data: [],
                        key: key,
                        itemKey: itemKey,
                        dataType: itemKey,
                        visible: defaultVisible.indexOf(itemKey) !== -1,
                        pointData: [],
                        yData: []
                    };
                    seriesMap[dataKey] = data;
                }

                var point = [
                    parseInt(jsonItemData.time[itemIndex]) * 1000,
                    item[itemKey]
                ];
                data.pointData.push(point);
                data.yData.push(item[itemKey]);

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
                    enabled: false
                }
            },
            spline: {
                tooltip: {
                    xDateFormat: '%Y-%m-%d %H:%M:%S',
                    pointFormatter: function () {
                        var seriesName = this.series.name;
                        var seriesColor = this.series.color;
                        var value = formatMemory(this.y);

                        return '<span style="color:' + seriesColor + '">\u25CF</span> ' + seriesName + ': <b>' + value + '</b><br/>';
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
        return ['private'].indexOf(data.dataType) !== -1;
    });
    var seriesEmptyData = Array(categories.length).fill(0);
    var series = [];
    categories.forEach(function (key, index) {
        var data = seriesMap[key];
        var init = data.yData[0];
        var total = data.yData[data.yData.length - 1];
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
    formatData();
    drawLineChart();
    drawRangeChart();
}

var vue = new Vue({
    el: '#body',
    data: {
        onlyPrivate: true,
        displayTime: true,
        sortBy: 'total'
    },
    watch: {
        displayTime: function() {
            drawLineChart()
        },
        sortBy: function() {
            drawRangeChart();
        },
        onlyPrivate: function() {
            charts.line.destroy();
            charts.range.destroy();
            charts = {};
            seriesMap = {};

            initPage();
        }
    }
});

initPage();