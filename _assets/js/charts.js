
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