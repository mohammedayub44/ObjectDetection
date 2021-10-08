import React, { Component } from 'react'
import Chart from "chart.js";
//import classes from "./LineGraph.module.css";
let myLineChart;

//--Chart Style Options--//
Chart.defaults.global.defaultFontFamily = "'PT Sans', sans-serif"
Chart.defaults.global.legend.display = false;
//--Chart Style Options--//

export default class LineGraph extends Component {
    chartRef = React.createRef();

    componentDidMount() {
        this.buildChart();
    }

    componentDidUpdate() {
        this.buildChart();
    }

    buildChart = () => {
        const myChartRef = this.chartRef.current.getContext("2d");
        const { data, ssdcnet,average, threshold, labels } = this.props;

        if (typeof myLineChart !== "undefined") myLineChart.destroy();

        myLineChart = new Chart(myChartRef, {
            type: "line",
            data: {
                //Bring in data
                labels: labels,
                datasets: [
                    {
                        label: "CSRNet Count",
                        data: data,
                        fill: false,
                        type: 'line',
                        borderColor: "#3377FF"
                    }, {
                        label: "SSDC Count",
                        data: ssdcnet,
                        type: 'line',
                        fill: false,
                        borderColor: "#FFE033"
                    },{
                        label: "Average Count",
                        data: average,
                        type: 'line',
                        fill: false,
                        borderColor: "#4CBB17"
                    },{
                        label: "Occupancy Threshold",
                        data: threshold,
                        type: 'line',
                        fill: false,
                        borderColor: "#FF0000"
                    }


                ]
            },
            options: {
                scales:{
                    yAxes: [{scaleLabel:
                    {
                        display:true, 
                        labelString: 'Count Persons'
                    }}],
                    xAxes:[{scaleLabel:
                        {
                            display:true, 
                            labelString: 'Elapsed Time'
                        }}]
                },
                showLines: true,
                animation:{
                    duration: 0
                },
            legend: {
                display: true,
                position: 'right',
                labels: {
                  fontColor: "#000080",
                }
            }}
        });

    }

    render() {

        return (
            <div >
                <canvas
                    id="myChart"
                    ref={this.chartRef}
                />
            </div>
        )
    }
}