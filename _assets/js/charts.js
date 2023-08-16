
import { GBPFormat } from "./constants";

export function spendByDirectorate(jsonElementId, chartElementId) {
    const json = JSON.parse(document.getElementById(jsonElementId).textContent);

    let groupedData = _(json)
        .groupBy("Directorate")
        .map((directorate, total) => ({
            directorate: total,
            total: _.sumBy(directorate, "Transaction Amount")
        }))
        .orderBy("total", "desc")
        .value();

    const chart = Highcharts.chart(chartElementId, {
        chart: {
            type: 'bar'
        },
        title: {
            text: 'Spend by Directorate'
        },
        xAxis: {
            categories: groupedData.map(x => x.directorate.replaceAll(/Directorate for /gi, "")),
        },
        yAxis: {
            title: {
                text: 'Spend in £'
            }
        },
        series: [{
            name: "Spend for month",
            data: groupedData.map(x => x.total)
        }],
        tooltip: {
            formatter: function () {
                return GBPFormat.format(this.y);
            }
        },
        credits: {
            enabled: false
        },
    });
}

export function spendByMonth(jsonElementId, chartElementId) {
    const jsonData = JSON.parse(document.getElementById(jsonElementId).textContent);

    const chart = Highcharts.chart(chartElementId, {
        chart: {
            type: 'line'
        },
        title: {
            text: 'Spends over £500 by month'
        },
        xAxis: {            
            type: "category"
        },
        yAxis: {
            title: {text:"Spend in £"}
        },
        series: [{
            name: "Spend for month by all directorates",
            data: jsonData.map(x => [x.displayTitle, x.total])
        }],
        tooltip: {
            useHTML: true,
            formatter: function () {                
                return `<p><strong>${this.point.name}</strong></p><p>${GBPFormat.format(this.y)}</p>`;
            }
        },
        credits: {
            enabled: false
        },
    });
}